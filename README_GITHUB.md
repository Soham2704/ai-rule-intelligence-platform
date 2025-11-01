# 🏗️ AI Rule Intelligence & Design Platform Bridge

> **An intelligent, adaptive compliance system that transforms building regulations into actionable design intelligence using AI reasoning and reinforcement learning.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 Overview

The **AI Rule Intelligence Platform** is a comprehensive backend system that:

- 🧠 **Analyzes building regulations** using AI-powered reasoning
- 📊 **Provides confidence scores** via reinforcement learning agents
- 🏙️ **Supports multiple cities** (Mumbai, Pune, Ahmedabad)
- 🔌 **Exposes REST APIs** for frontend integration
- 📈 **Learns from user feedback** with city-adaptive algorithms
- 📚 **Stores structured data** in MCP (Model Context Protocol) database

---

## 🎯 Key Features

### ✨ AI-Powered Reasoning
- **Explainer Agent**: Generates human-readable explanations with clause-level reasoning
- **Confidence Scoring**: RL agent provides confidence levels (High/Moderate/Low)
- **Multi-Agent System**: Coordinates reasoning, calculation, and classification agents

### 🔌 REST API Bridge
- **8 Production-Ready Endpoints** for frontend integration
- **OpenAPI Documentation** auto-generated at `/api/design-bridge/docs`
- **CORS-Enabled** for cross-origin requests

### 🏙️ Multi-City Support
- **Mumbai**: 1,061 building regulations
- **Pune**: 232 development rules
- **Ahmedabad**: Regional planning norms
- **City-Adaptive Learning**: RL agent learns city-specific patterns

### 📊 Interactive Dashboard
- **Streamlit UI** for data exploration
- **Rule browsing** and search
- **Case analysis** with confidence visualization
- **Feedback collection** for RL training

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-rule-intelligence-platform.git
cd ai-rule-intelligence-platform

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### Running the System

```bash
# Terminal 1: Start Main API (Port 8000)
python main.py

# Terminal 2: Start Bridge API (Port 8001)
python api_bridge.py

# Terminal 3: Start Streamlit UI (Port 8501) - Optional
streamlit run design_platform_ui.py
```

### Access Points

- **Main API Docs**: http://127.0.0.1:8000/docs
- **Bridge API Docs**: http://127.0.0.1:8001/api/design-bridge/docs
- **Streamlit UI**: http://localhost:8501

---

## 📚 API Documentation

### Bridge API Endpoints

All endpoints are prefixed with `/api/design-bridge`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/rules/{city}` | Fetch all regulations for a city |
| `GET` | `/reasoning/{case_id}` | Get AI-generated reasoning for a case |
| `GET` | `/geometry/{case_id}` | Get 3D model information |
| `GET` | `/geometry/{case_id}/download` | Download STL geometry file |
| `GET` | `/feedback/city/{city}/stats` | Get city-specific feedback statistics |
| `GET` | `/cities` | List all available cities |
| `GET` | `/projects` | List all projects with metadata |
| `GET` | `/feedback/{case_id}` | Get feedback for a specific case |

### Example Usage

```bash
# Get rules for Mumbai
curl http://127.0.0.1:8001/api/design-bridge/rules/Mumbai

# Get AI reasoning for a case
curl http://127.0.0.1:8001/api/design-bridge/reasoning/mumbai_001

# Get city feedback statistics
curl http://127.0.0.1:8001/api/design-bridge/feedback/city/Mumbai/stats
```

### Frontend Integration Example

```javascript
// Fetch rules for a city
const response = await fetch('http://127.0.0.1:8001/api/design-bridge/rules/Mumbai');
const rules = await response.json();

// Get AI reasoning with confidence
const reasoning = await fetch('http://127.0.0.1:8001/api/design-bridge/reasoning/mumbai_001');
const data = await reasoning.json();
console.log('Confidence:', data.confidence_level, data.confidence_score);
console.log('Reasoning:', data.reasoning);
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│     AI Design Platform (Frontend)           │
└──────────────────┬──────────────────────────┘
                   │ HTTP/REST
                   ▼
