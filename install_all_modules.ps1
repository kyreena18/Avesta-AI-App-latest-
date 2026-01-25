# Install all required modules for platform_app.py

Write-Host "Installing required modules..." -ForegroundColor Yellow

$modules = @(
    "Flask",
    "chromadb",
    "sentence-transformers",
    "PyPDF2",
    "python-docx"
)

foreach ($module in $modules) {
    Write-Host "Installing $module..." -ForegroundColor Gray
    pip install $module --quiet
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Run: python check_modules.py to verify" -ForegroundColor Yellow
Write-Host "Then: python platform_app.py to start" -ForegroundColor Yellow
