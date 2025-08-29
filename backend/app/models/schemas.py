from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisRequest(BaseModel):
    """Request model for starting repository analysis"""
    repository_url: HttpUrl
    api_key: Optional[str] = None
    include_dependencies: bool = True
    generate_mocks: bool = True
    target_coverage: int = 80
    max_files: Optional[int] = None
    
    @validator('target_coverage')
    def validate_coverage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Coverage must be between 0 and 100')
        return v

class AnalysisResponse(BaseModel):
    """Response model for analysis task creation"""
    task_id: str
    status: TaskStatus
    message: str
    estimated_time: Optional[int] = None

class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str
    status: TaskStatus
    current_step: str
    progress_percentage: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class AnalysisResult(BaseModel):
    """Response model for analysis results"""
    task_id: str
    status: TaskStatus
    repository_url: str
    
    # Analysis summary
    detected_languages: List[str]
    total_files: int
    analyzed_files: int
    generated_tests: int
    coverage_percentage: float
    
    # File information
    test_files: Dict[str, Any]
    coverage_report: Optional[Dict[str, Any]] = None
    analysis_summary: Optional[str] = None
    
    # Timing
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Download links
    test_files_download_url: Optional[str] = None
    coverage_report_download_url: Optional[str] = None

class LanguageInfo(BaseModel):
    """Information about detected programming language"""
    language: str
    framework: str
    file_count: int
    test_files_generated: int
    coverage_percentage: float

class TestFileInfo(BaseModel):
    """Information about generated test file"""
    file_path: str
    language: str
    framework: str
    test_count: int
    coverage_percentage: float
    file_size: int

class CoverageReport(BaseModel):
    """Coverage report information"""
    overall_coverage: float
    language_breakdown: Dict[str, float]
    file_breakdown: List[Dict[str, Any]]
    uncovered_lines: List[Dict[str, Any]]

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    timestamp: datetime
    version: str
