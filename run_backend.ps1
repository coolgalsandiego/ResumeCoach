# Backend Startup Script for Resume Coach
Write-Host "Starting Resume Coach Backend..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "backend\venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv backend\venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "backend\venv\Scripts\Activate.ps1"

# Check if .env file exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "WARNING: backend\.env file not found!" -ForegroundColor Red
    Write-Host "Please create backend\.env file with your OpenAI API key." -ForegroundColor Yellow
    Write-Host "See SETUP_GUIDE.md for details." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to continue anyway, or Ctrl+C to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
$packages = & "backend\venv\Scripts\python.exe" -m pip list
if ($packages -notmatch "fastapi") {
    Write-Host "Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    & "backend\venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
    Write-Host "Downloading spaCy model..." -ForegroundColor Yellow
    & "backend\venv\Scripts\python.exe" -m spacy download en_core_web_sm
}

# Start the server
Write-Host ""
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

& "backend\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
