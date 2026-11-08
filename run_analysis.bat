@echo off
setlocal enabledelayedexpansion
title UAV Traffic Analysis - Runner

cd /d "%~dp0"

echo =====================================================================
echo    UAV-Based Vehicle Detection and Trajectory Analysis
echo =====================================================================
echo.

:: Check environment
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found! Please run 'setup.bat' first.
    echo.
    pause
    exit /b 1
)

call .\.venv\Scripts\activate.bat

:: Prompt for video path
echo Drag and drop your video file here, or type the file path:
set /p VIDEO_PATH="Video Path: "

:: Remove surrounding quotes if user dragged and dropped
set VIDEO_PATH=%VIDEO_PATH:"=%

if "%VIDEO_PATH%"=="" (
    echo [INFO] No video entered, using default: videos\National Highway 48.mp4
    set VIDEO_PATH=videos\National Highway 48.mp4
)

if not exist "%VIDEO_PATH%" (
    echo [ERROR] Video file does not exist: %VIDEO_PATH%
    echo.
    pause
    exit /b 1
)

:: Prompt for lane width
echo.
echo Enter assumed lane or highway width in metres (press Enter for default 3.5m):
set /p LANE_WIDTH="Lane Width (m) [3.5]: "
if "%LANE_WIDTH%"=="" set LANE_WIDTH=3.5

echo.
echo =====================================================================
echo  Starting Pipeline:
echo    Video     : %VIDEO_PATH%
echo    Lane Width: %LANE_WIDTH% m
echo =====================================================================
echo.

python run_pipeline.py --video "%VIDEO_PATH%" --lane-width %LANE_WIDTH%

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Analysis pipeline finished with an error.
    pause
    exit /b %errorlevel%
)

echo.
echo =====================================================================
echo  Analysis Finished!
echo =====================================================================
echo.
set /p OPEN_DASH="Open dashboard now in browser? (Y/N) [Y]: "
if /i "%OPEN_DASH%"=="" set OPEN_DASH=Y
if /i "%OPEN_DASH%"=="Y" (
    start "" launch_dashboard.bat
)

pause
