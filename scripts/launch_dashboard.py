"""
Interactive Dashboard Launcher
==============================
Opens the UAV-Based Vehicle Detection & Trajectory Analysis Dashboard
in the default web browser.

Supports both:
  - Redesigned Liquid Glass Dashboard: http://localhost:8000/
  - Preserved Classic Dashboard:        http://localhost:8000/dashboard/index.html

Usage:
  python scripts/launch_dashboard.py [--port 8000] [--classic] [--no-server]
"""

import argparse
import http.server
import os
import socketserver
import webbrowser


def main():
    parser = argparse.ArgumentParser(description="Launch Traffic Analysis Dashboard")
    parser.add_argument("--port", type=int, default=8000, help="Local HTTP server port (default: 8000)")
    parser.add_argument("--classic", action="store_true", help="Launch the original classic dashboard instead of the redesigned liquid glass UI")
    parser.add_argument("--no-server", action="store_true", help="Open local HTML file directly without server")
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    outputs_dir = os.path.join(project_root, "outputs")
    
    redesigned_file = os.path.join(outputs_dir, "index.html")
    classic_file = os.path.join(outputs_dir, "dashboard", "index.html")

    target_file = classic_file if args.classic else redesigned_file
    if not os.path.exists(target_file):
        print(f"ERROR: Dashboard file not found at: {target_file}")
        return

    if args.no_server:
        print(f"Opening dashboard directly in default browser: {target_file}")
        webbrowser.open(f"file://{target_file}")
        return

    # Serve outputs directory as root so /analysis, /safety_analysis, /calibration, /dashboard resolve
    os.chdir(outputs_dir)
    handler = http.server.SimpleHTTPRequestHandler
    
    # Enable address reuse to avoid WinError 10048 when restarting quickly
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            target_url = f"http://localhost:{args.port}/dashboard/index.html" if args.classic else f"http://localhost:{args.port}/"
            
            print("=" * 70)
            print(" UAV-Based Vehicle Detection & Trajectory Analysis - Dashboard Server ")
            print("=" * 70)
            print(f" * Liquid Glass UI (New Redesign) : http://localhost:{args.port}/")
            print(f" * Classic Dashboard (Preserved)  : http://localhost:{args.port}/dashboard/index.html")
            print(f" * Serving Directory              : {os.getcwd()}")
            print("-" * 70)
            print(f" Launching: {target_url}")
            print(" Press Ctrl+C in terminal to stop server.")
            print("=" * 70)
            
            webbrowser.open(target_url)
            httpd.serve_forever()
    except OSError as e:
        print(f"Port {args.port} busy or unavailable ({e}). Opening HTML directly...")
        webbrowser.open(f"file://{target_file}")


if __name__ == "__main__":
    main()
