# DGX Heartbeat

Minimal health endpoint for ArchiMeades to detect DGX availability. No Redis or other deps.

## Run on DGX

```bash
cd dgx_orchestrator
pip install -r requirements.txt
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Health Response

```json
{"status": "ok", "at_capacity": false, "cluster_size": 1}
```

## ArchiMeades Config

In backend `.env`:
```
DGX_ENABLED=true
DGX_BASE_URL=http://10.88.111.9:8000
```
