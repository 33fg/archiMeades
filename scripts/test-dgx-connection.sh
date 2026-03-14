#!/bin/bash
# Test DGX heartbeat connectivity from this machine.
DGX="${DGX_HOST:-10.88.111.9}"
echo "Testing connection to $DGX:8000/health..."
curl -v --connect-timeout 5 "http://$DGX:8000/health" 2>&1 || echo "Connection failed"
