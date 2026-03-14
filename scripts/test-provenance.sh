#!/bin/bash
# Test Neo4j provenance connection. Run from project root.
# Prereqs: Docker running, Neo4j up (docker compose up -d neo4j), backend running (npm run dev or uvicorn)

set -e
cd "$(dirname "$0")/.."

echo "=== 1. Neo4j container ==="
docker compose ps neo4j 2>/dev/null || echo "Docker not running or neo4j not started"

echo ""
echo "=== 2. Provenance status ==="
curl -s http://localhost:8002/api/provenance/status | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8002/api/provenance/status

echo ""
echo "=== 3. Theories (get ID for lineage test) ==="
THEORIES=$(curl -s http://localhost:8002/api/theories)
echo "$THEORIES" | python3 -m json.tool 2>/dev/null || echo "$THEORIES"

THEORY_ID=$(echo "$THEORIES" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if d else '')" 2>/dev/null)
if [ -n "$THEORY_ID" ]; then
  echo ""
  echo "=== 4. Provenance lineage for $THEORY_ID ==="
  curl -s "http://localhost:8002/api/provenance/theory/$THEORY_ID/lineage" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:8002/api/provenance/theory/$THEORY_ID/lineage"
else
  echo ""
  echo "=== 4. No theories - create one in the UI first ==="
fi
