import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import json
import shutil
from pathlib import Path

from app.models.schemas import (
    AnalysisRequest, AnalysisResponse, TaskStatusResponse, 
    AnalysisResult, ErrorResponse, HealthResponse
)
from app.core.database import AnalysisTaskManager, ModelUsageManager
from app.services.test_generator_service import TestGeneratorService
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Store active tasks (in production, use Redis or database)
active_tasks: Dict[str, Dict[str, Any]] = {}

@router.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Start repository analysis and test generation"""
    
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Create task record in MongoDB
        task_data = {
            "id": task_id,
            "repository_url": str(request.repository_url),
            "status": "pending",
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "detected_languages": None,
            "total_files": 0,
            "analyzed_files": 0,
            "generated_tests": 0,
            "coverage_percentage": 0,
            "error_message": None,
            "error_traceback": None,
            "current_step": "initializing",
            "progress_percentage": 0,
            "test_files_path": None,
            "coverage_report_path": None,
            "analysis_summary": None
        }
        
        AnalysisTaskManager.create_task(task_data)
        
        # Store task info
        active_tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "current_step": "Initializing...",
            "started_at": None,
            "completed_at": None,
            "results": None,
            "error": None
        }
        
        # Start background task
        background_tasks.add_task(
            run_analysis_task,
            task_id,
            request.repository_url,
            request.api_key
        )
        
        logger.info(f"Started analysis task {task_id} for repository {request.repository_url}")
        
        return AnalysisResponse(
            task_id=task_id,
            status="pending",
            message="Analysis started successfully",
            estimated_time=300  # 5 minutes estimate
        )
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status of an analysis task"""
    
    try:
        # Get task from MongoDB
        task = AnalysisTaskManager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get current task info
        task_info = active_tasks.get(task_id, {})
        
        return TaskStatusResponse(
            task_id=task_id,
            status=task["status"],
            current_step=task_info.get("current_step", task.get("current_step", "Unknown")),
            progress_percentage=task_info.get("progress", task.get("progress_percentage", 0)),
            created_at=task["created_at"],
            started_at=task.get("started_at"),
            completed_at=task.get("completed_at"),
            error_message=task.get("error_message")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{task_id}", response_model=AnalysisResult)
async def get_analysis_results(task_id: str):
    """Get analysis results for a completed task"""
    try:
        # Get task from MongoDB
        task = AnalysisTaskManager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Parse detected_languages from MongoDB data first
        detected_languages = []
        if task.get("detected_languages"):
            try:
                if isinstance(task["detected_languages"], str):
                    detected_languages = json.loads(task["detected_languages"])
                elif isinstance(task["detected_languages"], list):
                    detected_languages = task["detected_languages"]
                else:
                    detected_languages = []
            except Exception:
                detected_languages = []
        
        # Get task results
        task_info = active_tasks.get(task_id, {})
        results = task_info.get("results")
        
        # If results not in active_tasks (e.g., after server restart), try to reconstruct from MongoDB
        if not results:
            logger.warning(f"Results not found in active_tasks for {task_id}, attempting to reconstruct from MongoDB")
            
            # Parse analysis_summary from MongoDB data
            analysis_summary = None
            if task.get("analysis_summary"):
                try:
                    if isinstance(task["analysis_summary"], str):
                        analysis_summary = json.loads(task["analysis_summary"])
                    elif isinstance(task["analysis_summary"], dict):
                        analysis_summary = task["analysis_summary"]
                    else:
                        analysis_summary = {}
                except Exception:
                    analysis_summary = {}
            
            # Parse test generation data from MongoDB
            test_generation_data = {}
            if task.get("test_generation_data"):
                try:
                    if isinstance(task["test_generation_data"], str):
                        test_generation_data = json.loads(task["test_generation_data"])
                    elif isinstance(task["test_generation_data"], dict):
                        test_generation_data = task["test_generation_data"]
                except Exception as e:
                    logger.error(f"Error parsing test_generation_data: {e}")
                    test_generation_data = {}
            
            # Parse coverage results data from MongoDB
            coverage_results_data = {}
            if task.get("coverage_results_data"):
                try:
                    if isinstance(task["coverage_results_data"], str):
                        coverage_results_data = json.loads(task["coverage_results_data"])
                    elif isinstance(task["coverage_results_data"], dict):
                        coverage_results_data = task["coverage_results_data"]
                except Exception as e:
                    logger.error(f"Error parsing coverage_results_data: {e}")
                    coverage_results_data = {}
            
            # Try to reconstruct basic results from MongoDB data
            results = {
                "test_files": test_generation_data,
                "coverage_report": coverage_results_data,
                "summary": {
                    "total_files": task.get("total_files", 0),
                    "total_tests_generated": task.get("generated_tests", 0),
                    "overall_coverage": task.get("coverage_percentage", 0),
                    "languages_detected": detected_languages
                }
            }
            
            # If we have analysis_summary, try to extract more details
            if analysis_summary and isinstance(analysis_summary, dict):
                results["summary"].update(analysis_summary)
            
            # Try to extract test generation data from the original results if available
            if task_info.get("results"):
                original_results = task_info["results"]
                if "test_generation" in original_results:
                    results["test_files"] = original_results["test_generation"]
                if "coverage_results" in original_results:
                    results["coverage_report"] = original_results["coverage_results"]
            
            # If we still don't have test_files, try to reconstruct from stored test_generation_data
            if not results["test_files"] and task.get("test_generation_data"):
                try:
                    test_generation_data = json.loads(task["test_generation_data"])
                    results["test_files"] = test_generation_data
                    logger.info(f"Reconstructed test_files from stored data for task {task_id}")
                except Exception as e:
                    logger.warning(f"Failed to parse test_generation_data for task {task_id}: {e}")
            
            # If we still don't have coverage_report, try to reconstruct from stored coverage_results_data
            if not results["coverage_report"] and task.get("coverage_results_data"):
                try:
                    coverage_results_data = json.loads(task["coverage_results_data"])
                    results["coverage_report"] = coverage_results_data
                    logger.info(f"Reconstructed coverage_report from stored data for task {task_id}")
                except Exception as e:
                    logger.warning(f"Failed to parse coverage_results_data for task {task_id}: {e}")
            
            # Update summary with actual data from stored results
            if results["test_files"]:
                total_tests = 0
                files_generated = 0
                for lang, lang_data in results["test_files"].items():
                    if isinstance(lang_data, dict):
                        total_tests += lang_data.get("generated_tests", 0)
                        files_generated += len(lang_data.get("files", []))
                
                if results.get("summary"):
                    results["summary"]["total_tests_generated"] = total_tests
                    results["summary"]["files_generated"] = files_generated
            
            if results["coverage_report"]:
                total_coverage = 0
                total_passed = 0
                total_failed = 0
                total_tests = 0
                coverage_count = 0
                
                for lang, lang_data in results["coverage_report"].items():
                    if isinstance(lang_data, dict):
                        total_coverage += lang_data.get("coverage_percentage", 0)
                        total_passed += lang_data.get("tests_passed", 0)
                        total_failed += lang_data.get("tests_failed", 0)
                        total_tests += lang_data.get("total_tests", 0)
                        coverage_count += 1
                
                if coverage_count > 0:
                    avg_coverage = total_coverage / coverage_count
                    if results.get("summary"):
                        results["summary"]["overall_coverage"] = avg_coverage
                        results["summary"]["tests_passed"] = total_passed
                        results["summary"]["tests_failed"] = total_failed
                        results["summary"]["total_tests"] = total_tests
        
        if not results:
            # Create minimal results if nothing is available
            results = {
                "test_files": {},
                "coverage_report": {},
                "summary": {
                    "total_files": 0,
                    "total_tests_generated": 0,
                    "overall_coverage": 0,
                    "languages_detected": []
                }
            }
        
        # Create response with proper error handling
        try:
            return AnalysisResult(
                task_id=task_id,
                status=task.get("status", "unknown"),
                repository_url=task.get("repository_url", ""),
                created_at=task.get("created_at"),
                started_at=task.get("started_at"),
                completed_at=task.get("completed_at"),
                detected_languages=detected_languages,
                total_files=results.get("summary", {}).get("total_files", 0),
                analyzed_files=results.get("summary", {}).get("total_files", 0),
                generated_tests=results.get("summary", {}).get("total_tests_generated", 0),
                coverage_percentage=results.get("summary", {}).get("overall_coverage", 0),
                analysis_summary=json.dumps(results.get("summary", {})) if isinstance(results.get("summary"), dict) else str(results.get("summary", "")),
                test_files=results.get("test_files", {}),
                coverage_report=results.get("coverage_report", {}),
                test_files_download_url=f"/api/download/{task_id}/tests",
                coverage_report_download_url=f"/api/download/{task_id}/coverage"
            )
        except Exception as validation_error:
            logger.error(f"Validation error for task {task_id}: {validation_error}")
            logger.error(f"Task data: {task}")
            logger.error(f"Results data: {results}")
            # Return a minimal valid response
            return AnalysisResult(
                task_id=task_id,
                status=task.get("status", "unknown"),
                repository_url=task.get("repository_url", ""),
                created_at=task.get("created_at"),
                started_at=task.get("started_at"),
                completed_at=task.get("completed_at"),
                detected_languages=[],
                total_files=0,
                analyzed_files=0,
                generated_tests=0,
                coverage_percentage=0,
                analysis_summary="{}",
                test_files={},
                coverage_report={},
                test_files_download_url=f"/api/download/{task_id}/tests",
                coverage_report_download_url=f"/api/download/{task_id}/coverage"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis results: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/download/{task_id}/tests")
async def download_test_files(task_id: str):
    """Download generated test files as a ZIP archive"""
    
    try:
        # Get task from MongoDB
        task = AnalysisTaskManager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task["status"] != "completed":
            raise HTTPException(status_code=400, detail="Task not completed yet")
        
        # Create ZIP file with test files
        zip_path = create_test_files_archive(task_id)
        
        if not zip_path.exists():
            raise HTTPException(status_code=404, detail="Test files not found")
        
        return FileResponse(
            path=zip_path,
            filename=f"test_files_{task_id}.zip",
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading test files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{task_id}/coverage")
async def download_coverage_report(task_id: str):
    """Download coverage report files as a ZIP archive"""
    
    try:
        # Get task from MongoDB
        task = AnalysisTaskManager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task["status"] != "completed":
            raise HTTPException(status_code=400, detail="Task not completed yet")
        
        # Create ZIP file with coverage reports
        zip_path = create_coverage_archive(task_id)
        
        if not zip_path.exists():
            raise HTTPException(status_code=404, detail="Coverage report not found")
        
        return FileResponse(
            path=zip_path,
            filename=f"coverage_report_{task_id}.zip",
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading coverage report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="ai-unit-testing-agent",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

async def run_analysis_task_internal(task_id: str, repo_url: str, api_key: str) -> Dict[str, Any]:
    """Internal function to run the analysis task"""
    # Use the passed API key or fallback to environment
    settings = get_settings()
    final_api_key = api_key or settings.openrouter_api_key or "default_key"
    
    test_generator = TestGeneratorService(final_api_key)
    
    # Progress callback function
    def progress_callback(progress: int, step: str):
        active_tasks[task_id]["progress"] = progress
        active_tasks[task_id]["current_step"] = step
        
        # Update MongoDB
        AnalysisTaskManager.update_task(task_id, {
            "progress_percentage": progress,
            "current_step": step
        })
    
    # Run the analysis
    results = await test_generator.generate_tests_for_repository(
        repo_url, 
        task_id, 
        progress_callback
    )
    
    # Update task with results
    task_update_data = {
        "status": "completed",
        "completed_at": datetime.utcnow(),
        "detected_languages": json.dumps(list(results.get("repository_analysis", {}).get("languages", {}).keys())),
        "total_files": results.get("summary", {}).get("total_files", 0),
        "analyzed_files": results.get("summary", {}).get("total_files", 0),
        "generated_tests": results.get("summary", {}).get("total_tests_generated", 0),
        "coverage_percentage": results.get("summary", {}).get("overall_coverage", 0),
        "analysis_summary": json.dumps(results.get("summary", {})),
        "test_generation_data": json.dumps(results.get("test_generation", {})),
        "coverage_results_data": json.dumps(results.get("coverage_results", {}))
    }
    
    AnalysisTaskManager.update_task(task_id, task_update_data)
    
    return results

async def run_analysis_task(task_id: str, repo_url: str, api_key: str):
    """Background task to run the analysis"""
    
    try:
        # Update task status
        AnalysisTaskManager.update_task(task_id, {
            "status": "running",
            "started_at": datetime.utcnow()
        })
        
        active_tasks[task_id]["status"] = "running"
        active_tasks[task_id]["started_at"] = datetime.utcnow()
        
        # Progress callback function
        def progress_callback(progress: int, step: str):
            active_tasks[task_id]["progress"] = progress
            active_tasks[task_id]["current_step"] = step
            
            # Update MongoDB
            AnalysisTaskManager.update_task(task_id, {
                "progress_percentage": progress,
                "current_step": step
            })
        
        # Run the analysis task with timeout
        try:
            results = await asyncio.wait_for(
                run_analysis_task_internal(task_id, repo_url, api_key),
                timeout=300  # 5 minutes timeout for entire analysis
            )
        except asyncio.TimeoutError:
            logger.error(f"Analysis task {task_id} timed out after 5 minutes")
            # Update task status to failed
            AnalysisTaskManager.update_task(task_id, {
                "status": "failed",
                "completed_at": datetime.utcnow(),
                "error_message": "Analysis timed out after 5 minutes"
            })
            raise HTTPException(status_code=408, detail="Analysis timed out after 5 minutes")
        
        # Store results in active_tasks for immediate access
        active_tasks[task_id] = results
        
        # Update task status to completed
        AnalysisTaskManager.update_task(task_id, {
            "status": "completed",
            "completed_at": datetime.utcnow()
        })
        
        logger.info(f"Analysis task {task_id} completed successfully")
        
        return {"task_id": task_id, "status": "completed"}
        
    except Exception as e:
        logger.error(f"Error in analysis task {task_id}: {e}")
        # Update task status to failed
        AnalysisTaskManager.update_task(task_id, {
            "status": "failed",
            "completed_at": datetime.utcnow(),
            "error_message": str(e)
        })
        raise

def create_test_files_archive(task_id: str) -> Path:
    """Create a ZIP archive of test files"""
    import zipfile
    
    try:
        # Create downloads directory
        downloads_dir = get_settings().downloads_dir
        downloads_dir.mkdir(exist_ok=True)
        
        # Create ZIP file
        zip_path = downloads_dir / f"test_files_{task_id}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add test files from temp directory
            temp_dir = get_settings().temp_dir / task_id
            if temp_dir.exists():
                for file_path in temp_dir.rglob("*.py"):
                    if "test" in file_path.name.lower():
                        zipf.write(file_path, file_path.relative_to(temp_dir))
                
                for file_path in temp_dir.rglob("*.js"):
                    if "test" in file_path.name.lower():
                        zipf.write(file_path, file_path.relative_to(temp_dir))
                
                for file_path in temp_dir.rglob("*.java"):
                    if "Test" in file_path.name:
                        zipf.write(file_path, file_path.relative_to(temp_dir))
        
        return zip_path
        
    except Exception as e:
        logger.error(f"Error creating test files archive: {e}")
        raise

def create_coverage_archive(task_id: str) -> Path:
    """Create a ZIP archive of coverage reports"""
    import zipfile
    
    try:
        # Create downloads directory
        downloads_dir = get_settings().downloads_dir
        downloads_dir.mkdir(exist_ok=True)
        
        # Create ZIP file
        zip_path = downloads_dir / f"coverage_report_{task_id}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add coverage reports from temp directory
            temp_dir = get_settings().temp_dir / task_id
            if temp_dir.exists():
                # Add HTML coverage reports
                for coverage_dir in temp_dir.rglob("htmlcov"):
                    for file_path in coverage_dir.rglob("*"):
                        if file_path.is_file():
                            zipf.write(file_path, file_path.relative_to(temp_dir))
                
                # Add other coverage files
                for file_path in temp_dir.rglob("coverage*"):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(temp_dir))
        
        return zip_path
        
    except Exception as e:
        logger.error(f"Error creating coverage archive: {e}")
        raise
