#!/bin/bash
# Docker cleanup - remove stopped containers, unused images, volumes.
# Run from project root: ./scripts/docker-cleanup.sh
# Use --project to only clean Archimedes containers/volumes.

set -e
cd "$(dirname "$0")/.."

PROJECT_ONLY=false
[ "$1" = "--project" ] && PROJECT_ONLY=true

echo "=== Docker cleanup ==="

if [ "$PROJECT_ONLY" = true ]; then
  echo "Stopping Archimedes containers and removing volumes..."
  docker compose down -v 2>/dev/null || true
  echo "Done (project only)."
else
  echo "Stopping Archimedes containers and volumes..."
  docker compose down -v 2>/dev/null || true
  
  echo "Pruning stopped containers..."
  docker container prune -f
  
  echo "Pruning dangling images..."
  docker image prune -f
  
  echo "Pruning unused volumes..."
  docker volume prune -f
  
  echo "Pruning unused networks..."
  docker network prune -f
  
  echo ""
  echo "Cleanup complete. Disk usage:"
  docker system df
fi
