import sys
import os

# This is the same professional pathing fix from our other scripts
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_client import MCPClient

def run_test():
    print("\n--- Starting Database Connection Test ---")
    
    # We will create a new, clean connection to the database.
    mcp = MCPClient()
    
    city_to_check = "Mumbai"
    print(f"Querying the MCP for feedback for city: '{city_to_check}'...")
    
    # Get the feedback records
    feedback_records = mcp.get_feedback_by_city(city_to_check)
    
    num_found = len(feedback_records)
    print(f"Found {num_found} feedback records for {city_to_check}.")
    
    if num_found > 0:
        print("\nSUCCESS: The script can successfully see the feedback in the database.")
        for record in feedback_records:
            print(f"  - Found Feedback ID: {record.id}, Type: {record.feedback_type}")
    else:
        print("\nFAILURE: The script could not find any feedback for this city in the database.")
        print("This confirms there is a resource conflict or a data saving issue.")
        
    mcp.close()
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    run_test()

    
