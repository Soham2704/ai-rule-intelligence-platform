#!/usr/bin/env python3
"""
Comprehensive startup script for the AI Rule Intelligence Platform.
This script ensures all components are initialized before starting the FastAPI server.
"""

import os
import sys

def main():
    print("Starting AI Rule Intelligence Platform...")
    
    # Ensure the database is created before starting the server
    print("Initializing database...")
    try:
        from database_setup import create_database
        create_database()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        # Continue anyway as this might be a deployment issue
    
    # Try to import and initialize other components
    print("Initializing components...")
    try:
        # Import main module to trigger startup events
        import main
        print("Main module loaded successfully.")
    except Exception as e:
        print(f"Warning: Main module initialization failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Start the FastAPI server
    print("Starting FastAPI server...")
    try:
        import uvicorn
        port = int(os.environ.get("PORT", "8000"))
        uvicorn.run("main:app", host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()