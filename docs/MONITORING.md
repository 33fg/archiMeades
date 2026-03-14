# Monitoring and Observability (WO-8)

Runbooks, alarm response, and AWS observability setup for the Gravitational Physics Simulations Platform.

## Overview

- **Local development**: Request logging middleware logs each request (method, path, status, duration, request_id)
- **Production (AWS)**: CloudWatch Logs, X-Ray tracing, dashboards, and alarms (when infrastructure is deployed)

## Request Logging (Local and Production)

Every HTTP request is logged with structured fields:

| Field | Description |
|-------|-------------|
| `method` | HTTP method (GET, POST, etc.) |
| `path` | Request path |
| `status_code` | Response status code |
| `duration_ms` | Request duration in milliseconds |
| `request_id` | UUID for request tracing (also in `X-Request-ID` header) |

`request_id` is bound to structlog context for the lifetime of the request. Any log emitted during request handling will include `request_id` when `merge_contextvars` is configured.

### Example Log (JSON)

```json
{
  "event": "request",
  "method": "GET",
  "path": "/health",
  "status_code": 200,
  "duration_ms": 12.34,
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2025-03-12T10:00:00.123456Z",
  "level": "info"
}
```

## Runbooks

### Health Check Degraded

**Symptom**: `GET /health` returns `"status": "degraded"`

**Causes**:
- Redis unavailable (Celery, rate limiting affected)
- Neo4j unavailable (provenance graph affected)
- S3 unavailable (output storage affected)

**Actions**:
1. Check Redis: `redis-cli ping` or verify `REDIS_URL`
2. Check Neo4j: `curl http://localhost:7475` or verify `NEO4J_URI` (bolt://localhost:7688)
3. Check S3: AWS credentials, `S3_BUCKET` exists, IAM permissions
4. App continues to serve API; Celery jobs, provenance, and S3-dependent features may fail
5. Restart Redis, Neo4j, or fix S3 config; no app restart required for recovery

### Health Check Unhealthy

**Symptom**: `GET /health` returns `"status": "unhealthy"`

**Causes**:
- Database unavailable

**Actions**:
1. Check `DATABASE_URL`, PostgreSQL connectivity
2. Run migrations if schema mismatch: `alembic upgrade head`
3. Restart API after DB is available
4. Consider rollback if recent deployment introduced the issue

### High Error Rate (5xx)

**Symptom**: Alarms on 5xx response rate (when CloudWatch alarms are configured)

**Actions**:
1. Check CloudWatch Logs for `status_code >= 500` in request logs
2. Correlate by `request_id` with application error logs
3. Check database connections, Redis, S3
4. Scale up or rollback if resource exhaustion

### High Latency

**Symptom**: P95/P99 latency exceeds threshold

**Actions**:
1. Use `duration_ms` in request logs to identify slow endpoints
2. Check X-Ray traces (when enabled) for slow spans
3. Review database query performance, N+1 queries
4. Check Celery queue depth and worker capacity

### Rate Limit Exceeded (429)

**Symptom**: Clients receive 429 responses

**Actions**:
1. Check `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers
2. Verify Redis is available (rate limiting uses Redis when configured)
3. Consider increasing `requests_per_minute` or per-user limits for legitimate traffic

## AWS Observability Setup (When Deployed)

When ECS/EC2 infrastructure exists (WO-7), configure:

### CloudWatch Logs

1. **Log group**: `/gravitational/api`
2. **Log stream**: ECS task ID or instance ID
3. **Structured JSON**: Use `JSONRenderer` in structlog (default when `debug=false`)
4. **Retention**: 30 days for staging, 90 days for production

### X-Ray Tracing

1. Install AWS X-Ray SDK: `opentelemetry-sdk`, `opentelemetry-exporter-otlp`
2. Configure trace exporter to X-Ray collector
3. Propagate `X-Amzn-Trace-Id` or `X-Request-ID` for distributed tracing
4. Create X-Ray sampling rule: 1% for normal traffic, 100% for errors

### CloudWatch Dashboards

| Widget | Metric | Purpose |
|--------|--------|---------|
| Request count | Custom metric from request logs | Traffic volume |
| Error rate | Count of status_code >= 500 | Health |
| Latency P95 | duration_ms percentile | Performance |
| Health status | Custom metric from /health | Service availability |

### Alarms

| Alarm | Condition | Action |
|-------|------------|--------|
| HealthUnhealthy | health status != ok | SNS → PagerDuty/Slack |
| High5xxRate | 5xx count > threshold | SNS notification |
| HighLatency | P95 > 500ms | SNS notification |
| DatabaseDown | health database != ok | SNS → on-call |

## Local Development

Request logging is always enabled. To view logs:

```bash
cd gravitational
uvicorn app.main:app --reload --port 8000
# Logs appear in console (ConsoleRenderer when debug=true)
```

To test request IDs:

```bash
curl -v -H "X-Request-ID: my-test-id" http://localhost:8000/health
# Response includes X-Request-ID: my-test-id
# Log includes request_id: my-test-id
```

## Related Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) – Rollback, health checks, CD
- [SECURITY.md](./SECURITY.md) – Rate limiting, security headers
