import urllib.request
import threading
import time
import socketserver
import http.server
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT / "outputs")

socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("127.0.0.1", 8096), http.server.SimpleHTTPRequestHandler)

server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
server_thread.start()
time.sleep(0.5)

url = "http://127.0.0.1:8096/dashboard/index.html"
try:
    req = urllib.request.urlopen(url, timeout=3)
    content = req.read().decode("utf-8")
    print("HTTP Status:", req.getcode())
    print("Content Length:", len(content))
    checks = [
        "UAV TRAFFIC STUDIO",
        "Developed by Eric Jose",
        "tab-overview",
        "tab-video",
        "tab-flow",
        "tab-trajectory",
        "tab-safety",
        "tab-hotspots",
        "tab-pipeline",
        "tab-reports",
        "EMBEDDED_CRITICAL_DATA",
        "warm-cream",
        "data-glass"
    ]
    all_ok = True
    for c in checks:
        if c in content:
            print(f"  PASS: found '{c}'")
        else:
            print(f"  FAIL: NOT found '{c}'")
            all_ok = False
    print("Overall result:", "SUCCESS" if all_ok else "FAILURE")
except Exception as e:
    print("ERROR:", e)

httpd.shutdown()
httpd.server_close()
