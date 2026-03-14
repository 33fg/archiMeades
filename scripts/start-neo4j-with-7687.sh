#!/bin/bash
# Stop any existing Neo4j, start ours with port 7687 exposed.
# Run from project root: ./scripts/start-neo4j-with-7687.sh
# Requires: Docker Desktop running

set -e
cd "$(dirname "$0")/.."

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running. Start Docker Desktop first."
  exit 1
fi

echo "Stopping existing Neo4j containers..."
for id in $(docker ps -q --filter "name=neo4j" 2>/dev/null); do docker stop "$id" 2>/dev/null; done
for id in $(docker ps -aq --filter "name=neo4j" 2>/dev/null); do docker rm "$id" 2>/dev/null; done

echo "Starting Neo4j from Archimedes docker-compose (ports 7474 + 7687)..."
docker compose up -d neo4j

echo "Waiting 30s for Neo4j to accept connections..."
sleep 30

echo ""
echo "Port check:"
docker compose port neo4j 7687 2>/dev/null && echo "7688 (Bolt) is exposed" || echo "WARNING: Bolt port not exposed"

echo ""
echo "Provenance status:"
curl -s http://localhost:8002/api/provenance/status 2>/dev/null | python3 -m json.tool || echo "Backend not running - start with: npm run dev"
