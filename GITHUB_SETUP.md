# 🚀 GitHub Repository Setup Guide - New Repository

This guide will help you create a **NEW** GitHub repository and upload this project there.

**⚠️ IMPORTANT:** This project is currently linked to an existing repository. We'll disconnect it and link to a new one.

---

## 📋 Prerequisites

1. **GitHub Account**: Create one at https://github.com if you don't have one
2. **Git Installed**: Download from https://git-scm.com/downloads
3. **Project Files**: All files in the BLACKHOLE directory

---

## 🔧 Step-by-Step Setup

### Step 0: Disconnect from Old Repository (IMPORTANT!)

**Current repository link:** `https://github.com/Soham2704/multi-agent-compliance-system.git`

Run this command to disconnect:

```powershell
# Remove old remote
git remote remove origin

# Verify it's removed
git remote -v
# Should show nothing
```

**OR** use the automated script:

```powershell
.\setup_new_repo.ps1
```

### Step 1: Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `ai-rule-intelligence-platform` (or your preferred name)
   - **Description**: "AI-powered building compliance system with multi-city support and REST API"
   - **Visibility**: Choose **Public** or **Private**
   - **DO NOT** initialize with README (we already have one)
   - **DO NOT** add .gitignore (we already have one)
5. Click **"Create repository"**

### Step 2: Prepare Your Local Repository

Open PowerShell/Terminal in the BLACKHOLE directory and run:

```powershell
# Initialize git repository
git init

# Add all files (respecting .gitignore)
git add .

# Check what will be committed
git status

# Create initial commit
git commit -m "Initial commit: AI Rule Intelligence Platform with multi-city support"
```

### Step 3: Connect to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username:

```powershell
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/ai-rule-intelligence-platform.git

# Verify remote was added
git remote -v
```

### Step 4: Push to GitHub

```powershell
# Push to GitHub (main branch)
git branch -M main
git push -u origin main
```

You may be prompted for GitHub credentials. Use:
- **Username**: Your GitHub username
- **Password**: Your Personal Access Token (NOT your GitHub password)

---

## 🔑 Creating a Personal Access Token (if needed)

If you need a Personal Access Token:

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: "AI Rule Intelligence Platform"
4. Select scopes:
   - ✅ `repo` (full control of private repositories)
5. Click **"Generate token"**
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

---

## 📝 Update README with Your Repository URL

After creating the repository, update the clone URL in `README_GITHUB.md`:

```bash
# Change this line:
git clone https://github.com/YOUR_USERNAME/ai-rule-intelligence-platform.git

# To your actual repository URL
```

Then commit and push the change:

```powershell
git add README_GITHUB.md
git commit -m "Update repository URL in README"
git push
```

---

## 🗂️ What Gets Uploaded

### ✅ Files Included (will be uploaded):

- All Python source files (`.py`)
- Documentation (`.md` files)
- Configuration files (`requirements.txt`, `.env.example`)
- Rules knowledge base (`rules_kb/*.json` - except large vector indexes)
- Test files (`tests/*.py`)
- Input case studies (`inputs/case_studies/*.json`)

### ❌ Files Excluded (won't be uploaded):

- Virtual environment (`venv/`)
- Database files (`*.db`)
- Output files (`outputs/`)
- Logs (`.log`, `.jsonl`)
- Trained RL models (`*.zip`)
- Vector indexes (`faiss_index*/`)
- Geometry files (`*.stl`)
- Python cache (`__pycache__/`)
- IDE settings (`.vscode/`, `.idea/`)

These exclusions are defined in `.gitignore` to keep the repository clean and lightweight.

---

## 🔄 Making Updates After Initial Push

When you make changes to the project:

```powershell
# Check what changed
git status

# Add specific files
git add <filename>

# Or add all changes
git add .

# Commit with a descriptive message
git commit -m "Add feature: city-adaptive feedback system"

# Push to GitHub
git push
```

---

## 🌿 Recommended Repository Structure on GitHub

After pushing, your repository should look like this:

```
ai-rule-intelligence-platform/
├── .gitignore
├── README.md (rename README_GITHUB.md to README.md)
├── requirements.txt
├── LICENSE (add if needed)
├── DELIVERABLES_SUMMARY.md
├── handover_v2.md
├── agents/
├── rl_env/
├── rules_kb/
├── tests/
└── ... (other files)
```

---

## 📄 Optional: Add a LICENSE

1. Go to your repository on GitHub
2. Click **"Add file"** → **"Create new file"**
3. Name it `LICENSE`
4. Click **"Choose a license template"**
5. Select **MIT License** (recommended for open source)
6. Fill in your name and year
7. Click **"Commit new file"**

---

## 🏷️ Optional: Add Topics/Tags

On your GitHub repository page:

1. Click the **⚙️ (gear icon)** next to "About"
2. Add topics:
   - `ai`
   - `machine-learning`
   - `reinforcement-learning`
   - `fastapi`
   - `urban-planning`
   - `building-regulations`
   - `rest-api`
   - `streamlit`
3. Click **"Save changes"**

---

## 📊 Optional: Create GitHub Actions (CI/CD)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python tests/test_pipeline.py
        python tests/test_calculators.py
```

---

## 🎯 After Successful Upload

Your repository will be available at:
```
https://github.com/YOUR_USERNAME/ai-rule-intelligence-platform
```

Share this URL with:
- Frontend team (Yash, Nipun, Bhavesh, Anmol)
- Stakeholders
- Collaborators

---

## ✅ Verification Checklist

After pushing to GitHub, verify:

- [ ] All source files are visible
- [ ] README displays correctly
- [ ] Documentation files are accessible
- [ ] .gitignore is working (no unwanted files)
- [ ] Repository description is set
- [ ] Topics/tags are added
- [ ] License is included (if applicable)

---

## 🆘 Troubleshooting

### Error: "Permission denied"
- Use Personal Access Token instead of password
- Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Error: "Large files"
- GitHub has a 100MB file size limit
- Check `.gitignore` is excluding large files
- Use `git lfs` for large files if needed

### Error: "Repository already exists"
- Use a different repository name
- Or delete the existing repository and recreate

---

## 📞 Need Help?

- GitHub Docs: https://docs.github.com
- Git Basics: https://git-scm.com/book/en/v2/Getting-Started-Git-Basics
- GitHub Support: https://support.github.com

---

**Ready to share your AI Rule Intelligence Platform with the world! 🚀**
