# Complete Project Startup Script
# This script starts both backend and frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Multi-Provider Image2Video Project" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if backend and frontend directories exist
if (-not (Test-Path "backend")) {
    Write-Host "Backend directory not found!" -ForegroundColor Red
    pause
    exit
}

if (-not (Test-Path "frontend")) {
    Write-Host "Frontend directory not found!" -ForegroundColor Red
    pause
    exit
}

Write-Host "Project structure verified" -ForegroundColor Green
Write-Host ""

# Start backend in a new window
Write-Host "Starting Backend Server..." -ForegroundColor Green
$backendScript = Join-Path $scriptPath "start-backend.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $backendScript

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host "Starting Frontend Server..." -ForegroundColor Green
$frontendScript = Join-Path $scriptPath "start-frontend.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $frontendScript

Write-Host ""
Write-Host "Both servers are starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to exit this window (servers will continue running)" -ForegroundColor Yellow
Read-Host | Out-Null
