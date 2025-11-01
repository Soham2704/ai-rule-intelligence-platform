# GitHub Repository Setup - Quick Commands
# Copy and paste these commands in PowerShell (in the BLACKHOLE directory)

# Step 1: Initialize git repository
Write-Host "Initializing Git repository..." -ForegroundColor Green
git init

# Step 2: Add all files
Write-Host "Adding files to git..." -ForegroundColor Green
git add .

# Step 3: Check status
Write-Host "Checking git status..." -ForegroundColor Green
git status

# Step 4: Create initial commit
Write-Host "Creating initial commit..." -ForegroundColor Green
git commit -m "Initial commit: AI Rule Intelligence Platform with multi-city support and REST API"

# Step 5: Add remote (UPDATE THIS WITH YOUR GITHUB USERNAME!)
Write-Host "IMPORTANT: Update the command below with your GitHub username!" -ForegroundColor Yellow
Write-Host "Replace YOUR_USERNAME with your actual GitHub username" -ForegroundColor Yellow
Write-Host ""
Write-Host "Command to run:" -ForegroundColor Cyan
Write-Host "git remote add origin https://github.com/YOUR_USERNAME/ai-rule-intelligence-platform.git" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter after you've updated and run the above command"

# Step 6: Verify remote
Write-Host "Verifying remote..." -ForegroundColor Green
git remote -v

# Step 7: Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Green
git branch -M main
git push -u origin main

Write-Host "Done! Check your GitHub repository." -ForegroundColor Green
