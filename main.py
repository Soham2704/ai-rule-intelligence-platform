from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import os
import json
import logging

from database_setup import SessionLocal, Rule, Feedback, GeometryOutput, ReasoningOutput
from mcp_client import MCPClient
from main_pipeline import process_case_logic
from populate_comprehensive_rules import populate_comprehensive_rules
from database_setup import create_database
from adaptive_feedback_system import AdaptiveFeedbackSystem

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. Create the FastAPI App with Enhanced Documentation ---
app = FastAPI(
    title="AI Rule Intelligence Platform API",
    description="""🏗️ **Multi-City Building Compliance & AI Reasoning System**

This API provides:
- 🧠 AI-powered building regulation analysis
- 🏙️ Multi-city support (Mumbai, Pune, Ahmedabad, Nashik)
- 📊 Confidence scoring with RL agents
- 🔄 Adaptive feedback learning
- 📐 3D geometry generation
- 🎯 Clause-level reasoning explanations

**Key Features:**
- Real-time rule matching from MCP database
- Gemini AI for contextual explanations
- PPO reinforcement learning for confidence scoring
- City-adaptive reward weights
- Comprehensive audit trails

**Documentation:**
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- API Guide: See endpoints below
    """,
    version="2.0.0",
    contact={
        "name": "AI Rule Intelligence Team",
        "email": "support@ai-rules.example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    terms_of_service="https://ai-rules.example.com/terms",
)

# --- 2. Add CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Data Models for API ---
class CaseParameters(BaseModel):
    plot_size: int
    location: str
    road_width: int

class CaseInput(BaseModel):
    project_id: str
    case_id: str
    city: str
    document: str
    parameters: CaseParameters

class FeedbackInput(BaseModel):
    project_id: str
    case_id: str
    input_case: Dict[str, Any]
    output_report: Dict[str, Any]
    user_feedback: str = Field(..., pattern="^(up|down)$")

# --- 4. Global State (Now much simpler) ---
class SystemState:
    def __init__(self):
        # Initialize database when the app starts
        print("=== Initializing database on app startup ===")
        self.initialize_database()
        
        # Initialize MCP client
        self.mcp_client: Optional[MCPClient] = None
        self.llm: Optional[Any] = None
        self.rl_agent: Optional[Any] = None
        self.is_initialized = False
    
    def initialize_database(self):
        """Initialize database and populate with rules."""
        try:
            print("Creating database...")
            create_database()
            
            # Check if rules exist, if not populate them
            db = SessionLocal()
            rule_count = db.query(Rule).count()
            print(f"Current rule count: {rule_count}")
            
            if rule_count == 0:
                print("Populating database with comprehensive rules...")
                populate_comprehensive_rules()
                new_count = db.query(Rule).count()
                print(f"Rules after population: {new_count}")
            else:
                print("Database already populated with rules")
                
            db.close()
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_rl_agent(self):
        """Load the RL agent if available."""
        try:
            from stable_baselines3 import PPO
            if os.path.exists("rl_env/ppo_hirl_agent.zip"):
                self.rl_agent = PPO.load("rl_env/ppo_hirl_agent.zip")
                print("RL agent loaded successfully")
            else:
                print("RL agent model file not found")
        except ImportError:
            print("Stable Baselines3 not installed, RL agent not available")
        except Exception as e:
            print(f"Error loading RL agent: {e}")

state = SystemState()

# --- 5. Server Startup & Shutdown Events ---
@app.on_event("startup")
def startup_event():
    """This function runs ONCE to initialize the MCP client and core AI models."""
    logger.info("Server starting up... Initializing MCP Client and AI models.")
    
    # Try to import AI models, but don't fail if they're not available
    ChatGoogleGenerativeAI = None
    PPO = None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from stable_baselines3 import PPO
    except ImportError as e:
        logger.warning(f"AI model imports failed: {e}")

    from dotenv import load_dotenv
    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY") or ""

    # We now create one instance of the MCP Client for the whole application
    if 'MCPClient' in globals():
        state.mcp_client = MCPClient()
        print("MCP client initialized in startup event")
    else:
        logger.warning("MCPClient not available")
    
    if ChatGoogleGenerativeAI:
        try:
            state.llm = ChatGoogleGenerativeAI(model="gemini-pro-latest")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM: {e}")
            state.llm = None
    else:
        state.llm = None
    
    # Try to load the RL agent, but don't fail if it's not available
    try:
        if PPO and os.path.exists("rl_env/ppo_hirl_agent.zip"):
            state.rl_agent = PPO.load("rl_env/ppo_hirl_agent.zip")
        else:
            logger.warning("RL Agent model file not found or PPO not available")
            state.rl_agent = None
    except Exception as e:
        logger.warning(f"Failed to load RL Agent: {e}")
        state.rl_agent = None
    
    state.is_initialized = True
    logger.info("Server initialization completed.")

@app.on_event("shutdown")
def shutdown_event():
    """This function runs ONCE to close connections."""
    if state.mcp_client:
        try:
            state.mcp_client.close()
        except Exception as e:
            logger.warning(f"Error closing MCP client: {e}")

# --- 6. API Endpoints (Now refactored to use MCP Client) ---

# Debug endpoint to check database status
@app.get("/debug/database")
def debug_database_status():
    """Debug endpoint to check database status."""
    try:
        # Check if database file exists
        from database_setup import DB_PATH
        db_exists = os.path.exists(DB_PATH)
        db_size = os.path.getsize(DB_PATH) if db_exists else 0
        
        # Check rules count
        if state.mcp_client:
            db = state.mcp_client.db
            total_rules = db.query(Rule).count() if Rule else 0
            mumbai_rules = db.query(Rule).filter(Rule.city == "Mumbai").count() if Rule else 0
            
            # Get sample rules
            sample_rules = []
            if Rule and total_rules > 0:
                rules = db.query(Rule).filter(Rule.city == "Mumbai").limit(5).all()
                if rules:
                    sample_rules = [{"id": r.id, "type": r.rule_type, "conditions": r.conditions} for r in rules]
            
            return {
                "database_exists": db_exists,
                "database_size_bytes": db_size,
                "total_rules": total_rules,
                "mumbai_rules": mumbai_rules,
                "sample_rules": sample_rules
            }
        else:
            return {"error": "MCP client not initialized"}
    except Exception as e:
        return {"error": str(e)}

# Root endpoint
@app.get("/", summary="API Root")
def root():
    """Root endpoint with API information and available endpoints."""
    return {
        "message": "AI Rule Intelligence Platform API",
        "version": "2.0.0",
        "description": "Multi-City Building Compliance & AI Reasoning System",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "run_case": "POST /run_case",
            "get_project_cases": "GET /projects/{project_id}/cases",
            "submit_feedback": "POST /feedback",
            "get_rules_by_city": "GET /rules/{city}",
            "get_case_logs": "GET /logs/{case_id}",
            "get_geometry": "GET /geometry/{project_id}/{case_id}",
            "get_feedback_by_case": "GET /feedback/{case_id}",
            "get_feedback_summary": "GET /get_feedback_summary",
            "health_check": "GET /health"
        }
    }

