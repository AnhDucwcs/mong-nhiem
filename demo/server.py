"""Lightweight Local Demo Server for Mộng Nhiễm Living World.

Zero external dependencies. 100% Python Standard Library.
Serves the HTML5 Canvas visual observability dashboard on port 8765.
"""

from __future__ import annotations

import http.server
import os
import socketserver
import sys
import webbrowser
from pathlib import Path

PORT = int(os.environ.get("DEMO_PORT", "8765"))
STATIC_DIR = Path(__file__).resolve().parent / "static"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Quiet HTTP request handler that serves files from demo/static."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:
        # Keep console output clean
        if "404" in format % args or "500" in format % args:
            sys.stderr.write(f"[Demo Server Warning] {format % args}\n")


def run_server() -> None:
    """Launches the demo web server and prints access URL."""
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), QuietHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print(f"\n========================================================")
        print(f" Mong Nhiem Living World Observability Dashboard Running")
        print(f" Access URL: {url}")
        print(f" Press Ctrl+C to terminate.")
        print(f"========================================================\n")
        
        # Auto-launch browser if interactive
        if "--no-browser" not in sys.argv:
            try:
                webbrowser.open(url)
            except Exception:
                pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down demo server.")
            httpd.server_close()


if __name__ == "__main__":
    run_server()
