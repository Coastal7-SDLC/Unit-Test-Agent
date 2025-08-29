import git
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from urllib.parse import urlparse
import logging
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class GitHubService:
    """Service for handling GitHub repository operations"""
    
    def __init__(self):
        self.temp_dir = get_settings().temp_dir
        
    def clone_repository(self, repository_url: str, task_id: str) -> Path:
        """Clone a GitHub repository to a temporary directory"""
        try:
            # Create task-specific directory
            repo_dir = self.temp_dir / task_id
            repo_dir.mkdir(exist_ok=True)
            
            logger.info(f"Cloning repository: {repository_url}")
            
            # Clone the repository
            git.Repo.clone_from(
                repository_url,
                repo_dir,
                depth=1  # Shallow clone for faster download
            )
            
            logger.info(f"Repository cloned successfully to: {repo_dir}")
            return repo_dir
            
        except git.exc.GitCommandError as e:
            logger.error(f"Failed to clone repository: {e}")
            raise Exception(f"Failed to clone repository: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error cloning repository: {e}")
            raise
    
    def analyze_repository_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze the repository structure and detect languages"""
        try:
            analysis = {
                "languages": {},
                "total_files": 0,
                "file_structure": {},
                "config_files": {},
                "main_files": []
            }
            
            # Walk through all files in the repository
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(repo_path)
                    
                    # Detect language based on file extension
                    language = self._detect_language(file_path)
                    
                    if language:
                        if language not in analysis["languages"]:
                            analysis["languages"][language] = {
                                "files": [],
                                "count": 0,
                                "framework": get_settings().supported_languages[language]["framework"]
                            }
                        
                        analysis["languages"][language]["files"].append(str(relative_path))
                        analysis["languages"][language]["count"] += 1
                        analysis["total_files"] += 1
                        
                        # Check if it's a main source file (not test file)
                        if not self._is_test_file(file_path, language):
                            analysis["main_files"].append(str(relative_path))
            
            # Detect configuration files
            analysis["config_files"] = self._detect_config_files(repo_path)
            
            logger.info(f"Repository analysis completed: {analysis['total_files']} files, {len(analysis['languages'])} languages")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing repository structure: {e}")
            raise
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language based on file extension"""
        extension = file_path.suffix.lower()
        
        for language, config in get_settings().supported_languages.items():
            if extension in config["file_extensions"]:
                return language
        
        return None
    
    def _is_test_file(self, file_path: Path, language: str) -> bool:
        """Check if a file is a test file"""
        filename = file_path.name
        test_pattern = get_settings().supported_languages[language]["test_pattern"]
        
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
    
    def _detect_config_files(self, repo_path: Path) -> Dict[str, str]:
        """Detect configuration files for different languages"""
        config_files = {}
        
        for language, config in get_settings().supported_languages.items():
            for config_file in config["config_files"]:
                # Handle wildcard patterns
                if "*" in config_file:
                    import glob
                    matches = glob.glob(str(repo_path / config_file))
                    if matches:
                        config_files[language] = matches[0]
                else:
                    config_path = repo_path / config_file
                    if config_path.exists():
                        config_files[language] = str(config_path)
        
        return config_files
    
    def get_file_content(self, file_path: Path, max_size: int = 100000) -> str:
        """Get the content of a file with size limit"""
        try:
            if file_path.stat().st_size > max_size:
                logger.warning(f"File {file_path} is too large, truncating")
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read(max_size) + "\n# ... (truncated due to size)"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except UnicodeDecodeError:
            logger.warning(f"Could not decode file {file_path} as UTF-8")
            return "# Binary or non-UTF-8 file - cannot analyze"
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return f"# Error reading file: {str(e)}"
    
    def cleanup_repository(self, task_id: str):
        """Clean up the cloned repository"""
        try:
            repo_path = Path("temp") / task_id
            if repo_path.exists():
                logger.info(f"Cleaning up repository: {repo_path}")
                
                # On Windows, try to handle file access issues
                import platform
                if platform.system() == "Windows":
                    try:
                        # First try normal removal
                        shutil.rmtree(repo_path)
                    except PermissionError:
                        logger.warning(f"Permission error during cleanup, trying alternative method for {repo_path}")
                        try:
                            # Try to remove read-only attributes first
                            import subprocess
                            subprocess.run(["attrib", "-R", str(repo_path / "*"), "/S"], 
                                         capture_output=True, shell=True)
                            # Wait a moment
                            import time
                            time.sleep(1)
                            # Try removal again
                            shutil.rmtree(repo_path)
                        except Exception as e:
                            logger.error(f"Failed to cleanup repository {repo_path}: {e}")
                            # Don't raise the exception, just log it
                else:
                    # On non-Windows systems, use normal removal
                    shutil.rmtree(repo_path)
                    
                logger.info(f"Repository cleanup completed: {repo_path}")
        except Exception as e:
            logger.error(f"Error cleaning up repository: {e}")
            # Don't raise the exception, just log it
    
    def validate_repository_url(self, url: str) -> bool:
        """Validate if the URL is a valid GitHub repository"""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                'github.com' in parsed.netloc and
                len(parsed.path.strip('/').split('/')) >= 2
            )
        except Exception:
            return False