@app.post("/run_case", summary="Run the full compliance pipeline for a single case")
def run_case_endpoint(case_input: CaseInput):
    if not state.is_initialized:
        raise HTTPException(status_code=503, detail="System is initializing.")
    try:
        # The pipeline logic now receives the state object which contains the MCP client
        return process_case_logic(case_input.dict(), state)
    except Exception as e:
        logger.error(f"Error in /run_case: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/cases", summary="Get all case results for a specific project")
def get_project_cases(project_id: str) -> List[Dict[str, Any]]:
    project_dir = f"outputs/projects/{project_id}"
    if not os.path.exists(project_dir):
        return []
    project_reports = []
    try:
        for filename in os.listdir(project_dir):
            if filename.endswith("_report.json"):
                with open(os.path.join(project_dir, filename), 'r') as f:
                    project_reports.append(json.load(f))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading project reports: {e}")
    return project_reports

@app.post("/feedback", summary="Save user feedback and trigger adaptive learning")
def save_feedback(feedback: FeedbackInput):
    if not state.is_initialized: raise HTTPException(status_code=503, detail="System is initializing.")
    if not state.mcp_client: raise HTTPException(status_code=501, detail="MCP Client not available.")
    
    try:
        # Save feedback to MCP
        feedback_data = {
            "case_id": feedback.case_id,
            "project_id": feedback.project_id,
            "input_case": feedback.input_case,
            "output_report": feedback.output_report,
            "user_feedback": feedback.user_feedback
        }
        feedback_record = state.mcp_client.add_feedback(feedback_data)
        
        try:
            # Trigger adaptive feedback learning (NEW)
            adaptive_system = AdaptiveFeedbackSystem()
            adaptation_result = adaptive_system.process_feedback(
                case_id=feedback.case_id,
                project_id=feedback.project_id,
                city=feedback.input_case.get("city", "Unknown"),
                feedback_type=feedback.user_feedback,
                input_params=feedback.input_case,
                output_report=feedback.output_report
            )
            adaptive_system.close()
            
            # Return success with adaptation details
            return {
                "status": "success",
                "feedback_id": getattr(feedback_record, 'id', 'unknown'),
                "adaptation_summary": adaptation_result  # NEW: Include adaptation details
            }
            
        except Exception as e:
            logger.warning(f"Adaptive feedback processing failed: {e}")
            # Still return success if MCP save worked
            return {
                "status": "success",
                "feedback_id": getattr(feedback_record, 'id', 'unknown'),
                "adaptation_summary": None,
                "note": "Feedback saved but adaptive processing unavailable"
            }
            
    except Exception as e:
        logger.error(f"Error in /feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not save feedback.")

