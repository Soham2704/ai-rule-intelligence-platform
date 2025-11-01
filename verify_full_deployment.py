#!/usr/bin/env python3
"""
Verification script for the full AI Rule Intelligence Platform deployment.
This script checks that all required components can be imported and initialized.
"""

import sys
import os

def check_python_version():
    """Check that we're using Python 3.12"""
    print("Checking Python version...")
    if sys.version_info < (3, 12):
        print(f"WARNING: Python 3.12 recommended, but found {sys.version}")
        return False
    else:
        print(f"✓ Python version {sys.version} is compatible")
        return True

def check_required_files():
    """Check that all required files exist"""
    print("\nChecking required files...")
    required_files = [
        "requirements.txt",
        "render.yaml",
        "Dockerfile",
        "start_server.py",
        "main.py",
        "runtime.txt",
        ".python-version",
        "Procfile"
    ]
    
    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} is missing")
            all_good = False
    
    return all_good

def check_imports():
    """Check that all major modules can be imported"""
    print("\nChecking imports...")
    modules_to_check = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "dotenv",
        "sqlalchemy",
        "requests",
        "numpy"
    ]
    
    all_good = True
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"✓ {module} can be imported")
        except ImportError as e:
            print(f"✗ {module} import failed: {e}")
            all_good = False
    
    # Check optional imports
    optional_modules = [
        "langchain",
        "google.generativeai",
        "stable_baselines3",
        "torch",
        "pandas",
        "sklearn",
        "streamlit",
        "plotly",
        "PIL",
        "pytesseract",
        "fitz",  # pymupdf
        "stl"
    ]
    
    print("\nChecking optional imports...")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✓ {module} (optional) can be imported")
        except ImportError:
            print(f"⚠ {module} (optional) not available - this is OK for minimal functionality")
    
    return all_good

def check_dependencies():
    """Check that key dependencies are at the right versions"""
    print("\nChecking key dependencies...")
    try:
        import numpy
        print(f"✓ NumPy version: {numpy.__version__}")
        
        import fastapi
        print(f"✓ FastAPI version: {fastapi.__version__}")
        
        # Check that numpy version is compatible with Python 3.12
        if numpy.__version__ >= "1.26.0":
            print("✓ NumPy version is compatible with Python 3.12")
            return True
        else:
            print("⚠ NumPy version may not be fully compatible with Python 3.12")
            return False
    except Exception as e:
        print(f"✗ Dependency check failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=== AI Rule Intelligence Platform - Full Deployment Verification ===")
    
    checks = [
        check_python_version,
        check_required_files,
        check_imports,
        check_dependencies
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"✗ Check {check.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n=== Summary ===")
    if all(results):
        print("✓ All checks passed! Your full deployment is ready.")
        print("\nNext steps:")
        print("1. Deploy to Render using the render.yaml configuration")
        print("2. Or build and run with Docker: docker build -t ai-rule-platform . && docker run -p 8000:8000 ai-rule-platform")
        print("3. Or run locally: python start_server.py")
        return 0
    else:
        print("✗ Some checks failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())