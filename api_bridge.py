"""
AI Design Platform Bridge API
-------------------------------
This module provides REST API endpoints specifically designed for integration
with the AI Design Platform front-end (Yash, Nipun, Bhavesh, Anmol).

It exposes:
- Rule summaries by city
- Geometry file paths and metadata
- Feedback data with confidence scores
- Reasoning outputs for visualization
"""

from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os

from database_setup import SessionLocal, Rule, Feedback, GeometryOutput, ReasoningOutput
from mcp_client import MCPClient

# Main API URL - support environment variable for deployment
MAIN_API_URL = os.getenv("MAIN_API_URL", "http://127.0.0.1:8000")

# Initialize MCP Client
mcp_client = MCPClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    if mcp_client:
        mcp_client.close()

# Create the Design Bridge API
app = FastAPI(
    title="AI Design Platform Bridge API",
    description="REST API bridge connecting MCP backend with AI Design Platform frontend",
    version="2.0.0",
    docs_url="/api/design-bridge/docs",
    redoc_url="/api/design-bridge/redoc",
    lifespan=lifespan
)

# CORS Configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP Client
mcp_client = MCPClient()


# ============================================================================
# DATA MODELS
# ============================================================================

class RuleSummary(BaseModel):
    """Structured rule summary for frontend display"""
    id: str
    city: str
    rule_type: str
    clause_no: str
    authority: str
    entitlements: Dict[str, Any]
    conditions: Dict[str, Any]
    notes: str
    quick_summary: str


class GeometryInfo(BaseModel):
    """Geometry file information"""
    case_id: str
    project_id: str
    stl_path: str
    file_exists: bool
    file_size_kb: Optional[float]
    timestamp: str


class FeedbackSummary(BaseModel):
    """Feedback summary with city-specific stats"""
    case_id: str
    project_id: str
    city: str
    feedback_type: str  # "up" or "down"
    timestamp: str


