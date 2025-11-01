"""
Complete System Demo Runner
----------------------------
This script orchestrates a complete demonstration of the AI Rule Intelligence
& Design Platform Bridge system.

It demonstrates:
1. Database initialization
2. API server startup
3. Multi-city case processing
4. Feedback collection
5. City-adaptive learning
6. Visualization
"""

import subprocess
import time
import requests
import json
import sys
import os
from datetime import datetime


class DemoRunner:
    """Orchestrates the complete system demonstration"""
    
    def __init__(self):
        self.main_api_url = "http://127.0.0.1:8000"
        self.bridge_api_url = "http://127.0.0.1:8001/api/design-bridge"
        self.processes = []
    
    def print_header(self, text):
        """Print formatted section header"""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")
    
    def print_step(self, step_num, text):
        """Print formatted step"""
        print(f"\n🔹 Step {step_num}: {text}")
        print("-" * 80)
    
    def check_api(self, url, name):
        """Check if API is running"""
        try:
            response = requests.get(url, timeout=2)
            print(f"✓ {name} is running")
            return True
        except:
            print(f"✗ {name} is NOT running")
            return False
    
    def run_demo(self):
        """Run complete demo"""
        
        self.print_header("🚀 AI RULE INTELLIGENCE & DESIGN PLATFORM DEMO")
        
        # Step 1: Check prerequisites
        self.print_step(1, "Checking Prerequisites")
        
        if not os.path.exists(".env"):
            print("⚠ WARNING: .env file not found. Make sure GEMINI_API_KEY is set.")
        
        # Step 2: Initialize database
        self.print_step(2, "Initializing Database")
        
        try:
            print("Running database_setup.py...")
            result = subprocess.run([sys.executable, "database_setup.py"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✓ Database initialized successfully")
            else:
                print(f"⚠ Database initialization warning: {result.stderr}")
        except Exception as e:
            print(f"⚠ Database initialization error: {e}")
        
        # Step 3: Check if APIs are running
        self.print_step(3, "Checking API Servers")
        
        main_api_running = self.check_api(f"{self.main_api_url}/rules/Mumbai", "Main API (Port 8000)")
        bridge_api_running = self.check_api(f"{self.bridge_api_url}/health", "Bridge API (Port 8001)")
        
        if not main_api_running:
            print("\n⚠ Please start the Main API in another terminal:")
            print("   python main.py")
            print("\n   Then run this demo script again.")
            return
        
        if not bridge_api_running:
            print("\n⚠ Please start the Bridge API in another terminal:")
            print("   python api_bridge.py")
            print("\n   Continuing without Bridge API (some features will be limited)...")
        
        # Step 4: Demonstrate rule retrieval
        self.print_step(4, "Fetching Rules by City")
        
        cities = ["Mumbai", "Pune", "Ahmedabad"]
        for city in cities:
            try:
                response = requests.get(f"{self.main_api_url}/rules/{city}", timeout=10)
                if response.status_code == 200:
                    rules = response.json()
                    print(f"  {city}: {len(rules)} rules found")
                else:
                    print(f"  {city}: Error {response.status_code}")
            except Exception as e:
                print(f"  {city}: Error - {e}")
        
        # Step 5: Run sample cases
        self.print_step(5, "Processing Sample Cases")
        
        sample_cases = [
            {
                "project_id": "demo_mumbai_01",
                "case_id": "demo_mumbai_case_001",
                "city": "Mumbai",
                "document": "DCPR_2034.pdf",
                "parameters": {
                    "plot_size": 1500,
                    "location": "urban",
                    "road_width": 18
                }
            },
            {
                "project_id": "demo_pune_01",
                "case_id": "demo_pune_case_001",
                "city": "Pune",
                "document": "PMC_Rules.pdf",
                "parameters": {
                    "plot_size": 2000,
                    "location": "urban",
                    "road_width": 20
                }
            }
        ]
        
        results = []
        for case in sample_cases:
            print(f"\n  Processing: {case['case_id']} ({case['city']})")
            try:
                response = requests.post(
                    f"{self.main_api_url}/run_case",
                    json=case,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    results.append(result)
                    
                    print(f"    ✓ Success")
                    print(f"    Rules Applied: {len(result.get('rules_applied', []))}")
                    print(f"    Confidence: {result.get('confidence_level', 'N/A')} ({result.get('confidence_score', 0):.2%})")
                    
                    # Show first 150 chars of reasoning
                    reasoning = result.get('reasoning', '')
                    if reasoning:
                        print(f"    Reasoning: {reasoning[:150]}...")
                else:
                    print(f"    ✗ Error: {response.status_code}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
        
        # Step 6: Demonstrate feedback
        self.print_step(6, "Simulating User Feedback")
        
        if results:
            for idx, result in enumerate(results):
                feedback_type = "up" if idx % 2 == 0 else "down"
                
                feedback_data = {
                    "project_id": result.get("project_id"),
                    "case_id": result.get("case_id"),
                    "input_case": sample_cases[idx],
                    "output_report": result,
                    "user_feedback": feedback_type
                }
                
                try:
                    response = requests.post(
                        f"{self.main_api_url}/feedback",
                        json=feedback_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print(f"  ✓ Feedback '{feedback_type}' recorded for {result.get('case_id')}")
                    else:
                        print(f"  ✗ Feedback failed: {response.status_code}")
                except Exception as e:
                    print(f"  ✗ Feedback error: {e}")
        
        # Step 7: Show city statistics
        if bridge_api_running:
            self.print_step(7, "City-Specific Analytics")
            
            for city in cities:
                try:
                    response = requests.get(
                        f"{self.bridge_api_url}/feedback/city/{city}/stats",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        stats = response.json()
                        print(f"\n  {city}:")
                        print(f"    Total Feedback: {stats.get('total_feedback', 0)}")
                        print(f"    Approval Rate: {stats.get('approval_rate', 0):.1f}%")
                        if stats.get('confidence_avg'):
                            print(f"    Avg Confidence: {stats.get('confidence_avg', 0):.3f}")
                except:
                    print(f"  {city}: No stats available yet")
        
        # Step 8: Summary
        self.print_header("✅ DEMO COMPLETE")
        
        print("Summary:")
        print(f"  • Processed {len(results)} cases")
        print(f"  • Tested {len(cities)} cities")
        print(f"  • Generated AI reasoning with confidence scores")
        print(f"  • Stored all outputs in MCP database")
        
        print("\nNext Steps:")
        print("  1. View detailed results in outputs/projects/")
        print("  2. Check MCP database: rules_db/rules.db")
        print("  3. Launch visualization UI:")
        print("     streamlit run design_platform_ui.py")
        print("  4. Review API docs:")
        print(f"     Main API: {self.main_api_url}/docs")
        if bridge_api_running:
            print(f"     Bridge API: {self.bridge_api_url}/docs")
        
        print("\nFor full testing:")
        print("  python tests/test_multi_city.py")
        
        print("\n" + "="*80)
        print("  Thank you for exploring the AI Rule Intelligence System!")
        print("="*80 + "\n")


if __name__ == "__main__":
    demo = DemoRunner()
    demo.run_demo()
