#!/bin/bash
# WO-47: Test provenance API and UI availability.
# Run from project root: bash scripts/test-provenance-ui.sh
# Prerequisites: backend on :8002, Neo4j running

set -e
cd "$(dirname "$0")/.."

echo "=== Provenance API Tests ==="
echo ""

# 1. Health check (Neo4j status)
echo "1. Health / Neo4j status:"
curl -s http://localhost:8002/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
neo = d.get('neo4j', '?')
print(f'   Neo4j: {neo}')
if neo != 'ok':
    print('   WARNING: Neo4j unavailable - provenance endpoints will return 503')
" 2>/dev/null || echo "   Backend not reachable on :8002"

# 2. Provenance status
echo ""
echo "2. Provenance status:"
curl -s http://localhost:8002/api/provenance/status | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'   Available: {d.get(\"available\", \"?\")}')
if d.get('error'):
    print(f'   Error: {d[\"error\"]}')
" 2>/dev/null || echo "   Failed"

# 3. Get first theory ID and test lineage
echo ""
echo "3. Theory lineage (first theory):"
THEORY_ID=$(curl -s "http://localhost:8002/api/theories?limit=1" | python3 -c "
import sys, json
d = json.load(sys.stdin)
items = d if isinstance(d, list) else d.get('items', d.get('data', []))
print(items[0]['id'] if items else '')
" 2>/dev/null)
if [ -n "$THEORY_ID" ]; then
  curl -s "http://localhost:8002/api/provenance/theory/$THEORY_ID/lineage" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'   Theory: {d.get(\"theory_id\", \"?\")[:8]}…')
print(f'   Simulations: {len(d.get(\"simulation_ids\", []))}')
print(f'   Publications: {len(d.get(\"publication_ids\", []))}')
" 2>/dev/null || echo "   Failed"
else
  echo "   No theories in DB - create one first"
fi

echo ""
echo "=== UI Verification ==="
echo "1. Open http://localhost:5173/theories"
echo "2. Click a theory → see Provenance (Neo4j) with verification icon and Export JSON"
echo "3. Open Settings (gear) → Provenance section → toggle Show export / Verification"
echo "4. Export JSON → downloads provenance-*.json"
echo ""
