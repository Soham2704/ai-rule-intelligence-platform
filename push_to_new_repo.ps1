# Push to New Repository - Final Commands
# Repository: https://github.com/Soham2704/ai-rule-intelligence-platform.git

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing to New Repository" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Remove old remote
Write-Host "Step 1: Removing old remote..." -ForegroundColor Yellow
git remote remove origin
Write-Host "✓ Old remote removed" -ForegroundColor Green
Write-Host ""

# Step 2: Add new remote
Write-Host "Step 2: Adding new remote..." -ForegroundColor Yellow
git remote add origin https://github.com/Soham2704/ai-rule-intelligence-platform.git
Write-Host "✓ New remote added" -ForegroundColor Green
Write-Host ""

# Step 3: Verify remote
Write-Host "Step 3: Verifying remote..." -ForegroundColor Yellow
git remote -v
Write-Host ""

# Step 4: Push to new repository
Write-Host "Step 4: Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Successfully pushed to new repository!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your repository URL:" -ForegroundColor White
Write-Host "https://github.com/Soham2704/ai-rule-intelligence-platform" -ForegroundColor Cyan