┌─────────────────────────────────────────────┐
│         Bridge API (Port 8001)              │
│   • /rules/{city}                           │
│   • /reasoning/{case_id}                    │
│   • /geometry/{case_id}                     │
│   • /feedback/city/{city}/stats             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Main API (Port 8000)                │
│   ┌──────────┬──────────┬──────────┐       │
│   │   MCP    │    RL    │   LLM    │       │
│   │  Client  │  Agent   │  Agent   │       │
│   └──────────┴──────────┴──────────┘       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│        MCP Database (SQLite)                │
│   • rules                                   │
│   • reasoning_outputs                       │
│   • feedback                                │
│   • geometry_outputs                        │
└─────────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
ai-rule-intelligence-platform/
├── agents/                      # AI agents
│   ├── reasoning_agent.py       # Basic reasoning
│   ├── explainer_agent.py       # Enhanced explanations
│   ├── calculator_agent.py      # FSI calculations
│   ├── classification_agent.py  # Rule classification
│   └── ...
├── rl_env/                      # Reinforcement learning
│   ├── city_adaptive_env.py     # City-specific RL environment
│   ├── train_city_adaptive_agent.py
│   └── city_reward_table.json   # City-specific weights
├── rules_kb/                    # Rules knowledge base
│   ├── mumbai_rules.json
│   ├── pune_rules.json
│   └── ahmedabad_rules.json
├── tests/                       # Test suite
│   ├── test_multi_city.py
│   ├── test_pipeline.py
│   └── test_calculators.py
├── api_bridge.py               # Bridge API for frontend
├── main.py                     # Main API server
├── main_pipeline.py            # Core processing pipeline
├── mcp_client.py               # MCP database client
├── database_setup.py           # Database schema
├── design_platform_ui.py       # Streamlit dashboard
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🧪 Testing

### Run All Tests

```bash
# Multi-city integration tests
python tests/test_multi_city.py

# Pipeline validation
python tests/test_pipeline.py

# Calculator tests
python tests/test_calculators.py
```

### Verify Deliverables

```bash
# Check all components
python verify_deliverables.py
```

Expected output:
```
✅ All core deliverables are COMPLETE:
   1. AI Reasoning Agent & API Bridge - READY
   2. MCP with Reasoning + Confidence + Feedback - OPERATIONAL
   3. Multi-city Support (Mumbai, Pune, Ahmedabad) - VERIFIED
   4. Handover Documentation - COMPLETE
   5. Backend Ready for Integration - READY
```

---

## 📊 Database Schema

### `reasoning_outputs` Table

| Column | Type | Description |
|--------|------|-------------|
| `case_id` | String | Unique case identifier |
| `project_id` | String | Project identifier |
| `rules_applied` | JSON | List of applied rule IDs |
| `reasoning_summary` | Text | AI-generated explanation |
| `clause_summaries` | JSON | Clause-level breakdown |
| `confidence_score` | Float | RL confidence (0-1) |
| `confidence_level` | String | High/Moderate/Low |
| `confidence_note` | Text | Human-readable interpretation |

### `feedback` Table

| Column | Type | Description |
|--------|------|-------------|
| `case_id` | String | Case identifier |
| `city` | String | City name (indexed) |
| `feedback_type` | String | "up" or "down" |
| `timestamp` | String | ISO 8601 timestamp |
| `full_input` | JSON | Complete input parameters |
| `full_output` | JSON | Complete output report |

---

## 🎓 Documentation

- **[Handover Documentation](handover_v2.md)** - Complete technical handover
- **[Deliverables Summary](DELIVERABLES_SUMMARY.md)** - Project completion checklist
- **[Setup Guide](SETUP_AND_RUN.md)** - Detailed setup instructions
- **[API Reference](http://127.0.0.1:8001/api/design-bridge/docs)** - Interactive OpenAPI docs

---

## 🤝 Contributing

This project was developed as part of an AI-powered urban planning initiative. For contributions:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Backend Development:** Sohum Phutane  
**Frontend Integration:** Yash, Nipun, Bhavesh, Anmol (AI Design Platform Team)

---

## 🙏 Acknowledgments

- FastAPI for the excellent API framework
- Streamlit for the interactive dashboard
- Google Gemini API for AI reasoning capabilities
- Stable-Baselines3 for reinforcement learning

---

## 📧 Contact

For questions or support regarding this project, please open an issue on GitHub.

---

**🎉 Status: Production Ready | All Deliverables Complete**

---

Made with ❤️ for intelligent urban planning
