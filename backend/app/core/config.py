from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "AI Unit Testing Agent"
    
    # OpenRouter Configuration
    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    primary_model: str = Field(default="deepseek/deepseek-r1:free", alias="PRIMARY_MODEL")
    secondary_model: str = Field(default="deepseek/deepseek-v3:free", alias="SECONDARY_MODEL")
    backup_model: str = Field(default="qwen/qwen-2.5-coder-32b-instruct:free", alias="BACKUP_MODEL")
    
    # GitHub Configuration
    github_token: Optional[str] = Field(default=None, alias="GITHUB_TOKEN")
    
    # Application Settings
    max_repository_size: str = Field(default="100MB", alias="MAX_REPOSITORY_SIZE")
    max_analysis_time: int = Field(default=3600, alias="MAX_ANALYSIS_TIME")  # seconds
    max_concurrent_analyses: int = Field(default=3, alias="MAX_CONCURRENT_ANALYSES")
    
    # MongoDB Configuration
    mongodb_url: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URL")
    mongodb_database: str = Field(default="ai_testing_agent", alias="MONGODB_DATABASE")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", alias="LOG_FILE")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-this", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Rate Limiting
    max_requests_per_minute: int = Field(default=20, alias="MAX_REQUESTS_PER_MINUTE")
    max_requests_per_day: int = Field(default=200, alias="MAX_REQUESTS_PER_DAY")
    
    # File Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    downloads_dir: Path = base_dir / "downloads"
    temp_dir: Path = base_dir / "temp"
    logs_dir: Path = base_dir / "logs"
    
    # Model Configuration
    max_tokens_per_request: int = Field(default=8000, alias="MAX_TOKENS_PER_REQUEST")
    max_input_tokens: int = Field(default=128000, alias="MAX_INPUT_TOKENS")
    temperature: float = Field(default=0.1, alias="TEMPERATURE")
    
    # Supported Languages and Frameworks
    supported_languages: dict = {
        "python": {
            "framework": "pytest",
            "coverage_tool": "pytest-cov",
            "file_extensions": [".py"],
            "test_pattern": "test_*.py",
            "config_files": ["pytest.ini", "pyproject.toml", "setup.cfg"]
        },
        "javascript": {
            "framework": "jest",
            "coverage_tool": "jest",
            "file_extensions": [".js", ".ts", ".jsx", ".tsx"],
            "test_pattern": "*.test.js",
            "config_files": ["package.json", "jest.config.js"]
        },
        "java": {
            "framework": "junit5",
            "coverage_tool": "jacoco",
            "file_extensions": [".java"],
            "test_pattern": "*Test.java",
            "config_files": ["pom.xml", "build.gradle"]
        },
        "csharp": {
            "framework": "xunit",
            "coverage_tool": "coverlet",
            "file_extensions": [".cs"],
            "test_pattern": "*Tests.cs",
            "config_files": ["*.csproj", "*.sln"]
        },
        "go": {
            "framework": "go_testing",
            "coverage_tool": "go",
            "file_extensions": [".go"],
            "test_pattern": "*_test.go",
            "config_files": ["go.mod", "go.sum"]
        },
        "ruby": {
            "framework": "rspec",
            "coverage_tool": "simplecov",
            "file_extensions": [".rb"],
            "test_pattern": "*_spec.rb",
            "config_files": ["Gemfile", "Rakefile"]
        },
        "php": {
            "framework": "phpunit",
            "coverage_tool": "phpunit",
            "file_extensions": [".php"],
            "test_pattern": "*Test.php",
            "config_files": ["composer.json", "phpunit.xml"]
        }
    }
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Allow extra fields during migration
    }

# Create settings instance (lazy initialization)
_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        # Ensure directories exist
        _settings.downloads_dir.mkdir(exist_ok=True)
        _settings.temp_dir.mkdir(exist_ok=True)
        _settings.logs_dir.mkdir(exist_ok=True)
    return _settings

# For backward compatibility - will be initialized when first accessed
settings = None

def _get_settings():
    global settings
    if settings is None:
        settings = get_settings()
    return settings
