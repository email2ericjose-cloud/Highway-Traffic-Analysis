@echo off
title UAV Traffic Studio - Standalone Research Platform
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call .\.venv\Scripts\activate.bat
    python scripts\launch_studio.py --port 8080
) else (
    echo Python virtual environment not found. Running with system Python...
    python scripts\launch_studio.py --port 8080
)
