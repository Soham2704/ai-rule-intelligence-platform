"""
Multi-City Integration Testing
-------------------------------
Comprehensive test suite for validating the system across multiple cities:
- Mumbai, Pune, Ahmedabad, Nashik

Tests include:
1. Rule retrieval and application
2. AI reasoning generation
3. Confidence score calculation
4. Geometry generation
5. MCP data storage
6. API endpoint validation
"""

import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import MCPClient
from database_setup import SessionLocal, Rule, ReasoningOutput


class MultiCityTester:
    """Comprehensive multi-city testing framework"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.api_url = api_url
        self.bridge_api_url = "http://127.0.0.1:8001/api/design-bridge"
        self.results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tests_passed": 0,
            "tests_failed": 0,
            "city_results": {}
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "ERROR": "✗",
            "WARNING": "⚠"
        }.get(level, "·")
        print(f"[{timestamp}] {prefix} {message}")
    
    def test_case(self, city: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case for a city.
        
        Args:
            city: City name
            test_data: Test case data with parameters
            
        Returns:
            Test result dictionary
        """
        self.log(f"Testing {city} - {test_data.get('case_id')}", "INFO")
        
        result = {
            "city": city,
            "case_id": test_data.get("case_id"),
            "status": "PENDING",
            "checks": {},
            "errors": []
        }
        
        try:
            # 1. Send request to main API
            response = requests.post(
                f"{self.api_url}/run_case",
                json=test_data,
                timeout=60
            )
            
            if response.status_code != 200:
                result["status"] = "FAILED"
                result["errors"].append(f"API returned status {response.status_code}")
                return result
            
            report = response.json()
            result["report"] = report
            
            # 2. Validate response structure
            required_fields = [
                "project_id", "case_id", "rules_applied", 
                "reasoning", "confidence_score", "confidence_level"
            ]
            
            for field in required_fields:
                if field in report:
                    result["checks"][f"has_{field}"] = True
                else:
                    result["checks"][f"has_{field}"] = False
                    result["errors"].append(f"Missing field: {field}")
            
            # 3. Validate confidence score
            confidence = report.get("confidence_score")
            if confidence is not None and 0 <= confidence <= 1:
                result["checks"]["valid_confidence"] = True
            else:
                result["checks"]["valid_confidence"] = False
                result["errors"].append(f"Invalid confidence score: {confidence}")
            
            # 4. Check reasoning is not empty
            reasoning = report.get("reasoning", "")
            if reasoning and len(reasoning) > 50:
                result["checks"]["has_reasoning"] = True
            else:
                result["checks"]["has_reasoning"] = False
                result["errors"].append("Reasoning is empty or too short")
            
            # 5. Verify MCP storage
            case_id = test_data.get("case_id")
            db = SessionLocal()
            reasoning_record = db.query(ReasoningOutput).filter(
                ReasoningOutput.case_id == case_id
            ).first()
            
            if reasoning_record:
                result["checks"]["stored_in_mcp"] = True
                result["mcp_confidence"] = reasoning_record.confidence_score
            else:
                result["checks"]["stored_in_mcp"] = False
                result["errors"].append("Not found in MCP reasoning_outputs")
            
            db.close()
            
            # 6. Check geometry file exists
            project_id = test_data.get("project_id")
            geometry_path = f"outputs/projects/{project_id}/{case_id}_geometry.stl"
            if os.path.exists(geometry_path):
                result["checks"]["geometry_generated"] = True
                result["geometry_size_kb"] = os.path.getsize(geometry_path) / 1024
            else:
                result["checks"]["geometry_generated"] = False
                result["errors"].append("Geometry file not found")
            
            # 7. Test Bridge API endpoints
            try:
                # Test reasoning endpoint
                bridge_response = requests.get(
                    f"{self.bridge_api_url}/reasoning/{case_id}",
                    timeout=10
                )
                if bridge_response.status_code == 200:
                    result["checks"]["bridge_api_reasoning"] = True
                else:
                    result["checks"]["bridge_api_reasoning"] = False
                    result["errors"].append(f"Bridge API reasoning failed: {bridge_response.status_code}")
            except Exception as e:
                result["checks"]["bridge_api_reasoning"] = False
                result["errors"].append(f"Bridge API error: {str(e)}")
            
            # Determine overall status
            if all(result["checks"].values()):
                result["status"] = "PASSED"
                self.results["tests_passed"] += 1
                self.log(f"{city} - {case_id}: PASSED", "SUCCESS")
            else:
                result["status"] = "PARTIAL"
                self.results["tests_failed"] += 1
                self.log(f"{city} - {case_id}: PARTIAL ({len(result['errors'])} issues)", "WARNING")
        
        except Exception as e:
            result["status"] = "FAILED"
            result["errors"].append(f"Exception: {str(e)}")
            self.results["tests_failed"] += 1
            self.log(f"{city} - {case_id}: FAILED - {str(e)}", "ERROR")
        
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run tests for all cities"""
        
        self.log("="*80, "INFO")
        self.log("MULTI-CITY INTEGRATION TESTS", "INFO")
        self.log("="*80, "INFO")
        
        # Define test cases for each city
        test_cases = {
            "Mumbai": [
                {
                    "project_id": "test_mumbai_urban_01",
                    "case_id": "mumbai_test_001",
                    "city": "Mumbai",
                    "document": "DCPR_2034.pdf",
                    "parameters": {
                        "plot_size": 1500,
                        "location": "urban",
                        "road_width": 18
                    }
                },
                {
                    "project_id": "test_mumbai_suburban_01",
                    "case_id": "mumbai_test_002",
                    "city": "Mumbai",
                    "document": "DCPR_2034.pdf",
                    "parameters": {
                        "plot_size": 800,
                        "location": "suburban",
                        "road_width": 12
                    }
                }
            ],
            "Pune": [
                {
                    "project_id": "test_pune_urban_01",
                    "case_id": "pune_test_001",
                    "city": "Pune",
                    "document": "PMC_Rules.pdf",
                    "parameters": {
                        "plot_size": 2000,
                        "location": "urban",
                        "road_width": 20
                    }
                },
                {
                    "project_id": "test_pune_mixed_01",
                    "case_id": "pune_test_002",
                    "city": "Pune",
                    "document": "PMC_Rules.pdf",
                    "parameters": {
                        "plot_size": 1200,
                        "location": "suburban",
                        "road_width": 15
                    }
                }
            ],
            "Ahmedabad": [
                {
                    "project_id": "test_ahmedabad_urban_01",
                    "case_id": "ahmedabad_test_001",
                    "city": "Ahmedabad",
                    "document": "AUDA_Regulations.pdf",
                    "parameters": {
                        "plot_size": 1800,
                        "location": "urban",
                        "road_width": 16
                    }
                }
            ],
            "Nashik": [
                {
                    "project_id": "test_nashik_urban_01",
                    "case_id": "nashik_test_001",
                    "city": "Nashik",
                    "document": "NMC_Rules.pdf",
                    "parameters": {
                        "plot_size": 1000,
                        "location": "urban",
                        "road_width": 14
                    }
                }
            ]
        }
        
        # Run tests for each city
        for city, cases in test_cases.items():
            self.log(f"\n--- Testing {city} ({len(cases)} cases) ---", "INFO")
            
            city_results = []
            for case in cases:
                result = self.test_case(city, case)
                city_results.append(result)
            
            self.results["city_results"][city] = city_results
        
        # Generate summary
        self.log("\n" + "="*80, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("="*80, "INFO")
        
        total_tests = self.results["tests_passed"] + self.results["tests_failed"]
        self.log(f"Total Tests: {total_tests}", "INFO")
        self.log(f"Passed: {self.results['tests_passed']}", "SUCCESS")
        self.log(f"Failed: {self.results['tests_failed']}", "ERROR" if self.results['tests_failed'] > 0 else "INFO")
        
        # City-specific summary
        for city, results in self.results["city_results"].items():
            passed = sum(1 for r in results if r["status"] == "PASSED")
            total = len(results)
            self.log(f"{city}: {passed}/{total} passed", "SUCCESS" if passed == total else "WARNING")
        
        # Save results to file
        results_file = f"tests/multi_city_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("tests", exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"\n✓ Results saved to: {results_file}", "SUCCESS")
        
        return self.results


def main():
    """Main test execution"""
    
    # Check if APIs are running
    print("\n🔍 Checking API availability...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/rules/Mumbai", timeout=5)
        print("✓ Main API is running")
    except:
        print("✗ Main API is NOT running. Please start it first:")
        print("  python main.py")
        return
    
    try:
        response = requests.get("http://127.0.0.1:8001/api/design-bridge/health", timeout=5)
        print("✓ Bridge API is running")
    except:
        print("⚠ Bridge API is NOT running. Some tests may fail.")
        print("  You can start it with: python api_bridge.py")
    
    # Run tests
    tester = MultiCityTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["tests_failed"] == 0:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠ {results['tests_failed']} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
