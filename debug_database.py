#!/usr/bin/env python3
"""
Debug script to check database status on Render
"""

import os
import sys

def debug_database():
    print("=== Database Debug Script ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Check environment
    print(f"Render environment: {os.environ.get('RENDER', 'Not detected')}")
    
    # Try to import and initialize database
    try:
        print("Importing database_setup...")
        from database_setup import DB_PATH, create_database, SessionLocal, Rule
        print(f"Database path: {DB_PATH}")
        print(f"Database file exists: {os.path.exists(DB_PATH)}")
        
        if os.path.exists(DB_PATH):
            print("Database file size:", os.path.getsize(DB_PATH))
        
        # Create database
        print("Creating database...")
        create_database()
        
        # Check tables
        from sqlalchemy import inspect
        from database_setup import engine
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Database tables: {tables}")
        
        # Try to query rules
        print("Querying Mumbai rules...")
        db = SessionLocal()
        total_rules = db.query(Rule).filter(Rule.city == "Mumbai").count()
        print(f"Total Mumbai rules: {total_rules}")
        
        if total_rules > 0:
            sample_rules = db.query(Rule).filter(Rule.city == "Mumbai").limit(3).all()
            print("Sample rules:")
            for rule in sample_rules:
                print(f"  - {rule.id}: {rule.rule_type}")
        else:
            print("No Mumbai rules found!")
            
        db.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database()