class CityFeedbackStats(BaseModel):
    """Aggregated feedback statistics by city"""
    city: str
    total_feedback: int
    upvotes: int
    downvotes: int
    approval_rate: float
    confidence_avg: Optional[float]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Root endpoint with API information and available endpoints."""
    return JSONResponse(content={
        "message": "AI Design Platform Bridge API",
        "version": "2.0.0",
        "description": "REST API bridge connecting MCP backend with AI Design Platform frontend",
        "documentation": {
            "swagger": "/api/design-bridge/docs",
            "redoc": "/api/design-bridge/redoc"
        },
        "endpoints": {
            "health_check": "GET /api/design-bridge/health",
            "get_rules_by_city": "GET /api/design-bridge/rules/{city}",
            "get_geometry_info": "GET /api/design-bridge/geometry/{case_id}",
            "download_geometry": "GET /api/design-bridge/geometry/{case_id}/download",
            "get_feedback_by_case": "GET /api/design-bridge/feedback/{case_id}",
            "get_city_feedback_stats": "GET /api/design-bridge/feedback/city/{city}/stats",
            "get_reasoning_output": "GET /api/design-bridge/reasoning/{case_id}",
            "get_available_cities": "GET /api/design-bridge/cities",
            "get_all_projects": "GET /api/design-bridge/projects"
        }
    })


@app.get("/api/design-bridge/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Design Platform Bridge",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/api/design-bridge/rules/{city}", response_model=List[Dict[str, Any]])
def get_rules_by_city(city: str):
    """
    Fetch all summarized rules from MCP for a specific city.
    
    **Use Case:** Frontend displays available regulations for a selected city
    
    **Example:** GET /api/design-bridge/rules/Mumbai
    """
    try:
        db = SessionLocal()
        rules = db.query(Rule).filter(Rule.city.ilike(city)).all()
        
        if not rules:
            raise HTTPException(
                status_code=404, 
                detail=f"No rules found for city: {city}"
            )
        
        # Convert to structured summaries
        rule_summaries = []
        for rule in rules:
            # Extract values from SQLAlchemy model
            rule_id = str(rule.id)
            rule_city = str(rule.city)
            rule_type = str(rule.rule_type)
            clause_no = str(rule.clause_no) if rule.clause_no is not None else "N/A"
            authority = str(rule.authority) if rule.authority is not None else "N/A"
            entitlements = rule.entitlements or {}
            conditions = rule.conditions or {}
            notes = str(rule.notes) if rule.notes is not None else ""
            
            # Generate quick summary
            summary_parts = []
            if "total_fsi" in entitlements:
                summary_parts.append(f"FSI: {entitlements['total_fsi']}")
            if "max_height_m" in entitlements:
                summary_parts.append(f"Height: {entitlements['max_height_m']}m")
            if "ground_coverage_percent" in entitlements:
                summary_parts.append(f"Coverage: {entitlements['ground_coverage_percent']}%")
            
            rule_summaries.append({
                "id": rule_id,
                "city": rule_city,
                "rule_type": rule_type,
                "clause_no": clause_no,
                "authority": authority,
                "entitlements": entitlements,
                "conditions": conditions,
                "notes": notes,
                "quick_summary": ", ".join(summary_parts) if summary_parts else "See entitlements"
            })
        
        db.close()
        return rule_summaries
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rules: {str(e)}")


@app.get("/api/design-bridge/geometry/{case_id}", response_model=GeometryInfo)
def get_geometry_info(case_id: str):
    """
    Fetch geometry file path and metadata for a specific case.
    
    **Use Case:** Frontend retrieves 3D model path for visualization
    
    **Example:** GET /api/design-bridge/geometry/mumbai_001
    """
    try:
        db = SessionLocal()
        geometry = db.query(GeometryOutput).filter(GeometryOutput.case_id == case_id).first()
        
        if not geometry:
            raise HTTPException(
                status_code=404,
                detail=f"No geometry found for case_id: {case_id}"
            )
        
        # Extract values from SQLAlchemy model
        stl_path = str(geometry.stl_path)
        case_id_val = str(geometry.case_id)
        project_id_val = str(geometry.project_id)
        timestamp_val = str(geometry.timestamp)
        
        # Check if file exists and get size
        file_exists = os.path.exists(stl_path)
        file_size_kb = None
        if file_exists:
            file_size_kb = os.path.getsize(stl_path) / 1024
        
        db.close()
        
        return GeometryInfo(
            case_id=case_id_val,
            project_id=project_id_val,
            stl_path=stl_path,
            file_exists=file_exists,
            file_size_kb=round(file_size_kb, 2) if file_size_kb else None,
            timestamp=timestamp_val
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching geometry: {str(e)}")


@app.get("/api/design-bridge/geometry/{case_id}/download")
def download_geometry(case_id: str):
    """
    Download the actual STL geometry file.
    
    **Use Case:** Frontend downloads 3D model for rendering
    
    **Example:** GET /api/design-bridge/geometry/mumbai_001/download
    """
    try:
        db = SessionLocal()
        geometry = db.query(GeometryOutput).filter(GeometryOutput.case_id == case_id).first()
        
        if not geometry:
            raise HTTPException(
                status_code=404,
                detail=f"No geometry found for case_id: {case_id}"
            )
        
        # Extract value from SQLAlchemy model
        stl_path = str(geometry.stl_path)
        
        if not os.path.exists(stl_path):
            raise HTTPException(
                status_code=404,
                detail=f"Geometry file not found on disk: {stl_path}"
            )
        
        db.close()
        
        return FileResponse(
            path=stl_path,
            media_type="application/vnd.ms-pki.stl",
            filename=f"{case_id}_geometry.stl"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading geometry: {str(e)}")


@app.get("/api/design-bridge/feedback/{case_id}", response_model=List[FeedbackSummary])
def get_feedback_by_case(case_id: str):
    """
    Fetch all feedback entries for a specific case.
    
    **Use Case:** Frontend displays user feedback history
    
    **Example:** GET /api/design-bridge/feedback/mumbai_001
    """
    try:
        db = SessionLocal()
        feedback_records = db.query(Feedback).filter(Feedback.case_id == case_id).all()
        
        if not feedback_records:
            return []  # Empty list, not an error
        
        feedback_list = []
        for fb in feedback_records:
            # Extract values from SQLAlchemy model
            feedback_list.append(FeedbackSummary(
                case_id=str(fb.case_id),
                project_id=str(fb.project_id),
                city=str(fb.city),
                feedback_type=str(fb.feedback_type),
                timestamp=str(fb.timestamp)
            ))
        
        db.close()
        return feedback_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feedback: {str(e)}")


@app.get("/api/design-bridge/feedback/city/{city}/stats", response_model=CityFeedbackStats)
def get_city_feedback_stats(city: str):
    """
    Get aggregated feedback statistics for a specific city.
    
    **Use Case:** Frontend displays city-specific approval rates and confidence
    
    **Example:** GET /api/design-bridge/feedback/city/Mumbai/stats
    """
    try:
        db = SessionLocal()
        
        # Get all feedback for the city
        feedback_records = db.query(Feedback).filter(Feedback.city.ilike(city)).all()
        
        if not feedback_records:
            raise HTTPException(
                status_code=404,
                detail=f"No feedback data found for city: {city}"
            )
        
        # Calculate statistics
        total = len(feedback_records)
        upvotes = sum(1 for fb in feedback_records if str(fb.feedback_type) == "up")
        downvotes = sum(1 for fb in feedback_records if str(fb.feedback_type) == "down")
        approval_rate = (upvotes / total * 100) if total > 0 else 0
        
        # Get average confidence from reasoning outputs
        reasoning_records = db.query(ReasoningOutput).join(
            Feedback, ReasoningOutput.case_id == Feedback.case_id
        ).filter(Feedback.city.ilike(city)).all()
        
        confidence_avg = None
        if reasoning_records:
            confidences = [float(str(r.confidence_score)) for r in reasoning_records if r.confidence_score is not None]
            confidence_avg = sum(confidences) / len(confidences) if confidences else None
        
        db.close()
        
        return CityFeedbackStats(
            city=city,
            total_feedback=total,
            upvotes=upvotes,
            downvotes=downvotes,
            approval_rate=round(float(approval_rate), 2),
            confidence_avg=round(float(confidence_avg), 3) if confidence_avg is not None else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")


@app.get("/api/design-bridge/reasoning/{case_id}")
def get_reasoning_output(case_id: str):
    """
    Fetch the complete AI reasoning output for a case.
    
    **Use Case:** Frontend displays detailed rule explanations with confidence
    
    **Example:** GET /api/design-bridge/reasoning/mumbai_001
    """
    try:
        db = SessionLocal()
        reasoning = db.query(ReasoningOutput).filter(ReasoningOutput.case_id == case_id).first()
        
        if not reasoning:
            raise HTTPException(
                status_code=404,
                detail=f"No reasoning output found for case_id: {case_id}"
            )
        
        # Extract values from SQLAlchemy model
        result = {
            "case_id": str(reasoning.case_id),
            "project_id": str(reasoning.project_id),
            "rules_applied": reasoning.rules_applied,
            "reasoning": str(reasoning.reasoning_summary),
            "clause_summaries": reasoning.clause_summaries,
            "confidence_score": float(str(reasoning.confidence_score)) if reasoning.confidence_score is not None else None,
            "confidence_level": str(reasoning.confidence_level) if reasoning.confidence_level is not None else None,
            "confidence_note": str(reasoning.confidence_note) if reasoning.confidence_note is not None else None,
            "timestamp": str(reasoning.timestamp)
        }
        
        db.close()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reasoning: {str(e)}")


@app.get("/api/design-bridge/cities")
def get_available_cities():
    """
    Get list of all cities with available data.
    
    **Use Case:** Frontend populates city selector dropdown
    
    **Example:** GET /api/design-bridge/cities
    """
    try:
        db = SessionLocal()
        
        # Get unique cities from rules
        cities = db.query(Rule.city).distinct().all()
        city_list = sorted([str(city[0]) for city in cities if city[0]])
        
        # Get counts for each city
        city_data = []
        for city in city_list:
            rule_count = db.query(Rule).filter(Rule.city.ilike(city)).count()
            feedback_count = db.query(Feedback).filter(Feedback.city.ilike(city)).count()
            
            city_data.append({
                "name": city,
                "rule_count": rule_count,
                "feedback_count": feedback_count
            })
        
        db.close()
        return {"cities": city_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cities: {str(e)}")


@app.get("/api/design-bridge/projects")
def get_all_projects():
    """
    Get list of all projects with metadata.
    
    **Use Case:** Frontend displays project portfolio
    
    **Example:** GET /api/design-bridge/projects
    """
    try:
        db = SessionLocal()
        
        # Get all projects from reasoning outputs
        projects = db.query(ReasoningOutput.project_id).distinct().all()
        project_list = []
        
        for proj in projects:
            project_id = str(proj[0]) if proj[0] else None
            if not project_id:
                continue
            
            # Get case count
            case_count = db.query(ReasoningOutput).filter(
                ReasoningOutput.project_id == project_id
            ).count()
            
            # Get latest case
            latest = db.query(ReasoningOutput).filter(
                ReasoningOutput.project_id == project_id
            ).order_by(ReasoningOutput.timestamp.desc()).first()
            
            project_list.append({
                "project_id": project_id,
                "case_count": case_count,
                "latest_case_id": str(latest.case_id) if latest and latest.case_id is not None else None,
                "last_updated": str(latest.timestamp) if latest and latest.timestamp is not None else None
            })
        
        db.close()
        return {"projects": project_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {str(e)}")





if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("🌉 AI Design Platform Bridge API")
    print("=" * 80)
    print("Starting API server...")
    print("Documentation: http://127.0.0.1:8001/api/design-bridge/docs")
    print("=" * 80)
    
    uvicorn.run("api_bridge:app", host="0.0.0.0", port=8001, reload=True)
