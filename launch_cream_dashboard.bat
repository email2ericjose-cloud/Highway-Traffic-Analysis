@echo off
title UAV Traffic Analysis - Cream Scientific Dashboard (Separate Domain)
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call .\.venv\Scripts\activate.bat
    python scripts\launch_cream_dashboard.py --port 8080
) else (
    start "" "outputs\cream\index.html"
)
