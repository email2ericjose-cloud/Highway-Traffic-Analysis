"""
Dedicated Full-Stack HTTP & REST API Server
===========================================
Hosts the UAV-Based Vehicle Detection & Trajectory Analysis Suite.
Serves the modern frontend, exposes live REST APIs, and runs background pipeline jobs.

Usage:
    python app/server.py [--port 8080] [--host 127.0.0.1] [--no-browser]
"""

import argparse
import http.server
import json
import os
import socketserver
import sys
import urllib.parse
import webbrowser
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api.data_provider import DataProvider
from app.api.pipeline_runner import PipelineRunner


class StudioServerHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler serving static files and JSON REST APIs.
    """
    def __init__(self, *args, **kwargs):
        self.app_dir = Path(__file__).resolve().parent
        self.static_dir = self.app_dir / "static"
        self.outputs_dir = PROJECT_ROOT / "outputs"
        self.data_provider = DataProvider(root_dir=str(PROJECT_ROOT))
        self.pipeline_runner = PipelineRunner()
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def _send_json(self, data: any, status_code: int = 200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, file_path: Path, content_type: str = "text/html"):
        if not file_path.is_file():
            self.send_error(404, f"File not found: {file_path.name}")
            return
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8" if "text" in content_type or "json" in content_type or "javascript" in content_type else content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error serving file: {e}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # ── REST API ROUTES ─────────────────────────────────────────────────
        if path == "/api/status":
            return self._send_json(self.data_provider.get_status())

        if path == "/api/metrics":
            return self._send_json(self.data_provider.get_metrics())

        if path == "/api/conflicts":
            tier = query.get("tier", [None])[0]
            search = query.get("search", [None])[0]
            return self._send_json(self.data_provider.get_conflicts(tier=tier, search=search))

        if path == "/api/critical-distances":
            return self._send_json(self.data_provider.get_critical_distances())

        if path == "/api/hotspots":
            return self._send_json(self.data_provider.get_hotspots())

        if path == "/api/trajectories":
            return self._send_json(self.data_provider.get_trajectories())

        if path == "/api/pipeline/status":
            return self._send_json(self.pipeline_runner.get_status())

        # ── FRONTEND & STATIC ASSET ROUTES ──────────────────────────────────
        if path in ["/", "/index.html", "/studio", "/app"]:
            return self._serve_file(self.static_dir / "index.html", "text/html")

        # Static assets inside app/static/
        if path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            target = self.static_dir / rel_path
            mime = "text/plain"
            if rel_path.endswith(".css"):
                mime = "text/css"
            elif rel_path.endswith(".js"):
                mime = "application/javascript"
            elif rel_path.endswith(".svg"):
                mime = "image/svg+xml"
            elif rel_path.endswith(".png"):
                mime = "image/png"
            elif rel_path.endswith(".jpg") or rel_path.endswith(".jpeg"):
                mime = "image/jpeg"
            return self._serve_file(target, mime)

        # Static assets in outputs/ or root
        # Check if mapped to outputs/
        if path.startswith("/outputs/"):
            subpath = path[len("/outputs/"):]
            target = self.outputs_dir / subpath
            if target.is_file():
                return super().do_GET()

        # Handle direct media paths from outputs
        direct_target = self.outputs_dir / path.lstrip("/")
        if direct_target.is_file():
            # Rewrite path to outputs/ direct
            self.path = f"/outputs/{path.lstrip('/')}"
            return super().do_GET()

        # Fallback to default SimpleHTTPRequestHandler for root files
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/pipeline/run":
            length = int(self.headers.get("Content-Length", 0))
            payload = {}
            if length > 0:
                try:
                    payload = json.loads(self.rfile.read(length).decode("utf-8"))
                except Exception:
                    pass

            video_path = payload.get("video", "videos/National Highway 48.mp4")
            lane_width = float(payload.get("lane_width", 3.5))
            skip_tracking = bool(payload.get("skip_tracking", True))

            result = self.pipeline_runner.start_pipeline(
                video_path=video_path,
                lane_width=lane_width,
                skip_tracking=skip_tracking
            )
            return self._send_json(result, 200 if result.get("success") else 400)

        self.send_error(404, "Endpoint not found")


def run_server(port: int = 8080, host: str = "127.0.0.1", open_browser: bool = True):
    socketserver.TCPServer.allow_reuse_address = True
    server_address = (host, port)
    
    try:
        with socketserver.TCPServer(server_address, StudioServerHandler) as httpd:
            url = f"http://localhost:{port}/"
            print("=" * 76)
            print("  UAV-BASED VEHICLE DETECTION & TRAJECTORY ANALYSIS STUDIO")
            print("  Civil Engineering & Geoinformatics Research Platform | Eric Jose")
            print("=" * 76)
            print(f"  * Dedicated Application URL : {url}")
            print(f"  * REST API Status Endpoint   : {url}api/status")
            print(f"  * Preserved Dark UI (v2.0)   : http://localhost:8000/")
            print(f"  * Preserved Classic UI       : http://localhost:8000/dashboard/index.html")
            print(f"  * Application Root Directory : {PROJECT_ROOT}")
            print("-" * 76)
            print("  Server is actively listening. Press Ctrl+C in terminal to stop.")
            print("=" * 76)

            if open_browser:
                webbrowser.open(url)
            httpd.serve_forever()
    except OSError as e:
        print(f"[ERROR] Port {port} is unavailable ({e}).")


def main():
    parser = argparse.ArgumentParser(description="Launch Standalone UAV Traffic Analysis Studio Server")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    run_server(port=args.port, host=args.host, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