@app.get("/logs/{case_id}", summary="Get all agent logs for a specific case_id")
def logs_endpoint(case_id: str) -> List[Dict[str, Any]]:
    log_file = "reports/agent_log.jsonl"
    case_logs = []
    if not os.path.exists(log_file): raise HTTPException(status_code=404, detail="Log file not found.")
    try:
        with open(log_file, 'r') as f:
            for line in f:
                log_entry = json.loads(line)
                if log_entry.get('extra_data', {}).get('case', {}).get('case_id') == case_id:
                    case_logs.append(log_entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {e}")
    return case_logs

@app.get("/rules/{city}", summary="Fetch all structured rules from MCP for a given city")
def get_rules_by_city(city: str) -> List[Dict[str, Any]]:
    if not state.is_initialized: raise HTTPException(status_code=503, detail="System is initializing.")
    if not state.mcp_client or not Rule: raise HTTPException(status_code=501, detail="Database not available.")
    try:
        rules_from_db = state.mcp_client.db.query(Rule).filter(Rule.city.ilike(city)).all()
        return [
            {
                "id": rule.id, "city": rule.city, "rule_type": rule.rule_type,
                "conditions": rule.conditions, "entitlements": rule.entitlements,
                "notes": rule.notes, "authority": rule.authority, 
                "clause_no": rule.clause_no, "page": rule.page
            } for rule in rules_from_db
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch rules: {e}")

@app.get("/geometry/{project_id}/{case_id}", summary="Serves the generated STL geometry file for a case")
def get_geometry(project_id: str, case_id: str):
    file_path = f"outputs/projects/{project_id}/{case_id}_geometry.stl"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Geometry file not found.")
    return FileResponse(file_path, media_type='application/vnd.ms-pki.stl', filename=f"{case_id}.stl")

@app.get("/feedback/{case_id}", summary="Fetch thumbs data for a given case_id")
def get_feedback_by_case(case_id: str) -> List[Dict[str, Any]]:
    if not state.is_initialized: raise HTTPException(status_code=503, detail="System is initializing.")
    if not state.mcp_client: raise HTTPException(status_code=501, detail="Database not available.")
    try:
        feedback_records = state.mcp_client.db.query(Feedback).filter(Feedback.case_id == case_id).all()
        return [
            {
                "feedback_id": getattr(record, 'id', 'unknown'),
                "project_id": getattr(record, 'project_id', ''),
                "feedback_type": getattr(record, 'feedback_type', ''),
                "timestamp": getattr(record, 'timestamp', '')
            } for record in feedback_records
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch feedback: {e}")

@app.get("/get_feedback_summary", summary="Returns aggregated thumbs up/down stats")
def get_feedback_summary():
    if not state.is_initialized: raise HTTPException(status_code=503, detail="System is initializing.")
    if not state.mcp_client: raise HTTPException(status_code=501, detail="Database not available.")
    try:
        summary = {"upvotes": 0, "downvotes": 0, "total_feedback": 0}
        feedback_records = state.mcp_client.db.query(Feedback).all()
        for record in feedback_records:
            feedback_type = getattr(record, 'feedback_type', '')
            if feedback_type == "up": 
                summary["upvotes"] += 1
            elif feedback_type == "down": 
                summary["downvotes"] += 1
        summary["total_feedback"] = len(feedback_records)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not process feedback from MCP.")

@app.get("/reasoning/{case_id}", summary="Get reasoning output for a specific case")
def get_reasoning_by_case(case_id: str) -> Dict[str, Any]:
    """Get reasoning output for a specific case from the database."""
    if not state.is_initialized: raise HTTPException(status_code=503, detail="System is initializing.")
    if not state.mcp_client: raise HTTPException(status_code=501, detail="Database not available.")
    try:
        # Try to get from ReasoningOutput table
        reasoning_record = state.mcp_client.db.query(ReasoningOutput).filter(ReasoningOutput.case_id == case_id).first()
        if reasoning_record:
            return {
                "case_id": getattr(reasoning_record, 'case_id', ''),
                "project_id": getattr(reasoning_record, 'project_id', ''),
                "rules_applied": getattr(reasoning_record, 'rules_applied', []),
                "reasoning": getattr(reasoning_record, 'reasoning_summary', ''),
                "clause_summaries": getattr(reasoning_record, 'clause_summaries', []),
                "confidence_score": getattr(reasoning_record, 'confidence_score', 0.0),
                "confidence_level": getattr(reasoning_record, 'confidence_level', ''),
                "confidence_note": getattr(reasoning_record, 'confidence_note', ''),
                "timestamp": getattr(reasoning_record, 'timestamp', '')
            }
        
        # Fallback: try to get from JSON files
        projects_dir = "outputs/projects"
        if os.path.exists(projects_dir):
            for project_id in os.listdir(projects_dir):
                project_path = os.path.join(projects_dir, project_id)
                if os.path.isdir(project_path):
                    report_file = os.path.join(project_path, f"{case_id}_report.json")
                    if os.path.exists(report_file):
                        with open(report_file, 'r') as f:
                            return json.load(f)
        
        raise HTTPException(status_code=404, detail=f"Reasoning data not found for case: {case_id}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reasoning data: {e}")

# Health check endpoint for deployment verification
@app.get("/health", summary="Health check endpoint")
def health_check():
    """Simple health check endpoint to verify the service is running."""
    return {"status": "healthy", "message": "AI Rule Intelligence Platform is running", "initialized": state.is_initialized}

@app.get("/projects", summary="Get all projects")
def get_all_projects() -> List[Dict[str, Any]]:
    """Get list of all projects with metadata."""
    try:
        # Get all unique project IDs from the outputs directory
        projects_dir = "outputs/projects"
        if not os.path.exists(projects_dir):
            return []
        
        project_list = []
        for project_id in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_id)
            if os.path.isdir(project_path):
                # Count cases in this project
                case_count = 0
                latest_case = None
                latest_timestamp = None
                
                try:
                    for filename in os.listdir(project_path):
                        if filename.endswith("_report.json"):
                            case_count += 1
                            # Try to get timestamp from file
                            file_timestamp = os.path.getmtime(os.path.join(project_path, filename))
                            if latest_timestamp is None or file_timestamp > latest_timestamp:
                                latest_timestamp = file_timestamp
                                # Extract case_id from filename
                                case_id = filename.replace("_report.json", "")
                                latest_case = case_id
                except Exception:
                    pass
                
                project_list.append({
                    "project_id": project_id,
                    "case_count": case_count,
                    "latest_case_id": latest_case,
                    "last_updated": datetime.fromtimestamp(latest_timestamp).isoformat() + "Z" if latest_timestamp else None
                })
        
        return project_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {e}")

# --- 7. Main execution block for running the server ---
if __name__ == "__main__":
    import uvicorn
    print("--- Starting MCP-Integrated API Server with Uvicorn ---")
    print("Access the interactive API docs at http://127.0.0.1:8000/docs")
    # Use 0.0.0.0 for Render deployment, 127.0.0.1 for local testing
    host = "0.0.0.0" if os.getenv("RENDER") else "127.0.0.1"
    uvicorn.run("main:app", host=host, port=8000, reload=False)
