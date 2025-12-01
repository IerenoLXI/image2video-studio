# Backend Startup Script
Write-Host "Starting Backend Server..." -ForegroundColor Green

# Navigate to backend directory
Set-Location -Path "backend"

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    pause
    exit
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env file with placeholder values..." -ForegroundColor Yellow
    $envContent = @"
A2E_TOKEN=your_a2e_api_key_here
DID_KEY=your_did_api_key_here
HEYGEN_KEY=your_heygen_api_key_here
"@
    $envContent | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "Created .env file. Please update it with your API keys." -ForegroundColor Green
}

# Start the server
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs available at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn main:app --reload --port 8000
