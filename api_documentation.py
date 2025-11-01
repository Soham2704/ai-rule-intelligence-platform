"""
API Documentation Generator
----------------------------
Generates comprehensive OpenAPI/Swagger documentation for all REST endpoints
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Enhanced API Models with detailed examples and descriptions

class CaseParameters(BaseModel):
    """Input parameters for a building development case"""
    plot_size: int = Field(
        ..., 
        description="Total plot area in square meters",
        example=2000,
        ge=100,
        le=100000
    )
    location: str = Field(
        ...,
        description="Location type: urban, suburban, or rural",
        example="urban",
        pattern="^(urban|suburban|rural)$"
    )
    road_width: int = Field(
        ...,
        description="Width of abutting road in meters",
        example=18,
        ge=3,
        le=100
    )

    class Config:
        schema_extra = {
            "example": {
                "plot_size": 2000,
                "location": "urban",
                "road_width": 18
            }
        }


class CaseInput(BaseModel):
    """Complete case submission for compliance analysis"""
    project_id: str = Field(
        ...,
        description="Unique identifier for the project",
        example="proj_tower_heights_01"
    )
    case_id: str = Field(
        ...,
        description="Unique identifier for this specific case",
        example="mumbai_case_001"
    )
    city: str = Field(
        ...,
        description="City where the project is located (Mumbai, Pune, Ahmedabad, Nashik)",
        example="Mumbai"
    )
    document: str = Field(
        ...,
        description="Reference to applicable building regulations document",
        example="Mumbai_DCPR_2034.pdf"
    )
    parameters: CaseParameters

    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_tower_heights_01",
                "case_id": "mumbai_case_001",
                "city": "Mumbai",
                "document": "Mumbai_DCPR_2034.pdf",
                "parameters": {
                    "plot_size": 2000,
                    "location": "urban",
                    "road_width": 18
                }
            }
        }


class ClauseSummary(BaseModel):
    """Structured summary of a specific regulatory clause"""
    clause_id: str = Field(..., description="Unique clause identifier", example="MUM-FSI-001")
    authority: str = Field(..., description="Regulatory authority", example="MCGM")
    clause_no: str = Field(..., description="Official clause number", example="DCPR-12.3")
    quick_summary: str = Field(..., description="Brief clause summary", example="FSI: 2.4, Height: 24m")
    entitlements: Dict[str, Any] = Field(..., description="Specific entitlements granted")
    conditions: Dict[str, Any] = Field(..., description="Conditions for applicability")


class CaseOutput(BaseModel):
    """AI-generated compliance analysis output"""
    project_id: str
    case_id: str
    city: str
    parameters: Dict[str, Any]
    
    rules_applied: List[str] = Field(
        ...,
        description="List of rule IDs that were applied",
        example=["MUM-FSI-001", "MUM-LOS-002", "MUM-SETBACK-003"]
    )
    
    reasoning: str = Field(
        ...,
        description="Human-readable explanation with contextual analysis",
        example="\ud83d\udccd **PROJECT OVERVIEW**\nThis proposal involves a 2,000 sqm urban residential plot..."
    )
    
    clause_summaries: List[ClauseSummary] = Field(
        ...,
        description="Detailed breakdown of each applicable clause"
    )
    
    confidence_score: float = Field(
        ...,
        description="RL agent confidence score (0-1)",
        example=0.92,
        ge=0.0,
        le=1.0
    )
    
    confidence_level: str = Field(
        ...,
        description="Qualitative confidence assessment",
        example="High",
        pattern="^(Low|Moderate|High)$"
    )
    
    confidence_note: str = Field(
        ...,
        description="Explanation of confidence level",
        example="The RL agent is highly confident in this recommendation."
    )
    
    geometry_file: Optional[str] = Field(
        None,
        description="Path to generated 3D geometry file (if applicable)",
        example="outputs/projects/proj_tower_heights_01/mumbai_case_001_geometry.stl"
    )
    
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp of analysis",
        example="2025-10-16T14:30:00Z"
    )

    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_tower_heights_01",
                "case_id": "mumbai_case_001",
                "city": "Mumbai",
                "parameters": {"plot_size": 2000, "location": "urban", "road_width": 18},
                "rules_applied": ["MUM-FSI-001", "MUM-LOS-002"],
                "reasoning": "\ud83d\udccd **PROJECT OVERVIEW**\nThis proposal involves a 2,000 sqm urban plot...",
                "clause_summaries": [
                    {
                        "clause_id": "MUM-FSI-001",
                        "authority": "MCGM",
                        "clause_no": "DCPR-12.3",
                        "quick_summary": "FSI: 2.4",
                        "entitlements": {"total_fsi": 2.4},
                        "conditions": {"plot_area_sqm": {"min": 1000, "max": 3000}}
                    }
                ],
                "confidence_score": 0.92,
                "confidence_level": "High",
                "confidence_note": "The RL agent is highly confident in this recommendation.",
                "geometry_file": "outputs/projects/proj_tower_heights_01/mumbai_case_001_geometry.stl",
                "timestamp": "2025-10-16T14:30:00Z"
            }
        }


class FeedbackInput(BaseModel):
    """User feedback submission for reinforcement learning"""
    project_id: str = Field(..., description="Project identifier")
    case_id: str = Field(..., description="Case identifier")
    input_case: Dict[str, Any] = Field(..., description="Original input parameters")
    output_report: Dict[str, Any] = Field(..., description="Generated analysis output")
    user_feedback: str = Field(
        ...,
        description="User rating: 'up' for positive, 'down' for negative",
        pattern="^(up|down)$",
        example="up"
    )
    selected_city: Optional[str] = Field(
        None,
        description="City context for feedback (required for city-adaptive learning)",
        example="Mumbai"
    )
    feedback_comments: Optional[str] = Field(
        None,
        description="Optional user comments",
        example="FSI calculation was accurate and clearly explained"
    )

    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_tower_heights_01",
                "case_id": "mumbai_case_001",
                "input_case": {"city": "Mumbai", "parameters": {"plot_size": 2000}},
                "output_report": {"reasoning": "...", "confidence_score": 0.92},
                "user_feedback": "up",
                "selected_city": "Mumbai",
                "feedback_comments": "Very helpful analysis"
            }
        }


class RuleSchema(BaseModel):
    """Structured building regulation rule"""
    id: str = Field(..., description="Unique rule identifier", example="MUM-FSI-001")
    city: str = Field(..., description="Applicable city", example="Mumbai")
    rule_type: str = Field(..., description="Type of rule", example="FSI")
    conditions: Dict[str, Any] = Field(..., description="Conditions for applicability")
    entitlements: Dict[str, Any] = Field(..., description="Granted permissions/requirements")
    notes: str = Field(..., description="Additional context", example="Standard FSI for urban plots")
    authority: str = Field(..., description="Regulatory authority", example="MCGM")
    clause_no: str = Field(..., description="Official clause reference", example="DCPR-12.3")
    page: str = Field(..., description="Page number in source document", example="84")

    class Config:
        schema_extra = {
            "example": {
                "id": "MUM-FSI-001",
                "city": "Mumbai",
                "rule_type": "FSI",
                "conditions": {
                    "plot_area_sqm": {"min": 1000, "max": 3000},
                    "road_width_m": {"min": 15, "max": 20}
                },
                "entitlements": {
                    "total_fsi": 2.4,
                    "max_height_m": 24
                },
                "notes": "Standard FSI for urban residential plots",
                "authority": "MCGM",
                "clause_no": "DCPR-12.3",
                "page": "84"
            }
        }


class FeedbackSummary(BaseModel):
    """Aggregated feedback statistics"""
    upvotes: int = Field(..., description="Total positive feedback count", example=127)
    downvotes: int = Field(..., description="Total negative feedback count", example=23)
    total_feedback: int = Field(..., description="Total feedback records", example=150)
    approval_rate: float = Field(..., description="Percentage of positive feedback", example=0.847)
    cities: Dict[str, Dict[str, int]] = Field(
        ...,
        description="City-specific feedback breakdown",
        example={
            "Mumbai": {"upvotes": 65, "downvotes": 10},
            "Pune": {"upvotes": 42, "downvotes": 8},
            "Ahmedabad": {"upvotes": 20, "downvotes": 5}
        }
    )

    class Config:
        schema_extra = {
            "example": {
                "upvotes": 127,
                "downvotes": 23,
                "total_feedback": 150,
                "approval_rate": 0.847,
                "cities": {
                    "Mumbai": {"upvotes": 65, "downvotes": 10},
                    "Pune": {"upvotes": 42, "downvotes": 8}
                }
            }
        }


# API Endpoint Documentation
API_ENDPOINTS_DOC = """
# AI Rule Intelligence Platform - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (add JWT/API keys for production).

