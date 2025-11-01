"""
Database Migration Script
-------------------------
Adds the new columns to the existing reasoning_outputs table
for the enhanced AI Rule Intelligence system.
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add new columns to the reasoning_outputs table"""
    
    db_path = Path("rules_db/rules.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run database_setup.py first.")
        return False
    
    print("🔄 Migrating database schema...")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(reasoning_outputs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns: {columns}")
        
        # Add missing columns if they don't exist
        new_columns = [
            ("clause_summaries", "JSON"),
            ("confidence_level", "TEXT"),
            ("confidence_note", "TEXT")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE reasoning_outputs ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️  Column already exists: {column_name}")
                    else:
                        print(f"❌ Error adding {column_name}: {e}")
            else:
                print(f"ℹ️  Column already exists: {column_name}")
        
        conn.commit()
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(reasoning_outputs)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Updated columns: {updated_columns}")
        
        # Test if we can insert with new schema
        test_data = {
            'id': 'test_migration',
            'case_id': 'test_case',
            'project_id': 'test_project',
            'rules_applied': '[]',
            'reasoning_summary': 'Test reasoning',
            'clause_summaries': '[]',
            'confidence_score': 0.5,
            'confidence_level': 'Moderate',
            'confidence_note': 'Test note',
            'timestamp': '2025-10-13T10:00:00Z'
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO reasoning_outputs 
            (id, case_id, project_id, rules_applied, reasoning_summary, 
             clause_summaries, confidence_score, confidence_level, confidence_note, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(test_data.values()))
        
        # Clean up test data
        cursor.execute("DELETE FROM reasoning_outputs WHERE id = 'test_migration'")
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print("✅ Schema validation passed!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  DATABASE MIGRATION - AI Rule Intelligence v2.0")
    print("="*60)
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Database migration completed!")
        print("📋 The system is now ready to use the enhanced schema.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")