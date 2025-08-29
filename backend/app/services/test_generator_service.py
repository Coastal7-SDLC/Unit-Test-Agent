import asyncio
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.github_service import GitHubService
from app.services.ai_service import AIService
from app.services.test_runner_service import TestRunnerService
from app.core.database import ModelUsageManager

logger = get_logger(__name__)

class TestGeneratorService:
    """Main service for orchestrating the test generation process"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.github_service = GitHubService()
        self.ai_service = AIService(api_key)
        self.test_runner = TestRunnerService()
        
    async def generate_tests_for_repository(
        self, 
        repository_url: str, 
        task_id: str,
        progress_callback=None
    ) -> Dict[str, Any]:
        """Main method to generate tests for an entire repository"""
        
        repo_path = None
        try:
            # Step 1: Clone repository
            if progress_callback:
                progress_callback(10, "Cloning repository...")
            
            repo_path = await self._clone_repository(repository_url, task_id)
            
            # Step 2: Analyze repository structure
            if progress_callback:
                progress_callback(20, "Analyzing repository structure...")
            
            analysis = self.github_service.analyze_repository_structure(repo_path)
            
            # Step 3: Generate tests for each language
            if progress_callback:
                progress_callback(30, "Generating unit tests...")
            
            test_results = await self._generate_tests_for_languages(
                repo_path, analysis, task_id, progress_callback
            )
            
            # Step 4: Run tests and generate coverage
            if progress_callback:
                progress_callback(80, "Running tests and generating coverage...")
            
            coverage_results = await self._run_tests_and_coverage(
                repo_path, test_results, progress_callback
            )
            
            # Step 5: Prepare final results
            if progress_callback:
                progress_callback(90, "Preparing final results...")
            
            final_results = self._prepare_final_results(
                analysis, test_results, coverage_results, task_id
            )
            
            if progress_callback:
                progress_callback(100, "Analysis completed!")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error in test generation process: {e}")
            raise
        finally:
            # Cleanup - DISABLED for manual cleanup
            # if repo_path and repo_path.exists():
            #     self.github_service.cleanup_repository(task_id)
            pass
    
    async def _clone_repository(self, repository_url: str, task_id: str) -> Path:
        """Clone the repository"""
        return self.github_service.clone_repository(repository_url, task_id)
    
    async def _generate_tests_for_languages(
        self, 
        repo_path: Path, 
        analysis: Dict[str, Any],
        task_id: str,
        progress_callback=None
    ) -> Dict[str, Any]:
        """Generate tests for each detected language"""
        
        test_results = {}
        total_languages = len(analysis["languages"])
        current_language = 0
        
        for language, lang_info in analysis["languages"].items():
            try:
                current_language += 1
                progress = 30 + (current_language / total_languages) * 40
                
                if progress_callback:
                    progress_callback(
                        int(progress), 
                        f"Generating tests for {language} ({current_language}/{total_languages})..."
                    )
                
                test_results[language] = await self._generate_tests_for_language(
                    repo_path, language, lang_info, task_id
                )
                
            except Exception as e:
                logger.error(f"Error generating tests for {language}: {e}")
                test_results[language] = {
                    "error": str(e),
                    "files": [],
                    "success": False
                }
        
        return test_results
    
    async def _generate_tests_for_language(
        self, 
        repo_path: Path, 
        language: str, 
        lang_info: Dict[str, Any],
        task_id: str
    ) -> Dict[str, Any]:
        """Generate tests for a specific language"""
        
        framework = lang_info["framework"]
        source_files = lang_info["files"]
        
        test_files = []
        generated_tests = 0
        
        for file_path in source_files:
            try:
                logger.info(f"Processing file: {file_path}")
                
                # Skip test files
                if self._is_test_file(file_path, language):
                    logger.info(f"Skipping test file: {file_path}")
                    continue
                
                # Generate test code using AI
                test_code = await self._generate_test_code(file_path, language, framework, repo_path)
                
                if test_code:
                    # Create test file
                    test_file_path = self._create_test_file(repo_path, file_path, test_code, language, framework)
                    
                    # Count tests in the generated code
                    test_count = self._count_tests_in_code(test_code, language)
                    generated_tests += test_count
                    
                    # Track model usage
                    self._track_model_usage(task_id, language, str(file_path))
                    
                    # Add to test files list
                    test_files.append({
                        "source_file": str(file_path),
                        "test_file": str(test_file_path.relative_to(repo_path)),
                        "test_count": test_count,
                        "coverage_estimate": 0  # Will be updated after running tests
                    })
                    
                    logger.info(f"Generated {test_count} tests for {file_path}")
                else:
                    logger.warning(f"Failed to generate tests for {file_path}")
                    
            except Exception as e:
                logger.error(f"Error generating tests for {file_path}: {e}")
                continue
        
        return {
            "framework": framework,
            "files": test_files,
            "generated_tests": generated_tests,
            "success": len(test_files) > 0
        }
    
    def _track_model_usage(self, task_id: str, language: str, file_path: str):
        """Track AI model usage in MongoDB"""
        try:
            usage_data = {
                "task_id": task_id,
                "model_name": "ai_service",
                "language": language,
                "file_path": file_path,
                "tokens_used": 0,  # Will be updated when we have token counting
                "requests_made": 1,
                "cost": 0,  # Will be updated when we have cost tracking
                "created_at": datetime.utcnow()
            }
            
            ModelUsageManager.create_usage_record(usage_data)
            
        except Exception as e:
            logger.error(f"Error tracking model usage: {e}")
    
    def _is_test_file(self, file_path: str, language: str) -> bool:
        """Check if a file is a test file"""
        filename = Path(file_path).name
        
        if language == "python":
            return filename.startswith("test_") or filename.endswith("_test.py")
        elif language == "javascript":
            return "test" in filename.lower() or filename.endswith(".test.js") or filename.endswith(".spec.js")
        elif language == "java":
            return filename.endswith("Test.java")
        elif language == "csharp":
            return filename.endswith("Tests.cs")
        elif language == "go":
            return filename.endswith("_test.go")
        elif language == "ruby":
            return filename.endswith("_spec.rb")
        elif language == "php":
            return filename.endswith("Test.php")
        
        return False
    
    async def _generate_test_code(self, file_path: str, language: str, framework: str, repo_path: Path) -> str:
        """Generate test code for a specific file"""
        try:
            full_path = repo_path / file_path
            if not full_path.exists():
                logger.warning(f"File not found: {full_path}")
                return ""
            
            # Read source code
            logger.info(f"Reading source code from: {file_path}")
            source_code = self.github_service.get_file_content(full_path)
            
            # Analyze code structure
            logger.info(f"Analyzing code structure for: {file_path}")
            analysis = await self.ai_service.analyze_code_structure(
                source_code, language, file_path
            )
            
            # Generate tests
            logger.info(f"Generating tests for: {file_path}")
            test_code = await self.ai_service.generate_unit_tests(
                source_code, language, framework, file_path, analysis.get("dependencies", [])
            )
            
            return test_code
            
        except Exception as e:
            logger.error(f"Error generating test code for {file_path}: {e}")
            return ""
    
    def _count_tests_in_code(self, test_code: str, language: str) -> int:
        """Count the number of tests in the generated code"""
        return self._count_test_functions(test_code, language)
    
    def _create_test_file(
        self, 
        repo_path: Path, 
        source_file: str, 
        test_code: str, 
        language: str, 
        framework: str
    ) -> Path:
        """Create a test file in the appropriate location"""
        
        source_path = Path(source_file)
        
        if language == "python":
            # Create tests directory if it doesn't exist
            test_dir = repo_path / "tests"
            test_dir.mkdir(exist_ok=True)
            
            # Create test file name
            test_filename = f"test_{source_path.stem}.py"
            test_file_path = test_dir / test_filename
            
        elif language == "javascript":
            # Place test file next to source file
            test_filename = f"{source_path.stem}.test{source_path.suffix}"
            test_file_path = repo_path / source_path.parent / test_filename
            
        elif language == "java":
            # Create test directory structure
            test_dir = repo_path / source_path.parent / "test"
            test_dir.mkdir(exist_ok=True)
            
            test_filename = f"{source_path.stem}Test.java"
            test_file_path = test_dir / test_filename
            
        elif language == "csharp":
            # Create test directory
            test_dir = repo_path / source_path.parent / "Tests"
            test_dir.mkdir(exist_ok=True)
            
            test_filename = f"{source_path.stem}Tests.cs"
            test_file_path = test_dir / test_filename
            
        elif language == "go":
            # Place test file next to source file
            test_filename = f"{source_path.stem}_test.go"
            test_file_path = repo_path / source_path.parent / test_filename
            
        else:
            # Default: place in tests directory
            test_dir = repo_path / "tests"
            test_dir.mkdir(exist_ok=True)
            test_file_path = test_dir / f"test_{source_path.name}"
        
        # Write test code to file
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        return test_file_path
    
    def _count_test_functions(self, test_code: str, language: str) -> int:
        """Count the number of test functions in the generated code"""
        count = 0
        
        if language == "python":
            # Count functions starting with test_
            lines = test_code.split('\n')
            for line in lines:
                if line.strip().startswith('def test_'):
                    count += 1
                    
        elif language == "javascript":
            # Count test/it/describe blocks
            lines = test_code.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['test(', 'it(', 'describe(']):
                    count += 1
                    
        elif language == "java":
            # Count @Test annotations
            lines = test_code.split('\n')
            for line in lines:
                if '@Test' in line:
                    count += 1
                    
        elif language == "csharp":
            # Count [Test] attributes
            lines = test_code.split('\n')
            for line in lines:
                if '[Test]' in line:
                    count += 1
        
        return count
    
    async def _run_tests_and_coverage(
        self, 
        repo_path: Path, 
        test_results: Dict[str, Any],
        progress_callback=None
    ) -> Dict[str, Any]:
        """Run tests and generate coverage reports"""
        
        coverage_results = {}
        
        for language, lang_result in test_results.items():
            if not lang_result.get("success", False):
                continue
                
            try:
                coverage = await self.test_runner.run_tests_with_coverage(
                    repo_path, language, lang_result["framework"]
                )
                coverage_results[language] = coverage
                
            except Exception as e:
                logger.error(f"Error running tests for {language}: {e}")
                coverage_results[language] = {
                    "error": str(e),
                    "coverage": 0,
                    "tests_passed": 0,
                    "tests_failed": 0
                }
        
        return coverage_results
    
    def _prepare_final_results(
        self, 
        analysis: Dict[str, Any], 
        test_results: Dict[str, Any], 
        coverage_results: Dict[str, Any],
        task_id: str
    ) -> Dict[str, Any]:
        """Prepare the final results summary"""
        
        total_files = analysis["total_files"]
        total_tests_generated = sum(
            lang_result.get("generated_tests", 0) 
            for lang_result in test_results.values()
        )

        # Aggregate executed test metrics from coverage_results
        executed_passed = 0
        executed_failed = 0
        executed_total = 0
        coverage_values: list[float] = []
        for lang_result in coverage_results.values():
            if isinstance(lang_result, dict) and "error" not in lang_result:
                executed_passed += int(lang_result.get("tests_passed", 0))
                executed_failed += int(lang_result.get("tests_failed", 0))
                # Prefer explicit total_tests; otherwise derive
                lang_total = int(lang_result.get("total_tests", 0))
                if lang_total == 0:
                    lang_total = int(lang_result.get("tests_total", 0))
                if lang_total == 0:
                    lang_total = int(lang_result.get("tests_passed", 0)) + int(lang_result.get("tests_failed", 0))
                executed_total += lang_total

                # Coverage key normalization
                if "coverage_percentage" in lang_result:
                    coverage_values.append(float(lang_result.get("coverage_percentage", 0)))
                elif "coverage" in lang_result:
                    coverage_values.append(float(lang_result.get("coverage", 0)))

        overall_coverage = round(sum(coverage_values) / len(coverage_values), 2) if coverage_values else 0.0
        
        return {
            "task_id": task_id,
            "repository_analysis": analysis,
            "test_generation": test_results,
            "coverage_results": coverage_results,
            "summary": {
                "total_files": total_files,
                "total_tests_generated": total_tests_generated,
                "total_tests_executed": executed_total,
                "tests_passed": executed_passed,
                "tests_failed": executed_failed,
                "overall_coverage": overall_coverage,
                "languages_detected": list(analysis["languages"].keys()),
                "successful_languages": [
                    lang for lang, result in test_results.items() 
                    if result.get("success", False)
                ]
            }
        }
