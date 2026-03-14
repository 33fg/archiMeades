#!/bin/bash
# Kill whatever is on 8002 and 5173, then start backend + frontend on those ports.
cd "$(dirname "$0")/.."

echo "Killing processes on ports 8002 and 5173..."
for port in 8002 5173; do
  pids=$(lsof -ti :$port 2>/dev/null)
  if [ -n "$pids" ]; then
    kill -9 $pids 2>/dev/null
    echo "  Killed port $port"
  fi
done
sleep 3

echo ""
echo "Starting backend on :8002 and frontend on :5173..."
exec npm run start
