#!/usr/bin/env python3

import time
from database_setup import SessionLocal, Feedback
import requests

def monitor_feedback_realtime():
    """Monitor feedback table in real-time to see what happens during UI submission"""
    
    print("🔍 REAL-TIME FEEDBACK MONITORING")
    print("=" * 60)
    print("This will monitor the database while you submit feedback through the UI...")
    print("Please keep this running and go submit feedback in the UI now!")
    print()
    
    db = SessionLocal()
    
    # Get initial state
    initial_total = db.query(Feedback).count()
    initial_mumbai = db.query(Feedback).filter(Feedback.city == 'Mumbai').count()
    
    print(f"📊 Initial state:")
    print(f"   Total feedback: {initial_total}")
    print(f"   Mumbai feedback: {initial_mumbai}")
    print()
    print("👀 Monitoring for changes... (Press Ctrl+C to stop)")
    print("-" * 60)
    
    last_total = initial_total
    last_mumbai = initial_mumbai
    
    try:
        while True:
            # Check current state
            current_total = db.query(Feedback).count()
            current_mumbai = db.query(Feedback).filter(Feedback.city == 'Mumbai').count()
            
            # Check if anything changed
            if current_total != last_total or current_mumbai != last_mumbai:
                timestamp = time.strftime("%H:%M:%S")
                print(f"🚨 [{timestamp}] CHANGE DETECTED!")
                print(f"   Total: {last_total} → {current_total} (+{current_total - last_total})")
                print(f"   Mumbai: {last_mumbai} → {current_mumbai} (+{current_mumbai - last_mumbai})")
                
                # Show the latest feedback record
                latest = db.query(Feedback).order_by(Feedback.timestamp.desc()).first()
                if latest:
                    print(f"   Latest feedback:")
                    print(f"     ID: {latest.id}")
                    print(f"     Case: {latest.case_id}")
                    print(f"     City: '{latest.city}'")
                    print(f"     Type: {latest.feedback_type}")
                    print(f"     Time: {latest.timestamp}")
                
                # Test Bridge API immediately
                try:
                    response = requests.get(f"http://127.0.0.1:8001/api/design-bridge/feedback/city/Mumbai/stats?t={int(time.time())}")
                    if response.status_code == 200:
                        stats = response.json()
                        print(f"   Bridge API stats:")
                        print(f"     Total: {stats.get('total_feedback', 0)}")
                        print(f"     Upvotes: {stats.get('upvotes', 0)}")
                        print(f"     Downvotes: {stats.get('downvotes', 0)}")
                    else:
                        print(f"   Bridge API error: {response.status_code}")
                except Exception as e:
                    print(f"   Bridge API error: {e}")
                
                print("-" * 60)
                
                last_total = current_total
                last_mumbai = current_mumbai
            
            time.sleep(0.5)  # Check every 500ms
            
    except KeyboardInterrupt:
        print(f"\n📊 Final state:")
        final_total = db.query(Feedback).count()
        final_mumbai = db.query(Feedback).filter(Feedback.city == 'Mumbai').count()
        print(f"   Total feedback: {initial_total} → {final_total} (+{final_total - initial_total})")
        print(f"   Mumbai feedback: {initial_mumbai} → {final_mumbai} (+{final_mumbai - initial_mumbai})")
    
    finally:
        db.close()

if __name__ == "__main__":
    monitor_feedback_realtime()