@echo off
title UAV Traffic Analysis - Dashboard Launcher
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call .\.venv\Scripts\activate.bat
    python scripts\launch_dashboard.py
) else (
    start "" "outputs\index.html"
)
