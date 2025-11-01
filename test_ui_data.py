import requests
import json

print("=" * 80)
print("Testing API Endpoints for Streamlit UI")
print("=" * 80)

# Test 1: Get projects from bridge API
print("\n1. Testing /api/design-bridge/projects...")
try:
    response = requests.get("http://127.0.0.1:8001/api/design-bridge/projects", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        projects = response.json().get("projects", [])
        print(f"   Found {len(projects)} projects")
        for p in projects:
            print(f"   - {p['project_id']}: {p['case_count']} cases")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Get cases for proj_skytower_01
print("\n2. Testing /projects/proj_skytower_01/cases...")
try:
    response = requests.get("http://127.0.0.1:8000/projects/proj_skytower_01/cases", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        cases = response.json()
        print(f"   Found {len(cases)} cases")
        for case in cases:
            print(f"   - {case.get('case_id')}: city={case.get('city', 'NOT SET')}")
            print(f"     Rules: {case.get('rules_applied', [])[:2]}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Get cities
print("\n3. Testing /api/design-bridge/cities...")
try:
    response = requests.get("http://127.0.0.1:8001/api/design-bridge/cities", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        cities = response.json().get("cities", [])
        print(f"   Found {len(cities)} cities")
        for city in cities:
            print(f"   - {city['name']}: {city['rule_count']} rules, {city['feedback_count']} feedback")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Check database directly
print("\n4. Checking database directly...")
try:
    from database_setup import SessionLocal, ReasoningOutput
    db = SessionLocal()
    cases = db.query(ReasoningOutput).all()
    print(f"   Total cases in DB: {len(cases)}")
    for case in cases:
        print(f"   - {case.case_id} ({case.project_id})")
        print(f"     Rules: {case.rules_applied[:2] if case.rules_applied else 'None'}")
    db.close()
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 80)
