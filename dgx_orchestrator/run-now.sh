#!/bin/bash
# Run heartbeat immediately on DGX - no pip install. Paste this into SSH session on DGX:
python3 -c '
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
    def log_message(self,*a): pass
print("Heartbeat on :8000 - Ctrl+C to stop")
HTTPServer(("0.0.0.0",8000),H).serve_forever()
'
