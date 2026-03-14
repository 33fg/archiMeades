# DGX Connection Setup

ArchiMeades connects to the DGX heartbeat at `10.88.111.9:8000`.

## 1. Run the Heartbeat on the DGX Machine

### Option A: Deploy from your machine (no pip on DGX)

```bash
./scripts/deploy-dgx-heartbeat.sh --no-pip
```

Copies `scripts/run-dgx-heartbeat-standalone.py` to the DGX and runs it (stdlib only, no pip).

**Survives reboot:** Add `--install-systemd` to install as a systemd service:

```bash
DGX_SSH_PASSWORD='your-password' ./scripts/deploy-dgx-heartbeat.sh --no-pip --install-systemd
```

Requires sudo on the DGX. Env: `DGX_SSH_KEY`, `DGX_SSH_USER`, `DGX_SSH_PASSWORD`.

### Option B: One-liner (no pip, paste into SSH on DGX)

```bash
nohup python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/health':
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status':'ok','at_capacity':False,'cluster_size':1}).encode())
        else: self.send_response(404); self.end_headers()
    def log_message(self,*a): pass
HTTPServer(('0.0.0.0',8000),H).serve_forever()
" > /tmp/dgx.log 2>&1 &
```

### Option C: Full app (FastAPI + uvicorn)

```bash
cd dgx_orchestrator
pip install -r requirements.txt
python main.py
```

Or deploy from your machine: `./scripts/deploy-dgx-heartbeat.sh` (no `--no-pip`).

### Option D: Docker

```bash
cd dgx_orchestrator
docker compose up -d
```

## 2. Enable in ArchiMeades

In `backend/.env`:
```
DGX_ENABLED=true
DGX_BASE_URL=http://10.88.111.9:8000
```

Restart the backend.

## 3. Verify

Settings → DGX Cluster should show "Connected", "1 node".
