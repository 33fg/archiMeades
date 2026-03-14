#!/bin/bash
# Set DGX at-capacity flag in Redis (triggers 500 req/hr rate limit fallback).
# Usage: ./scripts/set-dgx-at-capacity.sh [1|0]
#   1 = at capacity (default), 0 = clear
# TTL 120 seconds - refresh periodically if DGX stays busy.
set -e
VAL="${1:-1}"
redis-cli -u "${REDIS_URL:-redis://localhost:6379/0}" SETEX dgx:at_capacity 120 "$VAL"
echo "Set dgx:at_capacity=$VAL (TTL 120s)"
