@echo off
REM Batch file to start the project (double-click friendly)
echo ========================================
echo   Multi-Provider Image2Video Project
echo ========================================
echo.

REM Check if PowerShell is available
powershell -Command "& {Get-Command powershell}" >nul 2>&1
if errorlevel 1 (
    echo Error: PowerShell is not available!
    pause
    exit /b 1
)

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0start-project.ps1"

pause