---

## Endpoints

### 1. POST /run_case
**Run full compliance analysis for a building project**

**Request Body:**
```json
{
  "project_id": "proj_tower_heights_01",
  "case_id": "mumbai_case_001",
  "city": "Mumbai",
  "document": "Mumbai_DCPR_2034.pdf",
  "parameters": {
    "plot_size": 2000,
    "location": "urban",
    "road_width": 18
  }
}
```

**Response:** `CaseOutput` with AI reasoning, applicable rules, and confidence scores

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/run_case" \\
  -H "Content-Type: application/json" \\
  -d '{
    "project_id": "test_proj_01",
    "case_id": "test_001",
    "city": "Mumbai",
    "document": "DCPR_2034.pdf",
    "parameters": {
      "plot_size": 2000,
      "location": "urban",
      "road_width": 18
    }
  }'
```

---

### 2. GET /rules/{city}
**Fetch all building regulations for a specific city**

**Path Parameters:**
- `city` (string): City name (Mumbai, Pune, Ahmedabad, Nashik)

**Response:** Array of `RuleSchema` objects

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/rules/Mumbai"
```

---

### 3. POST /feedback
**Submit user feedback for RL training**

**Request Body:** `FeedbackInput`

**Response:**
```json
{
  "status": "success",
  "feedback_id": "fb_uuid_12345"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/feedback" \\
  -H "Content-Type: application/json" \\
  -d '{
    "project_id": "proj_01",
    "case_id": "case_001",
    "input_case": {...},
    "output_report": {...},
    "user_feedback": "up",
    "selected_city": "Mumbai"
  }'
```

