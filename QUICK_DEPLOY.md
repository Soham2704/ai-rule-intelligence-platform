# Quick Start Guide: Deploy to Render in 5 Minutes

## 🚀 Super Quick Deployment

### Step 1: Prepare Your Repository (30 seconds)

```bash
# Make build.sh executable (if on Mac/Linux)
chmod +x build.sh

# Commit all deployment files
git add .
git commit -m "Add Render deployment configuration"
git push
```

### Step 2: Deploy on Render (2 minutes)

1. **Go to**: https://dashboard.render.com
2. **Click**: "New +" → "Blueprint"
3. **Connect**: Your GitHub repository
4. **Set Environment Variable**:
   - `GEMINI_API_KEY` = `your_api_key_here`
5. **Click**: "Apply"

✅ **Done!** Your services will be live in 3-5 minutes at:
- Main API: `https://ai-rule-api.onrender.com/docs`
- Bridge API: `https://ai-rule-bridge.onrender.com/api/design-bridge/docs`
- UI: `https://ai-rule-ui.onrender.com`

---

## 📋 Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `.env` file NOT committed (it's in `.gitignore`)
- [ ] Gemini API key ready
- [ ] `build.sh` is executable
- [ ] All deployment files present:
  - [ ] `render.yaml`
  - [ ] `build.sh`
  - [ ] `Procfile`
  - [ ] `runtime.txt`
  - [ ] `requirements.txt`

---

## 🎯 What Happens During Deployment

1. **Build Phase** (~3 minutes):
   - Installs Python 3.12
   - Installs all dependencies from `requirements.txt`
   - Creates database schema
   - Populates database with 12+ Mumbai rules
   - Creates necessary directories

2. **Start Phase** (~30 seconds):
   - Starts 3 services simultaneously
   - Main API on random port (Render assigns)
   - Bridge API on random port
   - Streamlit UI on random port

3. **Health Checks**:
   - Render pings `/docs` endpoint for Main API
   - Pings `/api/design-bridge/docs` for Bridge
   - Pings `/` for Streamlit

---

## 🔑 Getting Your Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)
4. Add it to Render environment variables

---

## ⚡ Free Tier Limitations

**What you get FREE**:
- ✅ 3 web services (750 hours each/month)
- ✅ Automatic HTTPS/SSL
- ✅ Auto-deploys from GitHub
- ✅ Basic metrics

**Limitations**:
- ⚠️ Services spin down after 15 min idle
- ⚠️ First request after sleep: ~30 seconds
- ⚠️ Ephemeral storage (database resets on redeploy)

**Upgrade to keep services always-on**: $7/service/month

---

## 🔧 Post-Deployment: Update URLs

After deployment, Render will give you 3 URLs. Update your code:

### Option 1: Use Environment Variables (Already Done! ✅)
The code already supports environment variables:
```python
MAIN_API_URL = os.getenv("MAIN_API_URL", "http://127.0.0.1:8000")
BRIDGE_API_URL = os.getenv("BRIDGE_API_URL", "http://127.0.0.1:8001/api/design-bridge")
```

Just set these in Render:
- Main API: Set `MAIN_API_URL` env var
- Bridge API: Set `BRIDGE_API_URL` env var
- UI: Already reads from environment

### Option 2: Hardcode (Not Recommended)
Only if you need to hardcode for some reason.

---

## 🧪 Testing Your Deployment

### Test 1: Main API
```bash
curl https://ai-rule-api.onrender.com/docs
# Should return HTML page
```

### Test 2: Run a Case
```bash
curl -X POST "https://ai-rule-api.onrender.com/run_case" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test_deploy",
    "case_id": "deploy_test_01",
    "city": "Mumbai",
    "document": "test.pdf",
    "parameters": {
      "plot_size": 2000,
      "location": "urban",
      "road_width": 20
    }
  }'
```

Expected response: JSON with `rules_applied` containing 5+ rules

### Test 3: Check Rules in Database
```bash
curl https://ai-rule-api.onrender.com/rules/Mumbai
# Should return array of 12+ Mumbai rules
```

### Test 4: Open UI
Open in browser: `https://ai-rule-ui.onrender.com`

---

## 🐛 Common Issues & Fixes

### Issue: "Service Failed to Start"
**Solution**: Check build logs
1. Dashboard → Your Service → Logs
2. Look for errors in build phase
3. Common fix: Check `requirements.txt` syntax

### Issue: "Database is Empty"
**Solution**: Build script didn't run
1. Check if `build.sh` was executed
2. Re-deploy with manual trigger
3. Check logs for `populate_comprehensive_rules.py` output

### Issue: "Cannot Connect to Other Services"
**Solution**: Update environment variables
1. Main API → Add env var `BRIDGE_API_URL`
2. Bridge → Add env var `MAIN_API_URL`
3. UI → Add env var `BRIDGE_API_URL`

### Issue: "First Request Takes Forever"
**Solution**: This is normal on free tier
- Services sleep after 15 min
- First request wakes them up (~30 sec)
- Subsequent requests are fast
- Upgrade to paid tier for always-on

---

## 💡 Pro Tips

1. **Monitor Your Services**
   - Enable notifications in Render dashboard
   - Check logs regularly for errors

2. **Database Persistence**
   - Add a persistent disk (Settings → Disks)
   - Mount at: `/opt/render/project/src/rules_db`
   - 1GB free per service

3. **Auto-Deploy**
   - Already enabled in `render.yaml`
   - Every git push triggers redeploy
   - Disable if you want manual control

4. **Custom Domain**
   - Free SSL included
   - Add in Settings → Custom Domains
   - Update DNS records as instructed

5. **Environment Secrets**
   - Never commit API keys
   - Use Render's environment variables
   - Mark sensitive vars as "secret"

---

## 📊 Monitoring Your Deployment

**Built-in Metrics**:
- Request count
- Response time
- Error rate
- CPU/Memory usage

**Access**: Dashboard → Service → Metrics

---

## 🎉 Success Checklist

After deployment, verify:
- [ ] All 3 services show "Live" status
- [ ] Main API `/docs` loads successfully
- [ ] Bridge API `/api/design-bridge/docs` loads
- [ ] Streamlit UI opens in browser
- [ ] Test API call returns Mumbai rules
- [ ] Database has 12+ Mumbai rules
- [ ] No errors in logs

---

## 🆘 Need Help?

**Render Support**:
- Community: https://community.render.com
- Docs: https://render.com/docs
- Status: https://status.render.com

**Debug Checklist**:
1. Check service logs
2. Verify environment variables
3. Test endpoints manually
4. Check CORS settings
5. Verify database populated

---

## 🚀 Next Steps

Once deployed:
1. ✅ Test all endpoints
2. ✅ Add persistent disk for database
3. ✅ Set up custom domain (optional)
4. ✅ Monitor logs for errors
5. ✅ Consider upgrading to paid tier
6. ✅ Set up CI/CD pipeline
7. ✅ Add monitoring/alerts

---

**Deployment Time**: 5-10 minutes
**Cost**: $0/month (free tier)
**Scalability**: Upgrade anytime

Happy Deploying! 🎉
