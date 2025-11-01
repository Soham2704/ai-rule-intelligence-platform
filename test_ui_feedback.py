#!/usr/bin/env python3

import requests
from database_setup import SessionLocal, Feedback

def test_ui_feedback_flow():
    """Test the exact feedback flow from the UI"""
    
    print("🔍 TESTING UI FEEDBACK FLOW")
    print("=" * 50)
    
    # Step 1: Check current state
    db = SessionLocal()
    before_count = db.query(Feedback).count()
    mumbai_before = db.query(Feedback).filter(Feedback.city == 'Mumbai').count()
    print(f"📊 Before - Total: {before_count}, Mumbai: {mumbai_before}")
    db.close()
    
    # Step 2: Simulate getting a case from bridge API (like UI does)
    print("\n🌉 Getting case data from Bridge API...")
    try:
        response = requests.get("http://127.0.0.1:8001/api/design-bridge/reasoning/debug_case_001")
        if response.status_code == 200:
            reasoning_data = response.json()
            print("✅ Got reasoning data from bridge")
            print(f"📋 Case ID: {reasoning_data.get('case_id')}")
            print(f"📋 City: {reasoning_data.get('city')}")
        else:
            # Simulate fallback case data (like UI does when bridge fails)
            reasoning_data = {
                "case_id": "test_ui_case_001",
                "project_id": "test_ui_project", 
                "city": "Mumbai",
                "reasoning": "Test reasoning from UI simulation",
                "confidence_score": 0.85,
                "parameters": {
                    "plot_size": 1200,
                    "location": "urban", 
                    "road_width": 15
                }
            }
            print("⚠️  Using fallback case data (simulating UI fallback)")
    except:
        reasoning_data = {
            "case_id": "test_ui_case_001", 
            "project_id": "test_ui_project",
            "city": "Mumbai",
            "reasoning": "Test reasoning from UI simulation",
            "confidence_score": 0.85,
            "parameters": {
                "plot_size": 1200,
                "location": "urban",
                "road_width": 15
            }
        }
        print("❌ Bridge API failed, using fallback data")
    
    # Step 3: Create exact payload as UI does
    print(f"\n📤 Creating feedback payload (exactly like UI)...")
    feedback_payload = {
        "project_id": reasoning_data.get("project_id", "unknown"),
        "case_id": reasoning_data.get("case_id", "unknown"), 
        "input_case": {
            "city": reasoning_data.get("city", "unknown"),
            "parameters": reasoning_data.get("parameters", {})
        },
        "output_report": reasoning_data,
        "user_feedback": "up"
    }
    
    print("📋 Payload being sent:")
    import json
    print(json.dumps(feedback_payload, indent=2))
    
    # Step 4: Submit feedback
    print(f"\n📡 Submitting feedback to main API...")
    try:
        response = requests.post("http://127.0.0.1:8000/feedback", json=feedback_payload, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ API accepted the feedback")
        else:
            print("❌ API rejected the feedback") 
            return
            
    except Exception as e:
        print(f"❌ Error submitting feedback: {e}")
        return
    
    # Step 5: Check database after
    print(f"\n🔍 Checking database after submission...")
    db = SessionLocal()
    after_count = db.query(Feedback).count()
    mumbai_after = db.query(Feedback).filter(Feedback.city == 'Mumbai').count()
    print(f"📊 After - Total: {after_count}, Mumbai: {mumbai_after}")
    
    # Show recent feedback
    recent_feedback = db.query(Feedback).filter(
        Feedback.case_id == reasoning_data.get("case_id")
    ).first()
    
    if recent_feedback:
        print("✅ Found the feedback in database:")
        print(f"   ID: {recent_feedback.id}")
        print(f"   Case ID: {recent_feedback.case_id}")
        print(f"   City: {recent_feedback.city}")
        print(f"   Type: {recent_feedback.feedback_type}")
        print(f"   Timestamp: {recent_feedback.timestamp}")
    else:
        print("❌ Feedback NOT found in database!")
    
    db.close()
    
    # Step 6: Test bridge API stats
    print(f"\n🌉 Testing Bridge API stats...")
    try:
        response = requests.get("http://127.0.0.1:8001/api/design-bridge/feedback/city/Mumbai/stats")
        print(f"Bridge Stats Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print("📊 Bridge API Stats:")
            print(f"   Total: {stats.get('total_feedback', 0)}")
            print(f"   Upvotes: {stats.get('upvotes', 0)}")
            print(f"   Downvotes: {stats.get('downvotes', 0)}")
        else:
            print(f"Bridge Stats Error: {response.text}")
    except Exception as e:
        print(f"Bridge Stats Error: {e}")
    
    print(f"\n🎯 DIAGNOSIS:")
    if after_count > before_count:
        print("✅ Feedback IS being recorded in database")
        print("❓ Issue might be with Bridge API stats calculation") 
    else:
        print("❌ Feedback is NOT being recorded in database")
        print("❓ Issue is with main API or MCP client")

if __name__ == "__main__":
    test_ui_feedback_flow()