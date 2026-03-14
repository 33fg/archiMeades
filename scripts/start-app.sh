#!/bin/bash
# Start Archimedes backend + frontend. Run from project root: ./scripts/start-app.sh
set -e
cd "$(dirname "$0")/.."

echo "Starting backend on :8002..."
(cd backend && AWS_ENDPOINT_URL=http://localhost:4566 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test NEO4J_URI=bolt://localhost:7688 NEO4J_USER=neo4j NEO4J_PASSWORD=gravitational ../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload) &

echo "Starting frontend on :5173..."
(cd frontend && npm run dev) &

echo ""
echo "Backend: http://localhost:8002"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."

wait
