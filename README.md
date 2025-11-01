# 🏗️ AI Rule Intelligence & Design Platform Bridge v2.0

**An intelligent, adaptive compliance system that transforms building regulations into actionable design intelligence**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What's New in v2.0

✨ **AI Rule Explainer Agent** - Generates human-readable explanations with clause-level reasoning  
🌉 **REST API Bridge** - Complete API layer designed for frontend integration  
🧠 **City-Adaptive RL System** - Learns from user feedback per city  
🧪 **Multi-City Testing** - Validated across Mumbai, Pune, Ahmedabad, Nashik  
📊 **Interactive Visualization** - Streamlit dashboard for exploring data  
💾 **Enhanced MCP Schema** - Stores reasoning, confidence, and clause summaries  

---

## 📋 Overview
This repository contains the source code for a professional-grade, multi-agent AI pipeline designed to automate the analysis of complex, unstructured regulatory documents. The system is architected as a deployable API service that ingests raw PDF rulebooks, processes them through a robust data pipeline, and uses a combination of deterministic and AI agents—including a human-in-the-loop Reinforcement Learning agent—to generate comprehensive analysis reports and 3D geometry outputs.

This project was developed as a demonstration of advanced AI engineering principles, including system architecture, real-world data processing, building intelligent learning systems, and professional-grade testing, documentation, and automation.

## 🚀 Core Features

### Intelligent Reasoning System
- **AI Rule Explainer:** LLM-powered agent generates detailed explanations with clause references
- **Confidence Scoring:** RL agent provides High/Moderate/Low confidence levels
- **Structured Outputs:** JSON responses with reasoning, clause summaries, and metadata

### City-Adaptive Learning
- **Feedback Integration:** Learns from user thumbs up/down per city
- **Dynamic Weighting:** Adjusts recommendations based on city-specific preferences
- **Reward Tables:** Maintains separate learning curves for each city

### REST API Bridge
- **8 Production Endpoints:** Complete API for frontend integration
- **OpenAPI Documentation:** Interactive docs at `/api/design-bridge/docs`
- **CORS-Enabled:** Ready for cross-origin frontend integration

### Professional Architecture
End-to-End API Service: The entire system is packaged as a professional FastAPI service with documented endpoints for running cases, submitting feedback, and retrieving logs.

Automated AI Data Curation: A high-performance, parallelized AI agent (extract_rules_ai.py) reads unstructured text from OCR'd PDFs and uses an LLM to automatically populate a structured SQLite database.

Database-Driven "Fact-Checker" Architecture: The core analysis is driven by a precise Database Query Agent that retrieves deterministic facts, which are then explained in a rich, human-readable context by a Gemini Pro LLM agent. This hybrid approach ensures both accuracy and quality.

Human-in-the-Loop Reinforcement Learning (HIRL): A custom Gymnasium environment trains a Stable-Baselines3 PPO agent that learns an optimal policy from both a synthetically generated "oracle" and real human feedback collected via an interactive web UI.

Full-Stack Interactive UI: A Streamlit front-end application communicates with the FastAPI back-end to provide an interactive user experience, display results, and collect user feedback (👍/👎).

Professional Automation: N8N workflows automate the entire data ingestion pipeline (PDF Fetch -> OCR Parse -> AI Extract -> DB Load) and the RL retraining cycle.

