#!/usr/bin/env bash
# Celery worker startup for local development.
# WO-12: Set Up Celery Task Queue with Redis
#
# Prerequisites: Redis running (localhost:6379), activate venv
# Usage: ./scripts/celery-worker.sh [worker|beat|both]
#
# - worker: Run Celery worker only
# - beat: Run Celery Beat scheduler only
# - both: Run worker and beat (default)

set -e
# Run from backend (where app and celery_app live)
cd "$(dirname "$0")/../backend"
CMD="${1:-both}"

if [ "$CMD" = "worker" ]; then
  exec celery -A app.celery_app worker -l info
elif [ "$CMD" = "beat" ]; then
  exec celery -A app.celery_app beat -l info
elif [ "$CMD" = "both" ]; then
  # Run worker in background, beat in foreground
  celery -A app.celery_app worker -l info &
  WORKER_PID=$!
  trap "kill $WORKER_PID 2>/dev/null" EXIT
  exec celery -A app.celery_app beat -l info
else
  echo "Usage: $0 [worker|beat|both]"
  exit 1
fi
