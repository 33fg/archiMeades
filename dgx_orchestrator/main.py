"""DGX Heartbeat - minimal health endpoint for Archimedes to detect DGX availability."""

import os

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="DGX Heartbeat")

HOST = os.getenv("DGX_HOST", "0.0.0.0")
PORT = int(os.getenv("DGX_PORT", "8000"))


@app.get("/health")
def health():
    """Simple heartbeat - Archimedes polls this."""
    return {"status": "ok", "at_capacity": False, "cluster_size": 1}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
