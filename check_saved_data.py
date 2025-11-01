from database_setup import SessionLocal, ReasoningOutput, GeometryOutput, Feedback
import json
import os

def check_database_records():
    """Check what's saved in the database"""
    db = SessionLocal()
    
    print("=" * 70)
    print("DATABASE RECORDS CHECK")
    print("=" * 70)
    
    # Check ReasoningOutputs
    print("\n📊 REASONING OUTPUTS:")
    print("-" * 70)
    reasoning_records = db.query(ReasoningOutput).all()
    print(f"Total Records: {len(reasoning_records)}\n")
    
    for idx, r in enumerate(reasoning_records, 1):
        print(f"{idx}. Case ID: {r.case_id}")
        print(f"   Project ID: {r.project_id}")
        print(f"   Rules Applied: {len(r.rules_applied) if r.rules_applied else 0}")
        print(f"   Confidence: {r.confidence_score} ({r.confidence_level})")
        print(f"   Reasoning Preview: {r.reasoning_summary[:150] if r.reasoning_summary else 'N/A'}...")
        print(f"   Timestamp: {r.timestamp}")
        print()
    
    # Check GeometryOutputs
    print("\n🔷 GEOMETRY OUTPUTS:")
    print("-" * 70)
    geometry_records = db.query(GeometryOutput).all()
    print(f"Total Records: {len(geometry_records)}\n")
    
    for idx, g in enumerate(geometry_records, 1):
        print(f"{idx}. Case ID: {g.case_id}")
        print(f"   Project ID: {g.project_id}")
        print(f"   STL Path: {g.stl_path}")
        print(f"   File Exists: {os.path.exists(g.stl_path)}")
        if os.path.exists(g.stl_path):
            size_kb = os.path.getsize(g.stl_path) / 1024
            print(f"   File Size: {size_kb:.2f} KB")
        print(f"   Timestamp: {g.timestamp}")
        print()
    
    # Check Feedback
    print("\n👍 FEEDBACK RECORDS:")
    print("-" * 70)
    feedback_records = db.query(Feedback).all()
    print(f"Total Records: {len(feedback_records)}\n")
    
    for idx, f in enumerate(feedback_records, 1):
        print(f"{idx}. Case ID: {f.case_id}")
        print(f"   Feedback Type: {f.feedback_type}")
        print(f"   Timestamp: {f.timestamp}")
        print()
    
    db.close()
    
    # Check file system
    print("\n📁 FILE SYSTEM CHECK:")
    print("-" * 70)
    
    outputs_dir = "outputs/projects"
    if os.path.exists(outputs_dir):
        projects = []
        for item in os.listdir(outputs_dir):
            project_path = os.path.join(outputs_dir, item)
            if os.path.isdir(project_path):
                files = os.listdir(project_path)
                projects.append((item, files))
        
        print(f"Total Projects: {len(projects)}\n")
        for project, files in projects:
            print(f"Project: {project}")
            print(f"  Files: {len(files)}")
            for f in files:
                file_path = os.path.join(outputs_dir, project, f)
                size_kb = os.path.getsize(file_path) / 1024
                print(f"    - {f} ({size_kb:.2f} KB)")
            print()
    else:
        print("❌ outputs/projects directory not found!")
    
    # Check reports directory
    reports_dir = "reports"
    if os.path.exists(reports_dir):
        print(f"\n📝 REPORTS DIRECTORY:")
        print("-" * 70)
        report_files = [f for f in os.listdir(reports_dir) if os.path.isfile(os.path.join(reports_dir, f))]
        print(f"Total Files: {len(report_files)}\n")
        for f in report_files:
            file_path = os.path.join(reports_dir, f)
            size_kb = os.path.getsize(file_path) / 1024
            print(f"  - {f} ({size_kb:.2f} KB)")
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print(f"  Database: ✓ {len(reasoning_records)} reasoning + {len(geometry_records)} geometry + {len(feedback_records)} feedback")
    print(f"  Files: {'✓' if os.path.exists(outputs_dir) else '✗'} Project outputs")
    print("=" * 70)

if __name__ == "__main__":
    check_database_records()
