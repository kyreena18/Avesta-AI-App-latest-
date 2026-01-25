# Quick dependency installer for virtual environment
# Run this after activating .venv

Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

pip install chromadb==0.5.5 sentence-transformers==2.2.2 "transformers<4.35.0" "huggingface_hub<0.20.0" numpy scikit-learn python-dotenv PyPDF2 python-docx Flask

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Now run: python platform_app.py" -ForegroundColor Yellow
