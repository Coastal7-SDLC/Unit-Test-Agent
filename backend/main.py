import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.routes import router
from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.core.logging import setup_logging
import shutil
from pathlib import Path
import signal
import sys
import subprocess

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nReceived shutdown signal, cleaning up...")
    try:
        # Cleanup will be handled by the shutdown event
        sys.exit(0)
    except Exception as e:
        print(f"Error during shutdown: {e}")
        sys.exit(1)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def cleanup_stale_temp_dirs():
    """Clean up stale temporary directories on startup"""
    try:
        settings = get_settings()
        temp_dir = settings.temp_dir
        
        if temp_dir.exists():
            # Remove directories older than 1 hour
            import time
            current_time = time.time()
            one_hour = 3600
            
            for item in temp_dir.iterdir():
                if item.is_dir():
                    try:
                        # Check if directory is older than 1 hour
                        if current_time - item.stat().st_mtime > one_hour:
                            shutil.rmtree(item, ignore_errors=True)
                            print(f"Cleaned up stale temp directory: {item}")
                    except Exception as e:
                        print(f"Warning: Could not clean up {item}: {e}")
    except Exception as e:
        print(f"Warning: Error during temp directory cleanup: {e}")

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="AI Unit Testing Agent",
    description="An intelligent AI-powered agent for automated unit testing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Mount static files for serving generated test files
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

@app.on_event("startup")
async def startup_event():
    """Initialize database and other startup tasks"""
    cleanup_stale_temp_dirs()
    await init_db()
    print("AI Unit Testing Agent started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        print("Shutting down gracefully...")
        await close_db()
        print("AI Unit Testing Agent shutting down...")
    except Exception as e:
        print(f"Error during shutdown: {e}")
        # Continue with shutdown even if cleanup fails

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Unit Testing Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-unit-testing-agent"}

if __name__ == "__main__":
    import uvicorn
    import os
    import sys
    from pathlib import Path
    
    # Clean up stale temp directories on startup
    cleanup_stale_temp_dirs()
    
    # Try to install dependencies
    try:
        subprocess.run([sys.executable, "install_deps.py"], check=True, cwd=Path(__file__).parent)
    except FileNotFoundError:
        print("install_deps.py not found, skipping dependency installation")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
    
    print("AI Unit Testing Agent started successfully!")
    
    # Completely disable WatchFiles by setting environment variables
    os.environ["WATCHFILES_FORCE_POLLING"] = "false"
    os.environ["WATCHFILES_IGNORE_PATTERNS"] = "*"
    os.environ["WATCHFILES_IGNORE_DIRS"] = "*"
    os.environ["WATCHFILES_IGNORE_FILES"] = "*"
    os.environ["WATCHFILES_IGNORE_REGEX"] = ".*"
    
    # Run with completely disabled reload - no WatchFiles at all
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,  # Completely disable reload
        reload_dirs=None,
        reload_includes=None,
        reload_excludes=None,
        access_log=False,
        log_level="info"
    )