---

### 4. GET /get_feedback_summary
**Get aggregated feedback statistics**

**Response:** `FeedbackSummary` with city-wise breakdown

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/get_feedback_summary"
```

---

### 5. GET /projects/{project_id}/cases
**Get all cases for a specific project**

**Path Parameters:**
- `project_id` (string): Project identifier

**Response:** Array of case outputs

---

### 6. GET /geometry/{project_id}/{case_id}
**Download 3D geometry file (STL) for a case**

**Path Parameters:**
- `project_id` (string)
- `case_id` (string)

**Response:** STL file download

---

### 7. GET /logs/{case_id}
**Get detailed agent logs for debugging**

**Path Parameters:**
- `case_id` (string)

**Response:** Array of log entries

---

## Interactive API Documentation

Access Swagger UI at: **http://localhost:8000/docs**  
Access ReDoc at: **http://localhost:8000/redoc**

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 404 | Resource not found |
| 422 | Validation error |
| 500 | Server error |
| 503 | Service initializing |

---

## Rate Limiting
No rate limits currently (add for production)

## Versioning
API Version: v1.0 (add versioning for future releases)
"""


if __name__ == "__main__":
    print(API_ENDPOINTS_DOC)
    print("\n✓ API Documentation generated!")
    print("\n📚 For interactive docs, run: python main.py")
    print("   Then visit: http://localhost:8000/docs")
