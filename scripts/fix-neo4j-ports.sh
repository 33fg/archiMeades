#!/bin/bash
# Restart Neo4j with port 7687 (Bolt) exposed. The backend needs 7687, not just 7474.
# Run from project root: ./scripts/fix-neo4j-ports.sh

set -e
cd "$(dirname "$0")/.."

echo "Stopping existing Neo4j..."
docker compose stop neo4j 2>/dev/null || true

echo "Starting Neo4j with ports 7474 (browser) and 7687 (Bolt)..."
docker compose up -d neo4j

echo "Waiting for Neo4j to be ready (30s)..."
sleep 30

echo "Checking port 7687..."
if nc -z 127.0.0.1 7687 2>/dev/null; then
  echo "Port 7687 is open."
else
  echo "WARNING: Port 7687 still not reachable. Try: docker compose port neo4j 7687"
fi

echo "Done. Test: curl http://localhost:8002/api/provenance/status"
