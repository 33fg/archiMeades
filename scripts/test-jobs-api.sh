#!/usr/bin/env bash
# WO-12: Test jobs API - create, status, cancel.
# Prereqs: API on 8002, Celery worker running, Redis.

set -e
API="${API_URL:-http://localhost:8002}"
PASS=0
FAIL=0

run() {
  local name="$1"
  shift
  if "$@"; then
    echo "✅ $name"
    ((PASS++)) || true
    return 0
  else
    echo "❌ $name"
    ((FAIL++)) || true
    return 1
  fi
}

echo "=== Jobs API Tests ==="
echo

# 1. Health
run "Health returns 200" curl -sf "$API/health" >/dev/null

# 2. Create job
JOB_RESP=$(curl -s -X POST "$API/api/jobs" -H "Content-Type: application/json" -d '{"job_type":"sample"}')
JOB_ID=$(echo "$JOB_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || echo "")
if [ -n "$JOB_ID" ]; then
  echo "✅ Create job (id=$JOB_ID)"
  ((PASS++)) || true
else
  echo "❌ Create job"
  ((FAIL++)) || true
fi

# 3. Status (valid job)
run "Status 200 for valid job" curl -sf "$API/api/jobs/$JOB_ID/status" >/dev/null

# 4. Status 404 for invalid job
RESP=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/jobs/00000000-0000-0000-0000-000000000000/status")
if [ "$RESP" = "404" ]; then
  echo "✅ Status 404 for invalid job"
  ((PASS++)) || true
else
  echo "❌ Status 404 for invalid job (got $RESP)"
  ((FAIL++)) || true
fi

# 5. Cancel completed job (should return ok, no revoke)
CANCEL_RESP=$(curl -s -X POST "$API/api/jobs/$JOB_ID/cancel")
if echo "$CANCEL_RESP" | grep -q "already finished"; then
  echo "✅ Cancel on completed job returns message"
  ((PASS++)) || true
else
  echo "❌ Cancel on completed job (got: $CANCEL_RESP)"
  ((FAIL++)) || true
fi

# 6. Cancel 404 for invalid job
RESP=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API/api/jobs/00000000-0000-0000-0000-000000000000/cancel")
if [ "$RESP" = "404" ]; then
  echo "✅ Cancel 404 for invalid job"
  ((PASS++)) || true
else
  echo "❌ Cancel 404 for invalid job (got $RESP)"
  ((FAIL++)) || true
fi

# 7. Create and cancel while running (race - cancel ASAP)
JOB2_RESP=$(curl -s -X POST "$API/api/jobs" -H "Content-Type: application/json" -d '{"job_type":"sample"}')
JOB2_ID=$(echo "$JOB2_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || echo "")
if [ -n "$JOB2_ID" ]; then
  CANCEL2=$(curl -s -X POST "$API/api/jobs/$JOB2_ID/cancel")
  if echo "$CANCEL2" | grep -q "Cancellation requested\|already finished"; then
    echo "✅ Cancel (create+cancel race)"
    ((PASS++)) || true
  else
    echo "❌ Cancel response: $CANCEL2"
    ((FAIL++)) || true
  fi
else
  echo "❌ Create job 2 for cancel test"
  ((FAIL++)) || true
fi

echo
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
