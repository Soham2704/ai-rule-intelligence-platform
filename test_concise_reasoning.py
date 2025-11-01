import json
import requests

def test_concise_reasoning():
    """Test the updated concise reasoning"""
    
    # Test case data
    test_case = {
        'project_id': 'test_concise_01',
        'case_id': 'test_mumbai_concise',
        'city': 'Mumbai',
        'document': 'DCPR_2034.pdf',
        'parameters': {
            'plot_size': 2000,
            'location': 'urban',
            'road_width': 20
        }
    }
    
    print('Testing concise reasoning...')
    
    try:
        response = requests.post('http://127.0.0.1:8000/run_case', json=test_case, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print('\n' + '='*60)
            print('CONCISE REASONING TEST RESULT:')
            print('='*60)
            
            reasoning = result.get("reasoning", "N/A")
            print(f'Reasoning: {reasoning}')
            print(f'Length: {len(reasoning)} characters')
            
            # Calculate line count separately to avoid f-string backslash issue
            line_count = reasoning.count("\n") + 1
            print(f'Lines: {line_count}')
            
            print(f'Confidence: {result.get("confidence_level", "N/A")} ({result.get("confidence_score", 0):.1%})')
            print(f'Rules Applied: {len(result.get("rules_applied", []))}')
            
            print('='*60)
            
            # Check if it's actually concise (under 300 characters and max 3 lines)
            if len(reasoning) <= 300 and line_count <= 3:
                print('✅ SUCCESS: Reasoning is now concise!')
            else:
                print('⚠️  WARNING: Reasoning might still be too long')
                
        else:
            print(f'Error: {response.status_code}')
            print(response.text)
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test_concise_reasoning()