# HireSight Platform Setup Script
# This script creates a clean virtual environment and installs dependencies

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  HIRESIGHT PLATFORM - Setup Script" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create virtual environment
Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "   Virtual environment already exists. Removing old one..." -ForegroundColor Gray
    Remove-Item -Recurse -Force .venv
}
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "   ✓ Virtual environment created" -ForegroundColor Green

# Step 2: Activate virtual environment
Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "   Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}
Write-Host "   ✓ Virtual environment activated" -ForegroundColor Green

# Step 3: Upgrade pip
Write-Host "[3/4] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "   ✓ Pip upgraded" -ForegroundColor Green

# Step 4: Install dependencies
Write-Host "[4/4] Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
Write-Host "   Installing: chromadb, sentence-transformers, Flask, etc..." -ForegroundColor Gray
pip install chromadb==0.5.5 sentence-transformers==2.2.2 "transformers<4.35.0" "huggingface_hub<0.20.0" numpy scikit-learn python-dotenv PyPDF2 python-docx Flask --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "   WARNING: Some packages may have issues, but continuing..." -ForegroundColor Yellow
}
Write-Host "   ✓ Dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the platform, use:" -ForegroundColor Yellow
Write-Host "  python platform_app.py" -ForegroundColor White
Write-Host ""
Write-Host "Then open your browser to: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
