#!/usr/bin/env bash
# End-to-end test: submit MCMC job and verify it completes.
# Prereqs: Redis running (docker compose up -d redis)
#          Backend and worker running (npm run dev, or backend + celery:worker)

set -e
API="${API:-http://localhost:8002}"

echo "=== MCMC Job E2E Test ==="
echo "API: $API"
echo ""

# Health check
echo "[1] Health check..."
curl -sf "$API/health" > /dev/null || { echo "FAIL: API not reachable"; exit 1; }
echo "OK"
echo ""

# Submit job (minimal: 50 samples, 25 warmup, 1 chain for speed)
echo "[2] Submitting MCMC job..."
RESP=$(curl -sf -X POST "$API/api/jobs/submit" \
  -H "Content-Type: application/json" \
  -d '{"job_type":"mcmc","priority":"batch","payload":{"num_samples":50,"num_warmup":25,"num_chains":1,"prior_spec":{"omega_m":{"type":"uniform","low":0.2,"high":0.5},"h0":{"type":"uniform","low":65,"high":75}}}}')
JOB_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
TASK_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('celery_task_id',''))")
echo "Job ID: $JOB_ID"
echo "Celery Task ID: $TASK_ID"
echo ""

# Poll for completion (max 120s)
echo "[3] Polling for completion (50 samples should take ~30-60s)..."
for i in $(seq 1 60); do
  STATUS=$(curl -sf "$API/api/jobs/$JOB_ID/status" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'], d.get('progress_percent',0))" 2>/dev/null || echo "error 0")
  S=$(echo "$STATUS" | cut -d' ' -f1)
  P=$(echo "$STATUS" | cut -d' ' -f2)
  printf "\r  [%ds] status=%s progress=%s%%   " $((i*2)) "$S" "$P"
  case "$S" in
    completed) echo ""; echo "OK - Job completed!"; exit 0 ;;
    failed) echo ""; echo "FAIL - Job failed"; curl -sf "$API/api/jobs/$JOB_ID/status" | python3 -m json.tool; exit 1 ;;
  esac
  sleep 2
done

echo ""
echo "FAIL - Job did not complete within 120s"
exit 1
