#!/usr/bin/env python3
"""
Script to verify deployment readiness.
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print("[OK] Python version - OK ({})".format(sys.version.split()[0]))
        return True
    else:
        print("[ERROR] Python version - TOO OLD ({})".format(sys.version.split()[0]))
        return False

def check_requirements():
    """Check if requirements are installed."""
    try:
        result = subprocess.run([sys.executable, "check_requirements.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode == 0:
            print("[OK] Requirements check - PASSED")
            return True
        else:
            print("[ERROR] Requirements check - FAILED")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"[ERROR] Requirements check - ERROR: {e}")
        return False

def check_database():
    """Check if database can be initialized."""
    try:
        result = subprocess.run([sys.executable, "test_database.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode == 0:
            print("[OK] Database test - PASSED")
            return True
        else:
            print("[ERROR] Database test - FAILED")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"[ERROR] Database test - ERROR: {e}")
        return False

def check_env_file():
    """Check if .env file exists."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        # Check if it contains GEMINI_API_KEY
        with open(env_path, "r") as f:
            content = f.read()
            if "GEMINI_API_KEY" in content:
                print("[OK] .env file - OK (contains GEMINI_API_KEY)")
                return True
            else:
                print("[WARNING] .env file - EXISTS but missing GEMINI_API_KEY")
                return True
    else:
        print("[WARNING] .env file - MISSING (create .env from .env.example)")
        return True  # Not critical for deployment, just a warning

def main():
    print("Deployment Verification")
    print("=" * 25)
    
    checks = [
        ("Python Version", check_python_version),
        ("Requirements", check_requirements),
        ("Database", check_database),
        (".env File", check_env_file)
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] {name} - ERROR: {e}")
            results.append(False)
    
    print("\n" + "=" * 25)
    print("Summary:")
    
    all_passed = all(results)
    
    if all_passed:
        print("[SUCCESS] All checks passed! Ready for deployment.")
        print("\nNext steps:")
        print("1. Ensure GEMINI_API_KEY is set in Render environment variables")
        print("2. Deploy using render.yaml or manual configuration")
        return 0
    else:
        print("[ERROR] Some checks failed. Please fix before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())