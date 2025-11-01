# 🚀 Deploying AI Rule Intelligence Platform to Render

This guide will help you deploy the complete AI Rule Intelligence Platform to Render with all three services (Main API, Bridge API, and Streamlit UI).

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Google Gemini API Key** - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🎯 Deployment Options

### Option 1: Blueprint Deployment (Recommended - All Services at Once)

This deploys all 3 services automatically using the `render.yaml` blueprint.

#### Step 1: Push Code to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for Render deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-rule-platform.git
git branch -M main
git push -u origin main
```

#### Step 2: Deploy via Render Blueprint

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect the `render.yaml` file automatically
5. Configure the environment variables:
   - `GEMINI_API_KEY` - Your Google Gemini API key
6. Click **"Apply"**

Render will deploy all 3 services:
- ✅ `ai-rule-api` - Main API (https://ai-rule-api.onrender.com)
- ✅ `ai-rule-bridge` - Bridge API (https://ai-rule-bridge.onrender.com)
- ✅ `ai-rule-ui` - Streamlit UI (https://ai-rule-ui.onrender.com)

---

### Option 2: Manual Deployment (Individual Services)

Deploy each service separately for more control.

#### Service 1: Main API (Port 8000)

1. **Create New Web Service**
   - Dashboard → New + → Web Service
   - Connect your GitHub repository
   - Name: `ai-rule-api`

2. **Configure Build & Start**
   - **Build Command**: `./build.sh`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.12.0

3. **Environment Variables**
   ```
   GEMINI_API_KEY = your_actual_api_key_here
   PYTHON_VERSION = 3.12.0
   ```

4. **Advanced Settings**
   - Health Check Path: `/docs`
   - Auto-Deploy: Yes

#### Service 2: Bridge API (Port 8001)

1. **Create New Web Service**
   - Name: `ai-rule-bridge`

2. **Configure Build & Start**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_bridge:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   ```
   GEMINI_API_KEY = your_actual_api_key_here
   MAIN_API_URL = https://ai-rule-api.onrender.com
   PYTHON_VERSION = 3.12.0
   ```

4. **Advanced Settings**
   - Health Check Path: `/api/design-bridge/docs`

#### Service 3: Streamlit UI (Port 8501)

1. **Create New Web Service**
   - Name: `ai-rule-ui`

2. **Configure Build & Start**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run design_platform_ui.py --server.port $PORT --server.address 0.0.0.0`

3. **Environment Variables**
   ```
   BRIDGE_API_URL = https://ai-rule-bridge.onrender.com
   PYTHON_VERSION = 3.12.0
   ```

---

## 🔧 Post-Deployment Configuration

### Update API URLs in Code

After deployment, you need to update the hardcoded localhost URLs:

1. **Update `design_platform_ui.py`**:
   ```python
   # Replace localhost URLs with your Render URLs
   BRIDGE_API_URL = os.getenv("BRIDGE_API_URL", "https://ai-rule-bridge.onrender.com")
   ```

2. **Update `api_bridge.py`**:
   ```python
   # Replace localhost URLs with your Render URLs
   MAIN_API_URL = os.getenv("MAIN_API_URL", "https://ai-rule-api.onrender.com")
   ```

3. Commit and push changes to trigger auto-deploy.

---

## 📊 Database Persistence (Important!)

⚠️ **Warning**: Render's free tier uses **ephemeral storage**, meaning your database will reset on each deployment.

### Solutions:

#### Option A: Use Render Disk (Recommended)
Add a persistent disk to your `ai-rule-api` service:
1. Go to service settings → Disks
2. Add Disk: `/opt/render/project/src/rules_db`
3. Size: 1GB (free tier)

#### Option B: Use External Database
For production, use:
- **PostgreSQL** (Render provides free PostgreSQL)
- **Supabase** (Free tier with 500MB)
- **PlanetScale** (Free MySQL-compatible DB)

#### Option C: Cloud Storage for SQLite
Store the SQLite file in:
- **AWS S3**
- **Google Cloud Storage**
- **Backblaze B2**

---

## 🌐 Accessing Your Deployed Services

After deployment, access your services at:

- **Main API Docs**: `https://ai-rule-api.onrender.com/docs`
- **Bridge API Docs**: `https://ai-rule-bridge.onrender.com/api/design-bridge/docs`
- **Streamlit UI**: `https://ai-rule-ui.onrender.com`

---

## 🔍 Testing Deployment

### Test Main API
```bash
curl -X POST "https://ai-rule-api.onrender.com/run_case" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test_01",
    "case_id": "test_case_01",
    "city": "Mumbai",
    "document": "test.pdf",
    "parameters": {
      "plot_size": 2000,
      "location": "urban",
      "road_width": 20
    }
  }'
```

### Test Bridge API
```bash
curl "https://ai-rule-bridge.onrender.com/api/design-bridge/projects"
```

### Test UI
Open in browser: `https://ai-rule-ui.onrender.com`

---

## 🐛 Troubleshooting

### Issue 1: Service Won't Start
**Solution**: Check logs in Render Dashboard → Your Service → Logs

### Issue 2: Module Not Found
**Solution**: Ensure all dependencies are in `requirements.txt`
```bash
pip freeze > requirements.txt
```

### Issue 3: Database Empty After Restart
**Solution**: Add persistent disk (see Database Persistence section)

### Issue 4: API Timeout (Free Tier)
**Solution**: 
- Render free tier spins down after 15 mins of inactivity
- First request after sleep takes ~30 seconds
- Upgrade to paid tier for always-on service

### Issue 5: CORS Errors
**Solution**: Verify CORS middleware in `main.py` and `api_bridge.py` allows your domains

---

## 💰 Cost Estimate

### Free Tier (Perfect for Testing)
- 3 Web Services: **$0/month**
- 750 hours/month per service
- Services spin down after 15 min inactivity
- Ephemeral storage only

### Recommended Production Setup
- 3 Web Services (Starter): **$21/month** ($7 each)
- PostgreSQL (Starter): **$7/month**
- Persistent Disk (1GB): **Free**
- **Total**: ~$28/month

---

## 🚀 Advanced: Custom Domain

1. Go to Service Settings → Custom Domains
2. Add your domain (e.g., `api.yourdomain.com`)
3. Update DNS records as instructed
4. Render provides free SSL certificates

---

## 📝 Environment Variables Checklist

Make sure these are set for each service:

**Main API (`ai-rule-api`)**:
- ✅ `GEMINI_API_KEY`
- ✅ `PYTHON_VERSION`

**Bridge API (`ai-rule-bridge`)**:
- ✅ `GEMINI_API_KEY`
- ✅ `MAIN_API_URL`
- ✅ `PYTHON_VERSION`

**Streamlit UI (`ai-rule-ui`)**:
- ✅ `BRIDGE_API_URL`
- ✅ `PYTHON_VERSION`

---

## 🎉 You're Done!

Your AI Rule Intelligence Platform is now live on Render! 

**Next Steps**:
1. Test all endpoints
2. Monitor logs for errors
3. Set up persistent storage
4. Configure custom domains (optional)
5. Enable auto-scaling (paid tier)

**Need Help?**
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- Check service logs in dashboard

---

## 📚 Additional Resources

- **Render Python Docs**: https://render.com/docs/deploy-python
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Streamlit Deployment**: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app

---

Happy Deploying! 🚀
