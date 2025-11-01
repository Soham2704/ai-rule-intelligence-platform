import json
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# --- Import our logger, the NEW MCP Client, and the pipeline logic ---
from logging_config import logger

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
        self.mcp_client: Optional['MCPClient'] = None
        self.llm = None
        self.rl_agent = None
        self.is_initialized = False

state = SystemState()

# Import these modules AFTER the app is defined to avoid circular imports
# Use try/except to handle missing optional dependencies gracefully
try:
    from mcp_client import MCPClient 
except ImportError as e:
    logger.warning(f"MCPClient import failed: {e}")
    MCPClient = None

try:
    from main_pipeline import process_case_logic
except ImportError as e:
    logger.warning(f"process_case_logic import failed: {e}")
    def process_case_logic(*args, **kwargs):
        raise HTTPException(status_code=501, detail="Processing pipeline not available")

try:
    from database_setup import Rule, Feedback, GeometryOutput
except ImportError as e:
    logger.warning(f"Database imports failed: {e}")
    Rule, Feedback, GeometryOutput = None, None, None

try:
    from adaptive_feedback_system import AdaptiveFeedbackSystem
except ImportError as e:
    logger.warning(f"AdaptiveFeedbackSystem import failed: {e}")
    class AdaptiveFeedbackSystem:
        def process_feedback(self, **kwargs):
            return {"status": "not_implemented"}

# --- 5. Server Startup & Shutdown Events ---
@app.on_event("startup")
def startup_event():
    """This function runs ONCE to initialize the MCP client and core AI models."""
    logger.info("Server starting up... Initializing MCP Client and AI models.")
    
    # Try to import AI models, but don't fail if they're not available
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from stable_baselines3 import PPO
    except ImportError as e:
        logger.warning(f"AI model imports failed: {e}")
        ChatGoogleGenerativeAI = None
        PPO = None

    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

    # We now create one instance of the MCP Client for the whole application
    if MCPClient:
        state.mcp_client = MCPClient()
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

@app.post("/feedback", summary="Submit feedback for a processed case with adaptive learning")
def feedback_endpoint(feedback: FeedbackInput):
    if not state.is_initialized: 
        raise HTTPException(status_code=503, detail="System is initializing.")
    try:
        # Save to MCP database
        if state.mcp_client:
            feedback_record = state.mcp_client.add_feedback(feedback.dict())
            logger.info(f"Feedback saved via MCP for case {feedback.case_id}")
        else:
            feedback_record = type('obj', (object,), {'id': 'temp_id'})()
            logger.warning("MCP client not available, using temporary feedback record")
        
        # Process with adaptive feedback system (NEW: Integration)
        try:
            adaptive_system = AdaptiveFeedbackSystem()
            
            adaptation_result = adaptive_system.process_feedback(
                case_id=feedback.case_id,
                project_id=feedback.project_id,
                city=feedback.input_case.get("city", "Unknown"),
                feedback_type=feedback.user_feedback,
                input_params=feedback.input_case,
                output_report=feedback.output_report
            )
            
            # Log audit trail
            logger.info(f"Adaptive feedback processed for {feedback.case_id}:")
            for trail_entry in adaptation_result.get("audit_trail", []):
                logger.info(f"  {trail_entry}")
            
            return {
                "status": "success",
                "feedback_id": feedback_record.id,
                "adaptation_summary": adaptation_result  # NEW: Include adaptation details
            }
            
        except Exception as e:
            logger.warning(f"Adaptive feedback processing failed: {e}")
            # Still return success if MCP save worked
            return {
                "status": "success",
                "feedback_id": feedback_record.id,
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
    if not state.mcp_client or not Feedback: raise HTTPException(status_code=501, detail="Database not available.")
    try:
        feedback_records = state.mcp_client.db.query(Feedback).filter(Feedback.case_id == case_id).all()
        return [
            {
                "feedback_id": record.id, "project_id": record.project_id,
                "feedback_type": record.feedback_type, "timestamp": record.timestamp
            } for record in feedback_records
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch feedback: {e}")

@app.get("/get_feedback_summary", summary="Returns aggregated thumbs up/down stats")
def get_feedback_summary():
    if not state.is_initialized: raise HTTPException(status_code=503, detail="System is initializing.")
    if not state.mcp_client or not Feedback: raise HTTPException(status_code=501, detail="Database not available.")
    try:
        summary = {"upvotes": 0, "downvotes": 0, "total_feedback": 0}
        feedback_records = state.mcp_client.db.query(Feedback).all()
        for record in feedback_records:
            if record.feedback_type == "up": summary["upvotes"] += 1
            elif record.feedback_type == "down": summary["downvotes"] += 1
        summary["total_feedback"] = len(feedback_records)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not process feedback from MCP.")

# Health check endpoint for deployment verification
@app.get("/health", summary="Health check endpoint")
def health_check():
    """Simple health check endpoint to verify the service is running."""
    return {"status": "healthy", "message": "AI Rule Intelligence Platform is running", "initialized": state.is_initialized}

# --- 7. Main execution block for running the server ---
if __name__ == "__main__":
    print("--- Starting MCP-Integrated API Server with Uvicorn ---")
    print("Access the interactive API docs at http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)