Professional-Grade Engineering: The project includes a full pytest test suite, comprehensive structured JSONL logging, a Dockerfile for easy deployment, and a complete set of professional documentation.

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              AI DESIGN PLATFORM (Frontend)               │
│         (Yash, Nipun, Bhavesh, Anmol's Team)           │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/REST
                        ▼
┌─────────────────────────────────────────────────────────┐
│              BRIDGE API (Port 8001)                      │
│  • GET /rules/{city}                                     │
│  • GET /reasoning/{case_id}                              │
│  • GET /geometry/{case_id}                               │
│  • GET /feedback/city/{city}/stats                       │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│            CORE PIPELINE (Port 8000)                     │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐               │
│  │   MCP   │→ │ Explainer │→ │   RL    │               │
│  │ Client  │  │  Agent    │  │  Agent  │               │
│  └─────────┘  └──────────┘  └─────────┘               │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              MCP DATABASE (SQLite)                       │
│  • rules                  • reasoning_outputs            │
│  • feedback              • geometry_outputs             │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11 or higher
python --version

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Option 1: Run Complete Demo (Recommended)

```bash
# Terminal 1: Start Main API
python main.py

# Terminal 2: Start Bridge API
python api_bridge.py

# Terminal 3: Run Demo
python run_demo.py
```

### Option 2: Manual Setup

### Step-by-Step Manual Setup

#### 1. Environment Setup

```bash
python -m venv venv
.\venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

```

#### 2. Initialize Database

```bash
python database_setup.py
```

#### 3. Start API Servers

**Terminal 1 - Main API (Port 8000):**
```bash
python main.py
# Access docs at: http://127.0.0.1:8000/docs
```

**Terminal 2 - Bridge API (Port 8001):**
```bash
python api_bridge.py
# Access docs at: http://127.0.0.1:8001/api/design-bridge/docs
```

#### 4. Launch Visualization UI (Optional)

**Terminal 3 - Streamlit UI:**
```bash
streamlit run design_platform_ui.py
# Access at: http://localhost:8501
```

---

## ☁️ Deployment to Render

### Automatic Deployment with Render.yaml

This repository includes a `render.yaml` file for easy deployment to Render:

1. Fork this repository to your GitHub account
2. Log in to [Render](https://render.com/)
3. Click "New Web Service"
4. Connect your GitHub account and select this repository
5. Render will automatically detect the `render.yaml` file and configure the service
6. Add your `GEMINI_API_KEY` as an environment variable in the Render dashboard
7. Click "Create Web Service"

### Manual Deployment to Render

If you prefer to deploy manually:

1. Fork this repository to your GitHub account
2. Log in to [Render](https://render.com/)
3. Click "New Web Service"
4. Connect your GitHub account and select this repository
5. Configure the service with these settings:
   - **Name**: ai-rule-intelligence-platform
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_server.py`
6. Add your `GEMINI_API_KEY` as an environment variable in the Render dashboard
7. Click "Create Web Service"

### Environment Variables

Make sure to set the following environment variables in your Render dashboard:

- `GEMINI_API_KEY` - Your Google Gemini API key

---

## 🧪 Testing

### Run Multi-City Integration Tests

```bash
python tests/test_multi_city.py
```

**Tests:**
- ✅ Rule retrieval for Mumbai, Pune, Ahmedabad, Nashik
- ✅ AI reasoning generation with confidence scores
- ✅ MCP database storage
- ✅ Geometry file generation
- ✅ Bridge API endpoints

### Run Unit Tests

```bash
pytest tests/
```

---

## 📚 API Documentation

### Bridge API Endpoints (Port 8001)

#### Get Rules by City
```http
GET /api/design-bridge/rules/{city}
```

**Example:**
```bash
curl http://127.0.0.1:8001/api/design-bridge/rules/Mumbai
```

**Response:**
```json
[
  {
    "id": "DCPR_12.3",
    "city": "Mumbai",
    "clause_no": "12.3",
    "authority": "DCPR 2034",
    "entitlements": {
      "total_fsi": 3.0,
      "max_height_m": 24
    },
    "quick_summary": "FSI: 3.0, Height: 24m"
  }
]
```

#### Get AI Reasoning
```http
GET /api/design-bridge/reasoning/{case_id}
```

**Response:**
```json
{
  "case_id": "mumbai_001",
  "reasoning": "For a 1500 sqm plot on an 18m road...",
  "confidence_score": 0.88,
  "confidence_level": "High",
  "clause_summaries": [...]
}
```

#### Download Geometry
```http
GET /api/design-bridge/geometry/{case_id}/download
```

**Returns:** STL file for 3D visualization

#### Get City Statistics
```http
GET /api/design-bridge/feedback/city/{city}/stats
```

**Response:**
```json
{
  "city": "Mumbai",
  "approval_rate": 85.0,
  "upvotes": 17,
  "downvotes": 3,
  "confidence_avg": 0.856
}
```

**Full API Reference:** See [`handover_v2.md`](handover_v2.md)

---

## 🗂️ Project Structure

```
BLACKHOLE/
├── agents/
│   ├── explainer_agent.py      # NEW: AI Rule Explainer
│   ├── reasoning_agent.py      # Basic reasoning
│   ├── geometry_agent.py       # 3D geometry generation
│   └── ...
├── rl_env/
│   ├── city_adaptive_env.py    # NEW: City-adaptive RL
│   ├── train_city_adaptive_agent.py  # Training script
│   └── city_reward_table.json  # City-specific weights
├── tests/
│   ├── test_multi_city.py      # NEW: Integration tests
│   └── test_pipeline.py
├── api_bridge.py               # NEW: Bridge API
├── design_platform_ui.py       # NEW: Visualization UI
├── run_demo.py                 # NEW: Demo runner
├── main.py                     # Main API server
├── main_pipeline.py            # Core pipeline logic
├── mcp_client.py               # MCP database client
├── database_setup.py           # Database schema
├── handover_v2.md              # NEW: Complete handover docs
└── README.md                   # This file
```

---

## 🎓 Training the City-Adaptive RL Agent

```bash
python rl_env/train_city_adaptive_agent.py
```

**This will:**
1. Sync user feedback from MCP database
2. Update city-specific reward weights
3. Train PPO agent with adaptive rewards
4. Save model to `rl_env/ppo_city_adaptive_agent.zip`

---

## 📊 Visualization UI Features

Launch with: `streamlit run design_platform_ui.py`

### 4 Interactive Views:

1. **📊 Dashboard** - System metrics and city distribution
2. **🔍 Rule Explorer** - Browse and search rules by city
3. **💡 Case Analysis** - View AI reasoning with confidence
4. **📈 City Analytics** - Compare performance across cities

---

## 🏆 Deliverables Checklist

✅ **AI Reasoning Agent** - Clause-level explanations  
✅ **REST API Bridge** - 8 production endpoints  
✅ **City-Adaptive RL** - Feedback-driven learning  
✅ **Multi-City Testing** - 4 cities validated  
✅ **Visualization UI** - Interactive dashboard  
✅ **Enhanced MCP** - Reasoning + confidence storage  
✅ **Complete Documentation** - API reference + guides  �

---

## 📖 Documentation

- **[handover_v2.md](handover_v2.md)** - Complete technical handover for AI Design Platform team
- **API Docs (Interactive):**
  - Main API: http://127.0.0.1:8000/docs
  - Bridge API: http://127.0.0.1:8001/api/design-bridge/docs

---

## 🛠️ Technology Stack

**AI & Machine Learning:**
- PyTorch, LangChain, Google Gemini
- Stable-Baselines3 (PPO)
- Gymnasium (RL environments)

**Backend & API:**
- FastAPI, Uvicorn
- SQLAlchemy
- Pydantic

**Frontend & Visualization:**
- Streamlit
- Plotly
- Pandas

**Database:**
- SQLite (MCP)

**DevOps:**
- Docker
- Pytest
- Git/GitHub

---

## 👥 For the AI Design Platform Team

This backend is specifically designed for integration with your frontend:

1. **Start Here:** Read [`handover_v2.md`](handover_v2.md)
2. **API Reference:** Check `/api/design-bridge/docs`
3. **Test Integration:** Use the provided example calls
4. **Visualization:** Explore `design_platform_ui.py` for UI inspiration

**Questions?** All endpoints are documented with OpenAPI specs.


---

## 🚀 Next Steps

1. ✅ Backend is complete and tested
2. ✅ API bridge is production-ready
3. ✅ Documentation is comprehensive
4. 🎯 **Ready for frontend integration!**

**Let's build the future of intelligent design! 🏗️**
