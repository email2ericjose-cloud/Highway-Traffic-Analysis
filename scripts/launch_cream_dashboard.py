"""
Dedicated Independent Server Launcher for UAV Traffic Studio Dashboard
======================================================================
Hosts the newly built UAV-Based Vehicle Detection & Trajectory Analysis Studio
on an independent domain/port (default: http://localhost:8080/) while keeping
the original dashboard active on http://localhost:8000/.

Usage:
  python scripts/launch_cream_dashboard.py [--port 8080] [--no-browser]
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.server import run_server


def main():
    parser = argparse.ArgumentParser(description="Launch Independent UAV Traffic Studio Server")
    parser.add_argument("--port", type=int, default=8080, help="Dedicated HTTP server port (default: 8080)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    run_server(port=args.port, host=args.host, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
