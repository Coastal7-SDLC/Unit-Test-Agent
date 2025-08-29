#!/usr/bin/env python3
"""
Test script to verify the AI Unit Testing Agent setup
"""

import os
import sys
import subprocess
from pathlib import Path

def test_python_dependencies():
    """Test if Python dependencies can be imported"""
    print("🐍 Testing Python dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import pydantic
        import git
        import httpx
        print("✅ Python dependencies OK")
        return True
    except ImportError as e:
        print(f"❌ Python dependency error: {e}")
        return False

def test_node_dependencies():
    """Test if Node.js dependencies are installed"""
    print("📦 Testing Node.js dependencies...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("❌ node_modules not found. Run 'npm install' in frontend directory")
        return False
    
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found")
        return False
    
    print("✅ Node.js dependencies OK")
    return True

def test_environment():
    """Test environment configuration"""
    print("⚙️ Testing environment configuration...")
    
    env_file = Path("env.example")
    if not env_file.exists():
        print("❌ env.example file not found")
        return False
    
    print("✅ Environment configuration OK")
    return True

def test_directory_structure():
    """Test if required directories exist"""
    print("📁 Testing directory structure...")
    
    required_dirs = [
        "backend",
        "backend/app",
        "backend/app/api",
        "backend/app/core",
        "backend/app/models",
        "backend/app/services",
        "frontend",
        "frontend/src",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/services",
        "docs"
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Directory not found: {dir_path}")
            return False
    
    print("✅ Directory structure OK")
    return True

def test_backend_files():
    """Test if backend files exist"""
    print("🔧 Testing backend files...")
    
    required_files = [
        "backend/main.py",
        "backend/app/core/config.py",
        "backend/app/core/database.py",
        "backend/app/core/logging.py",
        "backend/app/models/schemas.py",
        "backend/app/services/github_service.py",
        "backend/app/services/ai_service.py",
        "backend/app/services/test_generator_service.py",
        "backend/app/services/test_runner_service.py",
        "backend/app/api/routes.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return False
    
    print("✅ Backend files OK")
    return True

def test_frontend_files():
    """Test if frontend files exist"""
    print("🎨 Testing frontend files...")
    
    required_files = [
        "frontend/package.json",
        "frontend/src/App.js",
        "frontend/src/index.js",
        "frontend/src/index.css",
        "frontend/src/components/Header.js",
        "frontend/src/components/AnalysisForm.js",
        "frontend/src/components/ProgressTracker.js",
        "frontend/src/pages/HomePage.js",
        "frontend/src/pages/AnalysisPage.js",
        "frontend/src/pages/ResultsPage.js",
        "frontend/src/services/api.js"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return False
    
    print("✅ Frontend files OK")
    return True

def test_requirements():
    """Test if requirements.txt exists"""
    print("📋 Testing requirements.txt...")
    
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt OK")
    return True

def main():
    """Run all tests"""
    print("🤖 AI Unit Testing Agent - Setup Verification")
    print("=" * 50)
    
    tests = [
        test_directory_structure,
        test_backend_files,
        test_frontend_files,
        test_requirements,
        test_environment,
        test_python_dependencies,
        test_node_dependencies
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is complete.")
        print("\n🚀 To start the application:")
        print("   python start.py")
        print("\n📖 For more information, see docs/SETUP.md")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n📖 For setup instructions, see docs/SETUP.md")
        sys.exit(1)

if __name__ == "__main__":
    main()
