#!/usr/bin/env python3
"""
AI Unit Testing Agent - Startup Script
This script starts both the backend and frontend servers.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        client.server_info()
        client.close()
        return True
    except Exception:
        return False

def run_backend():
    """Run the FastAPI backend server"""
    print("Starting backend server...")
    os.chdir("backend")
    subprocess.run([sys.executable, "main.py"])

def run_frontend():
    """Run the React frontend server"""
    print("Starting frontend server...")
    os.chdir("frontend")
    subprocess.run(["npm", "start"])

def main():
    """Main startup function"""
    print("AI Unit Testing Agent - Starting up...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("Error: Please run this script from the project root directory")
        print("   Make sure both 'backend' and 'frontend' directories exist")
        sys.exit(1)
    
    # Check MongoDB connection
    print("Checking MongoDB connection...")
    if not check_mongodb():
        print("Error: MongoDB is not running or not accessible")
        print("   Please start MongoDB service:")
        print("   - Windows: Start MongoDB service or run 'mongod'")
        print("   - macOS: brew services start mongodb-community")
        print("   - Linux: sudo systemctl start mongod")
        print("   - Or use Docker: docker run -d -p 27017:27017 mongo:latest")
        sys.exit(1)
    else:
        print("MongoDB connection successful")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("Warning: .env file not found. Creating from env.example...")
        if Path("env.example").exists():
            import shutil
            shutil.copy("env.example", ".env")
            print(".env file created from env.example")
            print("Warning: Please edit .env with your actual OpenRouter API key")
            print("   Then restart the application")
            sys.exit(1)
        else:
            print("Error: env.example file not found")
            sys.exit(1)
    
    # Check if node_modules exists in frontend
    if not Path("frontend/node_modules").exists():
        print("Installing frontend dependencies...")
        os.chdir("frontend")
        subprocess.run(["npm", "install"])
        os.chdir("..")
    
    # Check if backend dependencies are installed
    if not Path("backend/venv").exists() and not Path("venv").exists():
        print("Installing backend dependencies...")
        os.chdir("backend")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        os.chdir("..")
    
    # Check if pytest is available
    print("Checking pytest availability...")
    os.chdir("backend")
    try:
        result = subprocess.run([sys.executable, "install_deps.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ pytest and dependencies are ready")
        else:
            print("⚠️  Warning: Some dependencies may not be available")
            print(result.stderr)
    except Exception as e:
        print(f"⚠️  Warning: Could not check dependencies: {e}")
    os.chdir("..")
    
    print("All dependencies and configurations are ready!")
    print("Starting servers...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()
