# Setup New GitHub Repository - Fresh Start
# This script will disconnect from the old repository and prepare for a new one

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting Up New GitHub Repository" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check current remote
Write-Host "Step 1: Checking current remote repository..." -ForegroundColor Yellow
git remote -v
Write-Host ""

# Step 2: Remove old remote
Write-Host "Step 2: Removing old remote 'origin'..." -ForegroundColor Yellow
git remote remove origin
Write-Host "✓ Old remote removed successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Verify removal
Write-Host "Step 3: Verifying remote removed..." -ForegroundColor Yellow
$remotes = git remote -v
if ([string]::IsNullOrWhiteSpace($remotes)) {
    Write-Host "✓ No remotes configured - Ready for new repository" -ForegroundColor Green
} else {
    Write-Host "⚠ Still has remotes:" -ForegroundColor Red
    git remote -v
}
Write-Host ""

# Step 4: Instructions for new repository
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to GitHub and create a NEW repository:" -ForegroundColor White
Write-Host "   https://github.com/new" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Suggested name: ai-rule-intelligence-platform" -ForegroundColor Yellow
Write-Host "   Description: AI-powered building compliance system with multi-city support" -ForegroundColor Yellow
Write-Host "   ✓ Make it Public or Private (your choice)" -ForegroundColor Yellow
Write-Host "   ✗ DO NOT initialize with README" -ForegroundColor Red
Write-Host "   ✗ DO NOT add .gitignore" -ForegroundColor Red
Write-Host ""
Write-Host "2. After creating the repository, run these commands:" -ForegroundColor White
Write-Host ""
Write-Host "   # Add new remote (replace YOUR_USERNAME and REPO_NAME)" -ForegroundColor Gray
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git" -ForegroundColor Cyan
Write-Host ""
Write-Host "   # Verify new remote" -ForegroundColor Gray
Write-Host "   git remote -v" -ForegroundColor Cyan
Write-Host ""
Write-Host "   # Push to new repository" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Ready for new repository!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
