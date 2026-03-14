#!/bin/bash
# Start DGX Heartbeat on the DGX machine. Simple /health endpoint.
cd "$(dirname "$0")/../dgx_orchestrator"
python main.py
