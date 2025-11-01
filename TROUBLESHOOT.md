# 🚨 Render Deployment Troubleshooting Guide

If your deployment is failing, this guide will help you identify and fix the issues.

## 🔍 Common Deployment Issues & Solutions

### Issue 1: "Failed to Deploy" with No Specific Error

**Symptoms**: Generic "Failed to Deploy" message with no detailed error

**Solutions**:
1. **Check Build Logs**: In Render Dashboard → Your Service → Logs → Build tab
2. **Verify File Permissions**: Make sure [build.sh](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\build.sh) is executable
3. **Check Requirements**: Ensure all dependencies in [requirements.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\requirements.txt) are correct
4. **Verify Python Version**: Confirm [runtime.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\runtime.txt) contains `python-3.12.0`

### Issue 2: Build Process Fails

**Symptoms**: Build logs show errors during dependency installation

**Solutions**:
1. **Update Dependencies**: Some packages may have version conflicts
   ```bash
   # Try installing with --no-cache-dir
   pip install --no-cache-dir -r requirements.txt
   ```

2. **Check Package Versions**: Some packages may be incompatible
   - Try pinning specific versions in [requirements.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\requirements.txt)
   - Example: `langchain==0.1.0` instead of just `langchain`

3. **Memory Issues**: Large packages like torch may cause out-of-memory
   - Add `--no-cache-dir` flag to pip install
   - Consider using lighter alternatives if possible

### Issue 3: Database Setup Fails

**Symptoms**: Build logs show errors during database setup or rule population

**Solutions**:
1. **Check Script Permissions**: Ensure [database_setup.py](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\database_setup.py) and [populate_comprehensive_rules.py](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\populate_comprehensive_rules.py) are executable
2. **Verify Script Content**: Make sure the scripts don't have syntax errors
3. **Directory Creation**: Ensure directories are created before database setup

### Issue 4: Start Command Fails

**Symptoms**: Build succeeds but service fails to start

**Solutions**:
1. **Check Start Command**: Verify the command in [render.yaml](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\render.yaml) matches your app structure
2. **Port Binding**: Make sure your app binds to `0.0.0.0:$PORT`
3. **Missing Dependencies**: Ensure all runtime dependencies are in [requirements.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\requirements.txt)

## 🛠️ Step-by-Step Troubleshooting

### Step 1: Check Build Logs

1. Go to Render Dashboard
2. Click on your failed service
3. Go to "Logs" tab
4. Click on "Build" sub-tab
5. Look for error messages (usually in red)

### Step 2: Verify File Contents

Check these critical files:

**[runtime.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\runtime.txt)** should contain:
```
python-3.12.0
```

**[Procfile](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\Procfile)** should contain:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**[build.sh](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\build.sh)** should be executable and contain:
```bash
#!/usr/bin/env bash
set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p rules_db
mkdir -p outputs/projects
mkdir -p reports

echo "Setting up database..."
python database_setup.py

echo "Populating database with rules..."
python populate_comprehensive_rules.py

echo "Build completed successfully!"
```

### Step 3: Simplify Deployment for Testing

Try a minimal deployment first:

1. **Temporarily modify [render.yaml](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\render.yaml)**:
   ```yaml
   services:
     - type: web
       name: ai-rule-test
       runtime: python
       buildCommand: pip install --upgrade pip && pip install fastapi uvicorn
       startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Create a simple [main.py](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\main.py)** for testing:
   ```python
   from fastapi import FastAPI
   
   app = FastAPI()
   
   @app.get("/")
   def read_root():
       return {"Hello": "World"}
   
   @app.get("/docs")
   def read_docs():
       return {"status": "ok"}
   ```

3. Deploy this simplified version to verify the basic setup works

### Step 4: Check Dependencies

Some dependencies might be causing issues. Try this approach:

1. **Create a minimal [requirements.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\requirements.txt)**:
   ```
   fastapi
   uvicorn[standard]
   python-dotenv
   ```

2. Deploy with minimal dependencies first
3. Gradually add more dependencies after confirming basic deployment works

### Step 5: Environment Variables

Make sure environment variables are properly set:

1. In Render Dashboard → Your Service → Settings → Environment Variables
2. Add:
   - `PYTHON_VERSION` = `3.12.0`
   - `GEMINI_API_KEY` = `your_actual_api_key`

## 🐛 Specific Error Solutions

### Error: "No module named 'fastapi'"

**Solution**: 
- Check [requirements.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\requirements.txt) includes `fastapi`
- Verify build command installs requirements

### Error: "No such file or directory: 'rules_db'""

**Solution**:
- Ensure [build.sh](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\build.sh) creates the directory
- Add `mkdir -p rules_db` before database setup

### Error: "ModuleNotFoundError: No module named 'langchain'"

**Solution**:
- Check [requirements.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\requirements.txt) includes `langchain`
- Try pinning a specific version: `langchain==0.1.0`

### Error: "Address already in use"

**Solution**:
- Make sure your start command uses `$PORT` environment variable
- Don't hardcode port numbers

## 🔧 Advanced Troubleshooting

### Enable Verbose Logging

Add to your build command:
```bash
pip install -r requirements.txt -v
```

### Check Disk Space

Large dependencies might exceed Render's build disk space:
- Try installing packages one by one
- Remove unnecessary dependencies

### Use Build Cache

Add to your build command:
```bash
pip install --no-cache-dir -r requirements.txt
```

## 📞 Need More Help?

1. **Share Build Logs**: Copy the error messages from Render build logs
2. **Check GitHub Issues**: Look for similar issues in the repository
3. **Contact Render Support**: https://render.com/help

## ✅ Quick Checklist

Before redeploying:

- [ ] [runtime.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\runtime.txt) contains `python-3.12.0`
- [ ] [Procfile](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\Procfile) has correct start command
- [ ] [build.sh](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\build.sh) is executable and creates directories
- [ ] [requirements.txt](file://c:\Users\hp\Downloads\wert\ai-rule-intelligence-platform\requirements.txt) has all necessary dependencies
- [ ] Environment variables are set in Render dashboard
- [ ] No syntax errors in Python files
- [ ] Git repository is up to date

## 🔄 Redeploy Process

After making fixes:

1. Commit and push changes to GitHub
2. In Render Dashboard → Manual Deploy → Deploy Latest Commit
3. Monitor build logs for errors
4. Check runtime logs after deployment

---

**Remember**: Start simple and gradually add complexity. Deploy a minimal FastAPI app first, then add your actual code and dependencies.
