#!/bin/bash
# Fix Neo4j: stop conflicts, reset if needed, start Archimedes Neo4j
set -e
cd "$(dirname "$0")/.."
LOG=/Users/jbarseneau/Archimedes/scripts/fix-neo4j.log
exec > "$LOG" 2>&1

echo "=== Stopping conflicting Neo4j containers ==="
docker stop neo4j-1 2>/dev/null || true
docker stop archimedes-neo4j-1 2>/dev/null || true
docker rm neo4j-1 2>/dev/null || true
docker rm archimedes-neo4j-1 2>/dev/null || true

echo "=== Stopping Archimedes Neo4j and removing volume ==="
docker compose stop neo4j 2>/dev/null || true
docker compose rm -f neo4j 2>/dev/null || true
docker volume rm archimedes_neo4j_data 2>/dev/null || true

echo "=== Starting Archimedes Neo4j ==="
docker compose up -d neo4j

echo "=== Waiting 20s for Neo4j to start ==="
sleep 20

echo "=== Verifying ports ==="
docker compose port neo4j 7687 || echo "7687 not exposed"
docker compose port neo4j 7474 || echo "7474 not exposed"

echo "=== Done. Log: $LOG"
