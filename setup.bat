@echo off
setlocal enabledelayedexpansion
title UAV-Based Vehicle Detection and Trajectory Analysis - Installer

echo =====================================================================
echo  UAV-Based Vehicle Detection and Trajectory Analysis - Setup
echo =====================================================================
echo.

cd /d "%~dp0"

:: 1. Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10, 3.11, 3.12, or 3.13 from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%a in ('python --version 2^>^&1') do set PY_VER=%%a
echo       Found Python %PY_VER%

:: 2. Setup Virtual Environment
echo.
echo [2/4] Setting up virtual environment (.venv)...
if not exist ".venv\Scripts\python.exe" (
    echo       Creating new virtual environment in .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
) else (
    echo       Virtual environment already exists in .venv.
)

:: 3. Install Package and Dependencies
echo.
echo [3/4] Installing dependencies and package...
call .\.venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps

if %errorlevel% neq 0 (
    echo [ERROR] Package installation encountered an error.
    pause
    exit /b 1
)

:: 4. Verify Installation
echo.
echo [4/4] Verifying installation...
python -c "import uav_vehicle_analysis; print('       [OK] uav_vehicle_analysis version:', uav_vehicle_analysis.__doc__.strip().splitlines()[0])"
.\.venv\Scripts\uav-pipeline.exe --help >nul 2>&1
if %errorlevel% equ 0 (
    echo       [OK] Command 'uav-pipeline' is ready to use!
)

echo.
echo =====================================================================
echo  Setup Completed Successfully!
echo =====================================================================
echo.
echo How to use:
echo   1. Double-click 'run_analysis.bat' to analyze any drone video
echo   2. Double-click 'launch_dashboard.bat' to view results in browser
echo   3. CLI Command: uav-pipeline --video "videos\your_video.mp4" --lane-width 3.5
echo.
pause
