#!/usr/bin/env python3

import requests

def check_ui_data_flow():
    print('🔍 CHECKING ACTUAL UI DATA FLOW')
    print('=' * 50)

    # Check what cities are available
    print('1️⃣ Available cities:')
    try:
        response = requests.get('http://127.0.0.1:8001/api/design-bridge/cities')
        if response.status_code == 200:
            cities = response.json()
            for city in cities.get('cities', []):
                name = city.get('name', 'Unknown')
                rules = city.get('rule_count', 0)
                feedback = city.get('feedback_count', 0)
                print(f'   {name}: {rules} rules, {feedback} feedback')
        else:
            print(f'   Error: {response.status_code}')
    except Exception as e:
        print(f'   Error: {e}')

    # Check what projects exist
    print('\n2️⃣ Available projects:')
    try:
        response = requests.get('http://127.0.0.1:8001/api/design-bridge/projects')
        if response.status_code == 200:
            projects = response.json()
            for project in projects.get('projects', []):
                pid = project.get('project_id', 'Unknown')
                cases = project.get('case_count', 0)
                print(f'   {pid}: {cases} cases')
        else:
            print(f'   Error: {response.status_code}')
    except Exception as e:
        print(f'   Error: {e}')

    # Test the exact Mumbai stats call
    print('\n3️⃣ Testing Mumbai stats directly:')
    try:
        import time
        timestamp = int(time.time())
        response = requests.get(f'http://127.0.0.1:8001/api/design-bridge/feedback/city/Mumbai/stats?t={timestamp}')
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            stats = response.json()
            print('   Current Mumbai stats:')
            print(f'     Total: {stats.get("total_feedback", 0)}')
            print(f'     Upvotes: {stats.get("upvotes", 0)}')
            print(f'     Downvotes: {stats.get("downvotes", 0)}')
            print(f'     Approval: {stats.get("approval_rate", 0):.1f}%')
        else:
            print(f'   Error response: {response.text}')
    except Exception as e:
        print(f'   Error: {e}')

if __name__ == "__main__":
    check_ui_data_flow()