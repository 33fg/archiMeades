# Deployment Guide (WO-19)

Deployment procedures, rollback, and troubleshooting for the Gravitational Physics Simulations Platform.

## Overview

- **CI** (`.github/workflows/ci.yml`): Lint, typecheck, test, build on `main` and `develop`
- **CD** (`.github/workflows/cd.yml`): Build artifacts, smoke tests, manual approval for production on `main`

Full blue-green deployment requires AWS infrastructure (ECS, ALB, S3, CloudFront) from WO-7 and related work orders.

## Triggers

| Event | Workflow | Behavior |
|-------|----------|----------|
| Push to `main` | CD | Build → Staging smoke → Production approval gate → Release tag |
| Push to `develop` | CI only | Lint, test, build |
| Manual dispatch | CD | Choose `staging` or `production` |

## Health Checks

`GET /health` returns connectivity status:

```json
{
  "status": "ok|degraded|unhealthy",
  "service": "gravitational-api",
  "database": "ok|unavailable",
  "redis": "ok|unavailable",
  "s3": "ok|unavailable",
  "neo4j": "ok|unavailable",
  "dgx_host": "10.88.111.9"
}
```

- **ok**: All components (database, Redis, S3) available
- **degraded**: Database ok; Redis or S3 unavailable (e.g. local dev without Redis)
- **unhealthy**: Database unavailable (app cannot serve traffic)

Use `GET /health` for load balancer health checks and post-deployment smoke tests.

## Staging Smoke Tests

On push to `main`, the CD workflow:

1. Builds backend and frontend
2. Starts the API with SQLite
3. Runs `curl -sf http://localhost:8002/health` to verify liveness

## Production Approval Gate

Production deployment requires a GitHub environment named `production` with protection rules:

1. **GitHub** → Repository → Settings → Environments
2. Create `production` environment
3. Add required reviewers (e.g. senior engineer)
4. Optional: deployment branches = `main`

When the CD workflow reaches the production-approval job, it will wait for manual approval before proceeding (once deploy jobs are enabled).

## Rollback Procedure

1. **Identify** the last known-good deployment (version tag or commit)
2. **Revert** via `git revert` or redeploy previous image/task definition
3. **Verify** `GET /health` returns `ok` for database and critical services
4. **Alert** on-call if rollback was triggered by health check failure

## Troubleshooting

### Health returns "degraded"

- **Redis unavailable**: Start Redis (`redis-server`) or check `REDIS_URL`
- **S3 unavailable**: Configure AWS credentials and ensure `S3_BUCKET` exists. For local dev, use LocalStack:
  1. `docker run -d -p 4566:4566 localstack/localstack`
  2. `aws --endpoint-url=http://localhost:4566 s3 mb s3://gravitational-simulations`
  3. Add to `.env`: `AWS_ENDPOINT_URL=http://localhost:4566`, `AWS_ACCESS_KEY_ID=test`, `AWS_SECRET_ACCESS_KEY=test`
- App can still serve API requests; Celery and S3-dependent features will fail

### Health returns "unhealthy"

- **Database down**: Check `DATABASE_URL`, PostgreSQL/SQLite connectivity, migrations

### CD workflow fails on production-approval

- Ensure a `production` environment exists in GitHub repo settings
- Add at least one reviewer if using required reviewers

### Staging smoke fails

- Verify backend starts: `cd gravitational && pip install -e ".[dev]" && uvicorn app.main:app --port 8002`
- Check `DATABASE_URL` (SQLite used in CI: `sqlite+aiosqlite:///./test.db`)

## Staging Smoke Tests (Detailed)

On push to `main`, the CD workflow runs:

1. **Build** — Backend and frontend artifacts
2. **Migrations** — `alembic upgrade head` (uses `DATABASE_URL` secret or SQLite)
3. **Staging smoke** — Starts Redis service, runs backend, verifies:
   - `GET /health` returns `ok` or `degraded`
   - `database == "ok"`
   - `redis == "ok"`
4. **Notify** — Optional Slack notification when `SLACK_WEBHOOK_URL` secret is set
5. **Release tag** — Creates version tag `vYYYYMMDD-<short-sha>`

## Slack Notifications

Add `SLACK_WEBHOOK_URL` to repository secrets. On successful CD run, a message is sent to the configured channel.

## Enabling Full Deployment

When AWS infrastructure exists (WO-7, ECS, ECR, ALB, CloudFront):

1. Uncomment and configure `deploy-staging` and `deploy-production` jobs in `.github/workflows/cd.yml`
2. Add secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `ECR_REGISTRY`, `ECS_CLUSTER`, `ECS_SERVICE`, etc.
3. Set `if: secrets.DEPLOY_ENABLED == 'true'` on deploy jobs (or remove `if: false`)
4. Configure ECS task definition updates, ALB target group swap, and migration steps
5. Set up CloudWatch alarms for post-deployment monitoring (error rate, latency)
6. Configure CloudFront invalidation for frontend deployment to S3
