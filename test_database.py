#!/usr/bin/env python3
"""
Test script to verify database initialization.
"""

import sys
import os

def test_database_creation():
    """Test if the database can be created successfully."""
    try:
        # Add the current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import the database setup
        from database_setup import create_database, engine, Base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        
        print("Testing database creation...")
        
        # Create the database
        create_database()
        
        # Test if we can create a session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Test a simple query
        db.execute(text("SELECT 1"))
        db.close()
        
        print("[SUCCESS] Database creation and connection test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Database Initialization Test")
    print("=" * 30)
    
    if test_database_creation():
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[ERROR] Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())