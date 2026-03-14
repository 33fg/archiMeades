#!/bin/bash
# Start backend and frontend with auto-reload. Backend restarts on code changes.
# From project root: ./scripts/start-dev.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Kill existing processes on our ports
for port in 8002 5175; do
  lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null || true
done

# Start backend with --reload (auto-restart on code changes)
cd backend
AWS_ENDPOINT_URL=http://localhost:4566 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Backend: http://localhost:8002 (PID $BACKEND_PID)"
echo "Frontend: http://localhost:5175 (PID $FRONTEND_PID)"
echo "Press Ctrl+C to stop both"
wait
