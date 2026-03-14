#!/bin/bash
# WO-48: Test API v1 register and quota_request endpoints
set -e
BASE="${1:-http://localhost:8002}"

echo "=== Testing POST /api/v1/register ==="
RESP=$(curl -s -X POST "$BASE/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Researcher","email":"test@example.com","affiliation":"Test Lab"}')
echo "$RESP" | head -c 200
echo "..."

API_KEY=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('api_key',''))" 2>/dev/null || true)
if [ -z "$API_KEY" ]; then
  echo "Failed to get API key from register response"
  exit 1
fi
echo "Got API key: ${API_KEY:0:15}..."

echo ""
echo "=== Testing POST /api/v1/quota_request (with API key) ==="
curl -s -X POST "$BASE/api/v1/quota_request" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"requested_limit_per_hour":2000,"reason":"Production survey"}' | python3 -m json.tool

echo ""
echo "=== Testing /api/v1/quota_request without API key (expect 401) ==="
curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE/api/v1/quota_request" \
  -H "Content-Type: application/json" \
  -d '{"requested_limit_per_hour":2000}' | tail -5

echo ""
echo "Done."
