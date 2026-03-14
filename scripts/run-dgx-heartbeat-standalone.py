#!/usr/bin/env python3
"""Minimal heartbeat - no deps. Run on DGX: python3 run-dgx-heartbeat-standalone.py"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status":"ok","at_capacity":False,"cluster_size":1}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *a): pass

HTTPServer(("0.0.0.0", 8000), H).serve_forever()
