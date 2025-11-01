#!/usr/bin/env python3
"""
Full startup script for the AI Rule Intelligence Platform.
This script starts both the main API and the API bridge services.
"""

import os
import sys
import subprocess
import time
import threading

def initialize_database():
    """Initialize the database with required tables and data."""
    print("Initializing database...")
    try:
        from database_setup import create_database
        create_database()
        print("Database initialized successfully.")
        
        # Populate with Mumbai rules
        print("Populating database with Mumbai rules...")
        from populate_comprehensive_rules import populate_comprehensive_rules
        populate_comprehensive_rules()
        print("Mumbai rules populated successfully.")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        import traceback
        traceback.print_exc()

def start_main_api():
    """Start the main API service."""
    print("Starting Main API service...")
    try:
        # Use subprocess to run the main API in the background
        main_api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        print("Main API service started on port 8000")
        return main_api_process
    except Exception as e:
        print(f"Error starting Main API service: {e}")
        import traceback
        traceback.print_exc()
        return None

def start_api_bridge():
    """Start the API bridge service."""
    print("Starting API Bridge service...")
    try:
        # Use subprocess to run the API bridge in the background
        bridge_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api_bridge:app", 
            "--host", "0.0.0.0", 
            "--port", "8001"
        ])
        print("API Bridge service started on port 8001")
        return bridge_process
    except Exception as e:
        print(f"Error starting API Bridge service: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("Starting AI Rule Intelligence Platform (Full Services)...")
    
    # Initialize database
    initialize_database()
    
    # Start both services
    main_api_process = start_main_api()
    bridge_process = start_api_bridge()
    
    if main_api_process is None or bridge_process is None:
        print("Failed to start one or more services. Exiting.")
        sys.exit(1)
    
    # Wait for both processes
    try:
        main_api_process.wait()
        bridge_process.wait()
    except KeyboardInterrupt:
        print("Shutting down services...")
        main_api_process.terminate()
        bridge_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()