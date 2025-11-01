"""
Generate Sample Cases for UI Testing
-------------------------------------
Creates sample cases across different cities so the UI has data to display.
"""

import requests
import time

def create_sample_cases():
    """Create sample cases for UI testing"""
    
    api_url = "http://127.0.0.1:8000/run_case"
    
    sample_cases = [
        {
            "project_id": "ui_test_mumbai_01",
            "case_id": "ui_mumbai_small_plot",
            "city": "Mumbai",
            "document": "DCPR_2034.pdf",
            "parameters": {
                "plot_size": 800,
                "location": "urban",
                "road_width": 12
            }
        },
        {
            "project_id": "ui_test_mumbai_02", 
            "case_id": "ui_mumbai_large_plot",
            "city": "Mumbai",
            "document": "DCPR_2034.pdf",
            "parameters": {
                "plot_size": 2500,
                "location": "urban",
                "road_width": 24
            }
        },
        {
            "project_id": "ui_test_pune_01",
            "case_id": "ui_pune_medium_plot",
            "city": "Pune", 
            "document": "PMC_Rules.pdf",
            "parameters": {
                "plot_size": 1200,
                "location": "suburban",
                "road_width": 15
            }
        },
        {
            "project_id": "ui_test_ahmedabad_01",
            "case_id": "ui_ahmedabad_compact",
            "city": "Ahmedabad",
            "document": "AUDA_Rules.pdf", 
            "parameters": {
                "plot_size": 600,
                "location": "urban",
                "road_width": 9
            }
        },
        {
            "project_id": "ui_test_nashik_01",
            "case_id": "ui_nashik_standard",
            "city": "Nashik",
            "document": "NMC_Rules.pdf",
            "parameters": {
                "plot_size": 1000,
                "location": "urban", 
                "road_width": 14
            }
        }
    ]
    
    print("🏗️ Creating sample cases for UI testing...")
    print("="*60)
    
    successful_cases = []
    
    for i, case in enumerate(sample_cases, 1):
        print(f"\n{i}. Creating: {case['case_id']} ({case['city']})")
        
        try:
            response = requests.post(api_url, json=case, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success - Confidence: {result.get('confidence_level', 'N/A')} ({result.get('confidence_score', 0):.1%})")
                successful_cases.append(case)
            else:
                print(f"   ❌ Failed - Status: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay to avoid overwhelming the API
        time.sleep(1)
    
    print("\n" + "="*60)
    print(f"✅ Created {len(successful_cases)} sample cases successfully!")
    print("\n📋 Cases created:")
    
    for case in successful_cases:
        print(f"  • {case['city']}: {case['case_id']}")
    
    print(f"\n🌐 You can now test the UI at: http://localhost:8503")
    print("   1. Select a city from the dropdown")
    print("   2. Choose a case to review") 
    print("   3. Provide upvote/downvote feedback")
    print("   4. Your feedback will be stored in MCP for RL training!")

if __name__ == "__main__":
    create_sample_cases()