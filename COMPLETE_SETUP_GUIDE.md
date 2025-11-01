# Complete Setup Guide for AI Rule Intelligence Platform

This guide provides instructions for deploying the AI Rule Intelligence Platform with all features enabled in a complete, non-minimal configuration.

## Overview

The AI Rule Intelligence Platform is now configured for full deployment with all features enabled, including:
- Full AI/ML capabilities
- Database integration
- Advanced data processing
- Visualization tools
- Document processing
- 3D geometry handling
- Testing framework
- Proper error handling and logging

## File Structure

```
├── main.py                 # Main FastAPI application with all endpoints
├── requirements.txt        # Full dependency list for complete functionality
├── render.yaml             # Render deployment configuration
├── Dockerfile              # Docker container configuration
├── start_server.py         # Enhanced startup script with initialization
├── runtime.txt             # Python runtime version (3.12.0)
├── .python-version         # Python version specification (3.12.0)
├── Procfile                # Process configuration for deployment platforms
├── .render-buildpacks      # Render buildpack configuration
└── FULL_DEPLOYMENT_SUMMARY.md  # Summary of changes made
```

## Deployment Options

### 1. Render Deployment

The application is configured for deployment on Render:

1. Push your code to a GitHub repository
2. Connect the repository to Render
3. Render will automatically use:
   - `render.yaml` for service configuration
   - `requirements.txt` for dependencies
   - `start_server.py` for application startup

Build command: `pip install --upgrade pip && pip install setuptools==68.2.2 wheel==0.41.2 && pip install --only-binary=:all: -r requirements.txt`
Start command: `python start_server.py`

### 2. Docker Deployment

Build and run with Docker:

```bash
docker build -t ai-rule-platform .
docker run -p 8000:8000 ai-rule-platform
```

The Dockerfile is configured to:
- Use Python 3.12-slim base image
- Install system dependencies (gcc)
- Install all Python dependencies from requirements.txt
- Copy all application files
- Expose port 8000
- Start the server using start_server.py

### 3. Local Development

For local development:

```bash
python start_server.py
```

This will:
1. Initialize the database
2. Load all components
3. Start the FastAPI server on port 8000
4. Provide access to API documentation at:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Key Features Enabled

### Core API Endpoints
- POST /run_case - Run the full compliance pipeline for a single case
- GET /projects/{project_id}/cases - Get all case results for a specific project
- POST /feedback - Submit feedback for a processed case with adaptive learning
- GET /rules/{city} - Fetch all structured rules from MCP for a given city
- GET /logs/{case_id} - Get all agent logs for a specific case
- GET /geometry/{project_id}/{case_id} - Serve generated STL geometry files
- GET /feedback/{case_id} - Fetch feedback data for a given case
- GET /get_feedback_summary - Returns aggregated feedback statistics
- GET /health - Health check endpoint
- GET / - API root with information and available endpoints

### AI/ML Capabilities
- Langchain integration for advanced reasoning
- Google Generative AI (Gemini) for contextual explanations
- Stable Baselines3 for reinforcement learning
- PyTorch for deep learning models
- Sentence Transformers for semantic similarity

### Data Processing
- Pandas for data manipulation
- Scikit-learn for machine learning
- NumPy for numerical computing

### Visualization
- Streamlit for web interfaces
- Plotly for interactive charts

### Document Processing
- Pillow for image processing
- Pytesseract for OCR
- PyMuPDF (fitz) for PDF processing
- numpy-stl for 3D geometry handling

## Environment Variables

The application requires the following environment variables:

- `GEMINI_API_KEY` - Google Generative AI API key
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI models)
- `DATABASE_URL` - Database connection string (if using external database)

For local development, these can be specified in a `.env` file.

## Python Version

The application is configured to use Python 3.12.0, which provides:
- Better performance
- Improved error messages
- Enhanced type hinting
- Compatibility with the latest AI/ML libraries

## Dependencies

All dependencies are specified in `requirements.txt` with pinned versions to ensure reproducible builds. Key dependencies include:

- FastAPI 0.104.1 - Modern, fast web framework
- Uvicorn 0.24.0 - ASGI server
- SQLAlchemy 2.0.23 - Database toolkit
- NumPy 1.26.4 - Numerical computing (compatible with Python 3.12)
- Pandas 2.0.3 - Data analysis
- PyTorch 2.1.2 - Machine learning
- Langchain 0.0.350 - AI application framework

## Troubleshooting

### Import Errors
If you encounter import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Database Issues
If database initialization fails, check that:
1. The database file or connection is accessible
2. Required database tables are created
3. The database schema matches the application expectations

### AI Model Loading
If AI models fail to load:
1. Check that API keys are properly configured
2. Verify internet connectivity for cloud-based models
3. Ensure sufficient memory for model loading

## Maintenance

### Updating Dependencies
To update dependencies:
1. Modify `requirements.txt` with new versions
2. Test locally
3. Deploy to staging environment
4. Verify functionality
5. Deploy to production

### Adding New Features
To add new features:
1. Implement the feature in the appropriate module
2. Add new dependencies to `requirements.txt` if needed
3. Update API documentation in `main.py`
4. Add tests if applicable
5. Test thoroughly before deployment

## Support

For issues with deployment or functionality, refer to:
- `FULL_DEPLOYMENT_SUMMARY.md` - Summary of changes made
- `README.md` - General project documentation
- API documentation at `/docs` when the server is running

The platform is now ready for full production deployment with all features enabled.