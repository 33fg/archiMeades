#!/bin/bash
# Start backend + frontend. Run `npm run services:start` first for DB, Redis, Neo4j, S3.
cd "$(dirname "$0")"

lsof -ti :8002 | xargs kill -9 2>/dev/null
lsof -ti :5173 | xargs kill -9 2>/dev/null
sleep 2

echo "Backend: http://localhost:8002 | Frontend: http://localhost:5173"
echo ""

(cd backend && AWS_ENDPOINT_URL=http://localhost:4566 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test NEO4J_URI=bolt://localhost:7688 NEO4J_USER=neo4j NEO4J_PASSWORD=gravitational ../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload) &
(cd frontend && npx vite --port 5173 --strictPort) &

wait
