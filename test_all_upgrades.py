"""
Comprehensive Test: System Upgrades 8.5 → 10.0
-----------------------------------------------
Tests all three major improvements:
1. Enhanced reasoning output with rich formatting
2. REST API documentation validation
3. Adaptive feedback integration and visibility
"""

import requests
import json
import time
from datetime import datetime

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)


def test_enhanced_reasoning():
    """Test Upgrade #1: Enhanced Reasoning Output"""
    print_section("TEST 1: Enhanced Reasoning Output")
    
    print("\n📋 Submitting test case to pipeline...")
    
    test_case = {
        "project_id": "upgrade_test_01",
        "case_id": "enhanced_reasoning_test",
        "city": "Mumbai",
        "document": "Mumbai_DCPR_2034.pdf",
        "parameters": {
            "plot_size": 2000,
            "location": "urban",
            "road_width": 18
        }
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/run_case",
            json=test_case,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ SUCCESS! Analysis complete")
            print("\n" + "-"*80)
            print("📄 REASONING OUTPUT:")
            print("-"*80)
            print(result.get("reasoning", "No reasoning found"))
            
            print("\n" + "-"*80)
            print("📊 KEY METRICS:")
            print("-"*80)
            print(f"  Rules Applied: {len(result.get('rules_applied', []))}")
            print(f"  Confidence Score: {result.get('confidence_score', 0):.1%}")
            print(f"  Confidence Level: {result.get('confidence_level', 'N/A')}")
            
            # Check for enhanced formatting
            reasoning = result.get("reasoning", "")
            has_emoji = any(emoji in reasoning for emoji in ["📍", "📋", "✅"])
            has_sections = all(section in reasoning for section in ["OVERVIEW", "REGULATIONS", "ENTITLEMENTS"])
            has_calculations = "×" in reasoning or "sqm" in reasoning
            
            print("\n" + "-"*80)
            print("🔍 FORMAT VALIDATION:")
            print("-"*80)
            print(f"  {'✅' if has_emoji else '❌'} Contains emoji section headers")
            print(f"  {'✅' if has_sections else '❌'} Has structured sections")
            print(f"  {'✅' if has_calculations else '❌'} Includes calculations")
            
            if has_emoji and has_sections and has_calculations:
                print("\n🎉 UPGRADE #1: PASSED - Enhanced formatting detected!")
                return True
            else:
                print("\n⚠️  UPGRADE #1: PARTIAL - Some formatting missing")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_api_documentation():
    """Test Upgrade #2: REST API Documentation"""
    print_section("TEST 2: REST API Documentation")
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Check if Swagger UI is accessible
    print("\n📚 Test 2.1: Swagger UI Accessibility")
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        if response.status_code == 200:
            print("  ✅ Swagger UI accessible at /docs")
            tests_passed += 1
        else:
            print(f"  ❌ Swagger UI returned {response.status_code}")
    except Exception as e:
        print(f"  ❌ Cannot access Swagger UI: {e}")
    
    # Test 2: Check if ReDoc is accessible
    print("\n📖 Test 2.2: ReDoc Accessibility")
    try:
        response = requests.get("http://127.0.0.1:8000/redoc", timeout=5)
        if response.status_code == 200:
            print("  ✅ ReDoc accessible at /redoc")
            tests_passed += 1
        else:
            print(f"  ❌ ReDoc returned {response.status_code}")
    except Exception as e:
        print(f"  ❌ Cannot access ReDoc: {e}")
    
    # Test 3: Check OpenAPI schema
    print("\n🔧 Test 2.3: OpenAPI Schema Validation")
    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            
            # Check for key components
            has_info = "info" in schema
            has_paths = "paths" in schema
            has_components = "components" in schema
            
            print(f"  {'✅' if has_info else '❌'} API metadata present")
            print(f"  {'✅' if has_paths else '❌'} Endpoint definitions present")
            print(f"  {'✅' if has_components else '❌'} Schema models present")
            
            if has_info and has_paths and has_components:
                tests_passed += 1
        else:
            print(f"  ❌ OpenAPI schema returned {response.status_code}")
    except Exception as e:
        print(f"  ❌ Cannot access OpenAPI schema: {e}")
    
    # Test 4: Verify enhanced API title
    print("\n📋 Test 2.4: Enhanced API Metadata")
    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            info = schema.get("info", {})
            
            enhanced_title = "AI Rule Intelligence" in info.get("title", "")
            has_version = "version" in info
            has_contact = "contact" in info
            
            print(f"  {'✅' if enhanced_title else '❌'} Enhanced title present")
            print(f"  {'✅' if has_version else '❌'} Version information present")
            print(f"  {'✅' if has_contact else '❌'} Contact information present")
            
            if enhanced_title and has_version and has_contact:
                tests_passed += 1
    except Exception as e:
        print(f"  ❌ Cannot validate metadata: {e}")
    
    print(f"\n📊 API Documentation Tests: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("\n🎉 UPGRADE #2: PASSED - API documentation complete!")
        return True
    else:
        print(f"\n⚠️  UPGRADE #2: PARTIAL - {tests_passed}/{tests_total} checks passed")
        return False


def test_adaptive_feedback():
    """Test Upgrade #3: Adaptive Feedback Integration"""
    print_section("TEST 3: Adaptive Feedback Integration")
    
    # First, run a test case
    print("\n🔄 Step 1: Running test case...")
    test_case = {
        "project_id": "feedback_test_01",
        "case_id": "adaptive_feedback_test",
        "city": "Mumbai",
        "document": "Mumbai_DCPR_2034.pdf",
        "parameters": {
            "plot_size": 1500,
            "location": "urban",
            "road_width": 15
        }
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/run_case",
            json=test_case,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Case execution failed: {response.status_code}")
            return False
        
        result = response.json()
        print("  ✅ Test case executed successfully")
        
        # Submit positive feedback
        print("\n👍 Step 2: Submitting positive feedback...")
        
        feedback_data = {
            "project_id": result.get("project_id"),
            "case_id": result.get("case_id"),
            "input_case": test_case,
            "output_report": result,
            "user_feedback": "up",
            "selected_city": "Mumbai"
        }
        
        feedback_response = requests.post(
            "http://127.0.0.1:8000/feedback",
            json=feedback_data,
            timeout=10
        )
        
        if feedback_response.status_code != 200:
            print(f"  ❌ Feedback submission failed: {feedback_response.status_code}")
            return False
        
        feedback_result = feedback_response.json()
        print("  ✅ Feedback recorded successfully")
        
        # Check for adaptation summary
        if "adaptation_summary" in feedback_result:
            summary = feedback_result["adaptation_summary"]
            
            print("\n📊 Step 3: Validating adaptive response...")
            print(f"  Weights updated: {summary.get('weights_updated', False)}")
            print(f"  Approval rate: {summary.get('approval_rate', 0):.1%}")
            print(f"  Confidence adjustment: {summary.get('confidence_adjustment', 1.0):.2f}x")
            
            # Check audit trail
            if "audit_trail" in summary:
                print("\n📋 Audit Trail:")
                for entry in summary["audit_trail"][:5]:  # Show first 5
                    print(f"    {entry}")
                
                print("\n🎉 UPGRADE #3: PASSED - Adaptive feedback fully integrated!")
                return True
        
        print("\n⚠️  UPGRADE #3: PARTIAL - Feedback recorded but adaptation info missing")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_feedback_analytics_endpoint():
    """Test the new feedback analytics endpoint"""
    print_section("BONUS TEST: Feedback Analytics")
    
    print("\n📈 Testing feedback summary endpoint...")
    
    try:
        response = requests.get(
            "http://127.0.0.1:8000/get_feedback_summary",
            timeout=10
        )
        
        if response.status_code == 200:
            summary = response.json()
            
            print("\n📊 System-Wide Feedback Statistics:")
            print(f"  Total Feedback: {summary.get('total_feedback', 0)}")
            print(f"  Upvotes: {summary.get('upvotes', 0)}")
            print(f"  Downvotes: {summary.get('downvotes', 0)}")
            
            if summary.get('total_feedback', 0) > 0:
                approval = summary.get('upvotes', 0) / summary.get('total_feedback', 1)
                print(f"  Overall Approval: {approval:.1%}")
            
            print("\n✅ Feedback analytics endpoint working!")
            return True
        else:
            print(f"❌ Endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all upgrade tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "SYSTEM UPGRADE TEST SUITE" + " "*28 + "║")
    print("║" + " "*28 + "Version 8.5 → 10.0" + " "*33 + "║")
    print("╚" + "="*78 + "╝")
    
    print("\n⚠️  PREREQUISITES:")
    print("  1. Main API running on port 8000 (python main.py)")
    print("  2. Database populated with rules")
    print("  3. RL agent trained and available")
    
    input("\nPress ENTER to start tests...")
    
    results = {
        "Enhanced Reasoning": False,
        "API Documentation": False,
        "Adaptive Feedback": False,
        "Feedback Analytics": False
    }
    
    # Run all tests
    results["Enhanced Reasoning"] = test_enhanced_reasoning()
    time.sleep(1)
    
    results["API Documentation"] = test_api_documentation()
    time.sleep(1)
    
    results["Adaptive Feedback"] = test_adaptive_feedback()
    time.sleep(1)
    
    results["Feedback Analytics"] = test_feedback_analytics_endpoint()
    
    # Final summary
    print_section("FINAL RESULTS")
    
    print("\n📋 Test Summary:")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status} - {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 Overall Score: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL UPGRADES VERIFIED!")
        print("🏆 System Rating: 10/10")
        print("\n✨ Ready for production deployment!")
    elif total_passed >= 3:
        print(f"\n✅ Most upgrades verified ({total_passed}/{total_tests})")
        print("🎯 System Rating: 9.5/10")
    else:
        print(f"\n⚠️  Some upgrades need attention ({total_passed}/{total_tests})")
        print("📝 Please review failed tests above")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
