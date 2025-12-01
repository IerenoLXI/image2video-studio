# Frontend Startup Script
Write-Host "Starting Frontend Server..." -ForegroundColor Green

# Navigate to frontend directory
Set-Location -Path "frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies!" -ForegroundColor Red
        pause
        exit
    }
}

# Start the development server
Write-Host "Starting Vite development server..." -ForegroundColor Green
Write-Host "Frontend will be available at http://localhost:3000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

npm run dev
