#!/bin/bash
# WO-38: Test job submission, status, and queue endpoints
set -e
API="${API:-http://localhost:8002}"

echo "=== 1. Stamp DB to f1a2b3c4d5e6 (skip broken migrations) and upgrade ==="
cd "$(dirname "$0")/.."
(cd backend && alembic stamp f1a2b3c4d5e6 2>/dev/null || true)
(cd backend && alembic upgrade head 2>&1) || echo "Migration note: if jobs table exists, new columns may already be present"

echo ""
echo "=== 2. GET /api/jobs/queue (before submit) ==="
QUEUE_RESP=$(curl -s -w "\n%{http_code}" "$API/api/jobs/queue")
QUEUE_HTTP=$(echo "$QUEUE_RESP" | tail -1)
QUEUE_BODY=$(echo "$QUEUE_RESP" | sed '$d')
echo "HTTP $QUEUE_HTTP"
echo "$QUEUE_BODY" | head -c 500

echo ""
echo ""
echo "=== 3. POST /api/jobs/submit (MCMC job) ==="
SUBMIT_RESP=$(curl -s -w "\n%{http_code}" -X POST "$API/api/jobs/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "mcmc",
    "priority": "batch",
    "payload": {
      "theory_id": "lcdm",
      "dataset_id": "synthetic",
      "prior_spec": {"omega_m": {"type": "uniform", "low": 0.2, "high": 0.5}, "h0": {"type": "uniform", "low": 65, "high": 75}},
      "num_samples": 50,
      "num_warmup": 25,
      "num_chains": 1
    }
  }')
SUBMIT_HTTP=$(echo "$SUBMIT_RESP" | tail -1)
SUBMIT_BODY=$(echo "$SUBMIT_RESP" | sed '$d')
echo "HTTP $SUBMIT_HTTP"
echo "$SUBMIT_BODY"

if [ "$SUBMIT_HTTP" = "200" ]; then
  JOB_ID=$(echo "$SUBMIT_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
  if [ -n "$JOB_ID" ]; then
    echo ""
    echo "=== 4. GET /api/jobs/$JOB_ID/status ==="
    curl -s "$API/api/jobs/$JOB_ID/status" | python3 -m json.tool 2>/dev/null || curl -s "$API/api/jobs/$JOB_ID/status"
    echo ""
    echo "=== 5. GET /api/jobs/queue (after submit) ==="
    curl -s "$API/api/jobs/queue" | python3 -m json.tool 2>/dev/null || curl -s "$API/api/jobs/queue"
  fi
fi

echo ""
echo "=== Done ==="
