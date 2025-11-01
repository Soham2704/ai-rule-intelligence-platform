"""
Simplified Case Feedback UI
----------------------------
A focused Streamlit interface for:
1. Selecting existing cases by city
2. Viewing concise AI reasoning (2-3 lines)
3. Providing upvote/downvote feedback
4. Storing feedback in MCP for RL training
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime

# Configuration - Support environment variables for deployment
MAIN_API_URL = os.getenv("MAIN_API_URL", "http://127.0.0.1:8000")
BRIDGE_API_URL = os.getenv("BRIDGE_API_URL", "http://127.0.0.1:8001/api/design-bridge")

# Page Configuration
st.set_page_config(
    page_title="AI Rule Intelligence - Case Feedback",
    page_icon="🏗️",
    layout="centered"
)

# Custom CSS for better button styling
st.markdown("""
<style>
    .feedback-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 20px 0;
    }
    .stButton > button {
        width: 150px;
        height: 50px;
        font-size: 18px;
    }
    .upvote-button {
        background-color: #28a745 !important;
        color: white !important;
    }
    .downvote-button {
        background-color: #dc3545 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def get_cities():
    """Fetch available cities from the bridge API"""
    # Return only the three main supported cities
    return ["Mumbai", "Pune", "Ahmedabad"]

def get_cases_by_city(city):
    """Get all processed cases for a specific city from reasoning outputs"""
    try:
        # Get all projects first
        projects_response = requests.get(f"{BRIDGE_API_URL}/projects", timeout=5)
        if projects_response.status_code != 200:
            return []
        
        projects = projects_response.json().get("projects", [])
        cases = []
        
        # For each project, get cases and filter by city
        for project in projects:
            project_id = project["project_id"]
            try:
                cases_response = requests.get(f"{MAIN_API_URL}/projects/{project_id}/cases", timeout=5)
                if cases_response.status_code == 200:
                    project_cases = cases_response.json()
                    # Filter cases by city
                    for case in project_cases:
                        case_city = case.get("city", "")
                        # Direct match
                        if case_city and case_city.lower() == city.lower():
                            cases.append(case)
                        # Fallback: try to infer from case_id or rules if city field is missing
                        elif not case_city:
                            case_id = case.get("case_id", "")
                            if city.lower() in case_id.lower():
                                case["city"] = city
                                cases.append(case)
                            elif case.get("rules_applied"):
                                first_rule = case["rules_applied"][0] if case["rules_applied"] else ""
                                city_prefix_map = {
                                    "mumbai": "MUM-",
                                    "pune": "PUNE-",
                                    "ahmedabad": "AMD-",
                                    "nashik": "NSK-"
                                }
                                prefix = city_prefix_map.get(city.lower())
                                if prefix and first_rule.startswith(prefix):
                                    case["city"] = city
                                    cases.append(case)
            except Exception as e:
                continue
        
        return cases
    except Exception as e:
        return []

def get_case_reasoning(case_id):
    """Get reasoning output for a specific case"""
    try:
        response = requests.get(f"{BRIDGE_API_URL}/reasoning/{case_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def submit_feedback(case_data, feedback_type, selected_city=None):
    """Submit feedback to the main API"""
    try:
        # Get city from multiple sources - prioritize selected_city from UI
        city = selected_city or case_data.get("city") or "unknown"
        
        feedback_payload = {
            "project_id": case_data.get("project_id", "unknown"),
            "case_id": case_data.get("case_id", "unknown"),
            "input_case": {
                "city": city,  # Use the properly determined city
                "parameters": case_data.get("parameters", {})
            },
            "output_report": case_data,
            "user_feedback": feedback_type
        }
        
        response = requests.post(f"{MAIN_API_URL}/feedback", json=feedback_payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

# Initialize session state for feedback tracking
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "refresh_stats" not in st.session_state:
    st.session_state.refresh_stats = 0

# Main UI
st.title("🏗️ AI Rule Intelligence - Case Feedback")
st.markdown("### Review AI reasoning and provide feedback to improve the system")

# City Selection
st.markdown("---")
st.subheader("📍 Select City")

cities = get_cities()
if not cities:
    st.error("Could not load cities. Please ensure the APIs are running.")
    st.stop()

selected_city = st.selectbox("Choose a city to view cases:", cities, key="city_selector")

if selected_city:
    # Load cases for selected city
    with st.spinner(f"Loading cases for {selected_city}..."):
        cases = get_cases_by_city(selected_city)
    
    if not cases:
        st.warning(f"No processed cases found for {selected_city}. Try running some cases first using the main API.")
        
        # Show example of how to create cases
        with st.expander("ℹ️ How to create test cases"):
            st.code("""
# Example: Create a test case
import requests

test_case = {
    "project_id": "test_feedback_01",
    "case_id": "mumbai_feedback_001",
    "city": "Mumbai",
    "document": "DCPR_2034.pdf",
    "parameters": {
        "plot_size": 1500,
        "location": "urban",
        "road_width": 18
    }
}

response = requests.post('http://127.0.0.1:8000/run_case', json=test_case)
print(response.json())
            """)
        st.stop()
    
    st.success(f"Found {len(cases)} case(s) for {selected_city}")
    
    # Case Selection
    st.markdown("---")
    st.subheader("📋 Select Case")
    
    case_options = {}
    for case in cases:
        case_id = case.get("case_id", "Unknown")
        project_id = case.get("project_id", "Unknown")
        confidence = case.get("confidence_score", 0)
        display_name = f"{case_id} ({project_id}) - Confidence: {confidence:.1%}"
        case_options[display_name] = case
    
    selected_case_display = st.selectbox("Choose a case to review:", list(case_options.keys()), key="case_selector")
    
    if selected_case_display:
        selected_case = case_options[selected_case_display]
        case_id = selected_case.get("case_id")
        
        # Get detailed reasoning
        with st.spinner("Loading case details..."):
            reasoning_data = get_case_reasoning(case_id)
        
        if not reasoning_data:
            # Fallback to basic case data
            reasoning_data = selected_case
        
        # Display Case Information
        st.markdown("---")
        st.subheader(f"🔍 Case Analysis: {case_id}")
        
        # Case Parameters
        col1, col2, col3 = st.columns(3)
        
        # Try to get parameters from various sources
        params = reasoning_data.get("parameters") or selected_case.get("parameters") or {}
        
        with col1:
            st.metric("Plot Size", f"{params.get('plot_size', 'N/A')} sqm")
        with col2:
            st.metric("Location", params.get('location', 'N/A').title())
        with col3:
            st.metric("Road Width", f"{params.get('road_width', 'N/A')} m")
        
        # AI Reasoning (Concise)
        st.markdown("### 🧠 AI Reasoning")
        reasoning_text = reasoning_data.get("reasoning") or selected_case.get("reasoning", "No reasoning available")
        
        # Display reasoning in a nice box
        st.info(reasoning_text)
        
        # Confidence Information
        col1, col2 = st.columns(2)
        with col1:
            confidence_score = reasoning_data.get("confidence_score") or selected_case.get("confidence_score", 0)
            st.metric("Confidence Score", f"{confidence_score:.1%}")
        
        with col2:
            confidence_level = reasoning_data.get("confidence_level") or selected_case.get("confidence_level", "Unknown")
            if confidence_level == "High":
                st.success(f"Confidence: {confidence_level}")
            elif confidence_level == "Moderate":
                st.warning(f"Confidence: {confidence_level}")
            else:
                st.error(f"Confidence: {confidence_level}")
        
        # Rules Applied
        rules_applied = reasoning_data.get("rules_applied") or selected_case.get("rules_applied", [])
        if rules_applied:
            st.markdown(f"**Rules Applied:** {', '.join(rules_applied)}")
        
        # Feedback Section
        st.markdown("---")
        st.subheader("👥 Your Feedback")
        st.markdown("Was this AI analysis helpful and accurate?")
        
        # Create feedback buttons in columns
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("👍 Helpful (Upvote)", key="upvote_btn", help="This analysis was accurate and helpful"):
                if submit_feedback(reasoning_data, "up", selected_city):
                    st.success("✅ Thank you! Your upvote has been recorded.")
                    st.balloons()
                    # Update session state to trigger stats refresh
                    st.session_state.feedback_submitted = True
                    st.session_state.refresh_stats += 1
                else:
                    st.error("❌ Failed to record feedback. Please try again.")
        
        with col3:
            if st.button("👎 Not Helpful (Downvote)", key="downvote_btn", help="This analysis was inaccurate or not helpful"):
                if submit_feedback(reasoning_data, "down", selected_city):
                    st.success("✅ Thank you! Your feedback has been recorded.")
                    # Update session state to trigger stats refresh
                    st.session_state.feedback_submitted = True
                    st.session_state.refresh_stats += 1
                else:
                    st.error("❌ Failed to record feedback. Please try again.")
        
        # Feedback Statistics (if available)
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("📊 Feedback Statistics")
        with col2:
            if st.button("🔄 Refresh Stats", help="Refresh feedback statistics"):
                st.session_state.refresh_stats += 1
        
        # Load stats with timestamp to prevent caching
        import time
        import random
        cache_buster = f"{int(time.time())}{random.randint(1000,9999)}"
        
        try:
            stats_url = f"{BRIDGE_API_URL}/feedback/city/{selected_city}/stats"
            # Add multiple cache-busting parameters
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache', 
                'Expires': '0'
            }
            stats_response = requests.get(
                stats_url, 
                timeout=5, 
                headers=headers,
                params={'t': cache_buster, 'refresh': st.session_state.refresh_stats}
            )
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                
                # Show debug info
                st.caption(f"🔄 Last refreshed: {time.strftime('%H:%M:%S')} | Request ID: {cache_buster}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Feedback", stats.get("total_feedback", 0))
                with col2:
                    st.metric("Approval Rate", f"{stats.get('approval_rate', 0):.1f}%")
                with col3:
                    st.metric("Upvotes", stats.get("upvotes", 0))
                with col4:
                    st.metric("Downvotes", stats.get("downvotes", 0))
                    
                # Show feedback submission status
                if st.session_state.feedback_submitted:
                    st.success("✅ Your feedback was recorded! Numbers updated above.")
                    st.session_state.feedback_submitted = False  # Reset flag
                    
                # Show last update info
                st.caption("🕰️ Stats update in real-time. Click 'Refresh Stats' above if numbers don't reflect your recent feedback.")
            else:
                st.info(f"No feedback statistics available yet. Submit some feedback first! (Status: {stats_response.status_code})")
        except Exception as e:
            st.error(f"Could not load feedback statistics. The API might be temporarily unavailable. Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
**💡 How it works:**
1. Select a city to view processed cases
2. Choose a specific case to review
3. Read the AI's concise reasoning (2-3 lines)
4. Vote on whether the analysis was helpful
5. Your feedback is stored and will improve future AI recommendations

**🔧 For developers:** This feedback data is automatically integrated into the RL agent training pipeline.
""")
