#!/usr/bin/env python3

import requests
import json
from database_setup import SessionLocal, Feedback
from datetime import datetime

def test_feedback_recording():
    """Comprehensive test to diagnose feedback recording issues"""
    
    print("🔍 FEEDBACK SYSTEM DIAGNOSIS")
    print("=" * 60)
    
    # Step 1: Check current feedback in database
    print("1️⃣ Checking Current Database State...")
    db = SessionLocal()
    try:
        feedback_count_before = db.query(Feedback).count()
        print(f"   📊 Current feedback records: {feedback_count_before}")
        
        # Show existing feedback by city
        if feedback_count_before > 0:
            cities_query = db.query(Feedback.city).distinct().filter(Feedback.city.isnot(None))
            cities = [c[0] for c in cities_query.all()]
            
            for city in cities:
                upvotes = db.query(Feedback).filter(
                    Feedback.city == city, 
                    Feedback.feedback_type == 'up'
                ).count()
                
                downvotes = db.query(Feedback).filter(
                    Feedback.city == city, 
                    Feedback.feedback_type == 'down'
                ).count()
                
                print(f"   🏙️  {city}: {upvotes} upvotes, {downvotes} downvotes")
        else:
            print("   ⚠️  No feedback records found")
            
    finally:
        db.close()
    
    # Step 2: Test API connectivity
    print(f"\n2️⃣ Testing API Connectivity...")
    main_api_url = "http://127.0.0.1:8000"
    bridge_api_url = "http://127.0.0.1:8001/api/design-bridge"
    
    try:
        # Test main API
        response = requests.get(f"{main_api_url}/health", timeout=3)
        if response.status_code == 200:
            print("   ✅ Main API (port 8000) is running")
        else:
            print(f"   ⚠️  Main API returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Main API not accessible: {e}")
    
    try:
        # Test bridge API
        response = requests.get(f"{bridge_api_url}/health", timeout=3)
        if response.status_code == 200:
            print("   ✅ Bridge API (port 8001) is running")
        else:
            print(f"   ⚠️  Bridge API returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Bridge API not accessible: {e}")
    
    # Step 3: Submit test feedback
    print(f"\n3️⃣ Submitting Test Feedback...")
    
    test_feedback = {
        "project_id": "test_feedback_debug",
        "case_id": "debug_case_001", 
        "input_case": {
            "city": "Mumbai",
            "parameters": {
                "plot_size": 1200,
                "location": "urban",
                "road_width": 12
            }
        },
        "output_report": {
            "case_id": "debug_case_001",
            "city": "Mumbai",
            "reasoning": "Test reasoning for feedback debugging",
            "confidence_score": 0.85,
            "confidence_level": "High"
        },
        "user_feedback": "up"
    }
    
    try:
        print(f"   📤 Sending feedback to {main_api_url}/feedback...")
        response = requests.post(
            f"{main_api_url}/feedback",
            json=test_feedback,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Feedback submitted successfully!")
            response_data = response.json()
            print(f"   📋 Response: {response_data}")
        else:
            print(f"   ❌ Feedback submission failed")
            print(f"   📋 Error response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Feedback submission error: {e}")
    
    # Step 4: Check if feedback was recorded
    print(f"\n4️⃣ Verifying Database Update...")
    db = SessionLocal()
    try:
        feedback_count_after = db.query(Feedback).count()
        print(f"   📊 Feedback records after test: {feedback_count_after}")
        
        if feedback_count_after > feedback_count_before:
            print("   ✅ NEW FEEDBACK RECORDED!")
            # Show the new feedback
            new_feedback = db.query(Feedback).filter(
                Feedback.case_id == "debug_case_001"
            ).first()
            
            if new_feedback:
                print(f"   📋 New feedback details:")
                print(f"      ID: {new_feedback.id}")
                print(f"      Case ID: {new_feedback.case_id}")
                print(f"      City: {new_feedback.city}")
                print(f"      Type: {new_feedback.feedback_type}")
                print(f"      Timestamp: {new_feedback.timestamp}")
        else:
            print("   ❌ NO NEW FEEDBACK FOUND - Issue confirmed!")
            
    finally:
        db.close()
    
    # Step 5: Test Bridge API Stats
    print(f"\n5️⃣ Testing Bridge API Stats...")
    try:
        response = requests.get(f"{bridge_api_url}/feedback/city/Mumbai/stats", timeout=5)
        
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Bridge API stats working!")
            print(f"   📊 Mumbai stats:")
            print(f"      Total Feedback: {stats.get('total_feedback', 0)}")
            print(f"      Upvotes: {stats.get('upvotes', 0)}")
            print(f"      Downvotes: {stats.get('downvotes', 0)}")
            print(f"      Approval Rate: {stats.get('approval_rate', 0):.1f}%")
        elif response.status_code == 404:
            print("   ⚠️  No feedback data found for Mumbai (expected if database is empty)")
        else:
            print(f"   ❌ Bridge API stats failed: {response.status_code}")
            print(f"   📋 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Bridge API stats error: {e}")
    
    # Step 6: Recommendations
    print(f"\n6️⃣ DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if feedback_count_after > feedback_count_before:
        print("✅ FEEDBACK SYSTEM IS WORKING!")
        print("   The issue might be in the UI refresh or stats display logic.")
    else:
        print("❌ FEEDBACK NOT BEING RECORDED!")
        print("   Possible issues:")
        print("   1. Main API feedback endpoint not working")
        print("   2. Database connection issues") 
        print("   3. MCP client not saving feedback")
        print("   4. Request format issues")

if __name__ == "__main__":
    test_feedback_recording()