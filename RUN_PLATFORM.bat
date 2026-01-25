@echo off
echo ================================================
echo   HIRESIGHT PLATFORM - Quick Run
echo ================================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   1. Open PowerShell in this folder
    echo   2. Run: .\setup_and_run.ps1
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting platform...
echo.
python platform_app.py

pause
