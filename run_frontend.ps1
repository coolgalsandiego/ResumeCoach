# Frontend Startup Script for Resume Coach
Write-Host "Starting Resume Coach Frontend..." -ForegroundColor Green

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing npm dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

# Check if .env file exists
if (-not (Test-Path "frontend\.env")) {
    Write-Host "WARNING: frontend\.env file not found!" -ForegroundColor Yellow
    Write-Host "Creating frontend\.env file with default values..." -ForegroundColor Cyan
    "REACT_APP_API_URL=http://localhost:8000/api/v1" | Out-File -FilePath "frontend\.env" -Encoding utf8
}

# Start the development server
Write-Host ""
Write-Host "Starting React development server..." -ForegroundColor Green
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location frontend
npm start
