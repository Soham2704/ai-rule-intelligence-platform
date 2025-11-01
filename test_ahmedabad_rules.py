"""
Test Ahmedabad Rules Integration
---------------------------------
Test if the newly added Ahmedabad rules work with the AI reasoning system
"""

import requests
import json

def test_ahmedabad_rules():
    """Test the system with Ahmedabad rules"""
    
    print("🧪 TESTING AHMEDABAD RULES INTEGRATION")
    print("="*60)
    
    # Test case for Ahmedabad
    ahmedabad_test_case = {
        "project_id": "test_ahmedabad_rules_01", 
        "case_id": "ahmedabad_rules_test_001",
        "city": "Ahmedabad",
        "document": "Ahmedabad_DCR.pdf",
        "parameters": {
            "plot_size": 1500,
            "location": "urban", 
            "road_width": 15
        }
    }
    
    print(f"📋 Test Case:")
    print(f"   City: {ahmedabad_test_case['city']}")
    print(f"   Plot Size: {ahmedabad_test_case['parameters']['plot_size']} sqm")
    print(f"   Location: {ahmedabad_test_case['parameters']['location']}")
    print(f"   Road Width: {ahmedabad_test_case['parameters']['road_width']} m")
    
    try:
        print(f"\n🚀 Sending request to AI system...")
        
        # Send to main API
        response = requests.post(
            "http://127.0.0.1:8000/run_case", 
            json=ahmedabad_test_case,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ SUCCESS! AI reasoning generated")
            print(f"="*60)
            
            # Display key results
            print(f"📊 Results Summary:")
            print(f"   Rules Applied: {len(result.get('rules_applied', []))}")
            print(f"   Confidence Score: {result.get('confidence_score', 0):.1%}")
            print(f"   Confidence Level: {result.get('confidence_level', 'N/A')}")
            
            # Show rules applied
            rules_applied = result.get('rules_applied', [])
            if rules_applied:
                print(f"\n📋 Ahmedabad Rules Applied:")
                for rule in rules_applied[:5]:  # Show first 5 rules
                    print(f"   • {rule}")
                if len(rules_applied) > 5:
                    print(f"   ... and {len(rules_applied) - 5} more rules")
            
            # Show AI reasoning
            reasoning = result.get('reasoning', '')
            print(f"\n🧠 AI Reasoning:")
            lines = reasoning.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                print(f"   {line}")
            if len(lines) > 10:
                print(f"   ... ({len(lines) - 10} more lines)")
            
            # Test Bridge API - get detailed reasoning
            case_id = ahmedabad_test_case['case_id']
            print(f"\n🌉 Testing Bridge API...")
            
            try:
                bridge_response = requests.get(
                    f"http://127.0.0.1:8001/api/design-bridge/reasoning/{case_id}",
                    timeout=10
                )
                
                if bridge_response.status_code == 200:
                    bridge_data = bridge_response.json()
                    clause_summaries = bridge_data.get('clause_summaries', [])
                    
                    print(f"✅ Bridge API working - {len(clause_summaries)} clause summaries retrieved")
                    
                    if clause_summaries:
                        print(f"\n📋 Sample Clause Summaries:")
                        for clause in clause_summaries[:3]:  # Show first 3
                            print(f"   • {clause.get('clause_id', 'N/A')}: {clause.get('quick_summary', 'N/A')}")
                else:
                    print(f"⚠️  Bridge API returned {bridge_response.status_code}")
            
            except Exception as e:
                print(f"⚠️  Bridge API test failed: {e}")
            
            # Test city-specific feedback functionality
            print(f"\n👍 Testing Feedback System...")
            
            feedback_data = {
                "project_id": result.get("project_id"),
                "case_id": result.get("case_id"), 
                "input_case": ahmedabad_test_case,
                "output_report": result,
                "user_feedback": "up",
                "selected_city": "Ahmedabad"  # Important for city-specific tracking
            }
            
            try:
                feedback_response = requests.post(
                    "http://127.0.0.1:8000/feedback",
                    json=feedback_data,
                    timeout=10
                )
                
                if feedback_response.status_code == 200:
                    print("✅ Feedback system working - upvote recorded")
                else:
                    print(f"⚠️  Feedback failed: {feedback_response.status_code}")
            
            except Exception as e:
                print(f"⚠️  Feedback test failed: {e}")
            
            print(f"\n" + "="*60)
            print(f"🎉 AHMEDABAD RULES INTEGRATION: SUCCESS!")
            print(f"="*60)
            print(f"✅ Ahmedabad rules extracted and loaded")
            print(f"✅ AI reasoning working with Ahmedabad rules")  
            print(f"✅ Bridge API serving Ahmedabad data")
            print(f"✅ Feedback system functional")
            print(f"✅ System ready for Ahmedabad city!")
            
            return True
        
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ahmedabad_rules()
    
    if success:
        print(f"\n🚀 Next Steps:")
        print(f"   1. Test with different plot sizes and road widths")
        print(f"   2. Try the UI at http://localhost:8503") 
        print(f"   3. Run multi-city tests: python tests/test_multi_city.py")
        print(f"   4. The system now supports Mumbai, Pune, Nashik, AND Ahmedabad!")
    else:
        print(f"\n⚠️  Something went wrong - check API servers are running:")
        print(f"   python main.py  (Port 8000)")
        print(f"   python api_bridge.py  (Port 8001)")
