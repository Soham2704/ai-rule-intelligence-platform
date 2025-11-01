#!/usr/bin/env python3
"""
Script to check if all required packages are installed correctly.
"""

import sys
import importlib

def check_package(package_name, import_name=None):
    """Check if a package is installed and can be imported."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"[OK] {package_name} - OK")
        return True
    except ImportError as e:
        print(f"[ERROR] {package_name} - MISSING ({e})")
        return False

def main():
    print("Checking required packages...")
    print("=" * 50)
    
    # List of required packages and their import names
    packages = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("stable-baselines3", "stable_baselines3"),
        ("langchain", "langchain"),
        ("pymupdf", "fitz"),
        ("requests", "requests"),
        ("openai", "openai"),
        ("python-dotenv", "dotenv"),
        ("google-generativeai", "google.generativeai"),
        ("langchain-google-genai", "langchain_google_genai"),
        ("langchain-community", "langchain_community"),
        ("faiss-cpu", "faiss"),
        ("sentence-transformers", "sentence_transformers"),
        ("torch", "torch"),
        ("gymnasium", "gymnasium"),
        ("pytesseract", "pytesseract"),
        ("pillow", "PIL"),
        ("numpy-stl", "stl"),
        ("pytest", "pytest"),
        ("streamlit", "streamlit"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("plotly", "plotly")
    ]
    
    missing_packages = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    print("=" * 50)
    
    if missing_packages:
        print(f"\n[WARNING] Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return 1
    else:
        print("\n[SUCCESS] All packages are installed correctly!")
        return 0

if __name__ == "__main__":
    sys.exit(main())