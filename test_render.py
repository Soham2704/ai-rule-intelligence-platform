#!/usr/bin/env python3
"""
Simple test to check what Python version Render is using
"""

import sys
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Environment variables:")
for key, value in os.environ.items():
    if 'PYTHON' in key or 'RENDER' in key:
        print(f"  {key}: {value}")

print("\nTrying to import a simple package...")
try:
    import fastapi
    print("FastAPI imported successfully")
except Exception as e:
    print(f"Error importing FastAPI: {e}")

print("\nTest completed")