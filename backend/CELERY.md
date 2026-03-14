# Celery Task Queue

WO-12: Async job processing with Redis broker.

## Prerequisites

- Redis running at `localhost:6379` (or set `REDIS_URL` in `.env`)

## Running Workers

From project root:

```bash
# Worker only (processes tasks)
./scripts/celery-worker.sh worker

# Beat scheduler only (schedules periodic tasks)
./scripts/celery-worker.sh beat

# Both worker and beat (default)
./scripts/celery-worker.sh both
```

Or from `gravitational/backend`:

```bash
celery -A app.celery_app worker -l info
celery -A app.celery_app beat -l info
```

## Configuration

- **Broker / Backend**: Redis (`REDIS_URL`)
- **Result TTL**: 24h
- **Retry**: Exponential backoff, max 3 retries
- **Beat schedule**: `periodic_health_check` every 5 minutes

## Task Development

1. Add tasks in `app/tasks/` (e.g. `app/tasks/sample.py`)
2. Use `@app.task` decorator with `bind=True` for retries
3. Options: `autoretry_for`, `retry_backoff`, `retry_backoff_max`
4. Register in `celery_app.py` `include` if using a new module
5. For Beat: add to `beat_schedule` in `celery_app.py`

### Base Utilities (`app.tasks.base`)

Use shared helpers for progress tracking, cancellation checks, and error handling:

```python
from app.tasks.base import check_cancelled, update_progress, mark_failed

# In task loop: exit early if user cancelled
if check_cancelled(session, Job, job_id, status_attr="status", cancelled_value="cancelled"):
    return {"cancelled": True}

# Update progress (progress_percent, status, etc.)
update_progress(session, Job, job_id, progress_percent=50.0, status="running")

# On error: mark failed with message
mark_failed(session, Job, job_id, "Theory not found")
```

### Cancellation

- API: `POST /api/jobs/{job_id}/cancel` marks job CANCELLED and revokes the Celery task
- Tasks should poll `check_cancelled()` in loops and exit when cancelled
- `revoke(terminate=True)` stops the worker process executing the task

### Error Handling

- Use `autoretry_for=(Exception,)` for transient failures
- For permanent failures (e.g. missing theory), call `mark_failed()` and return—do not retry
- Set `task_acks_late=True` so failed tasks are not lost before ack

### DB Access in Tasks

Workers run in a separate process—use a **sync** SQLAlchemy/SQLModel session, not async. Create engine with `create_engine()` (no `+asyncpg` / `+aiosqlite`).

## Worker Monitoring and Health Checks

- **API**: `GET /api/jobs/workers/health` returns `{"status": "ok", "workers": ["celery@hostname"]}` when workers respond to ping
- **CLI**: `celery -A app.celery_app inspect ping` to ping workers from the command line
- **Active tasks**: `celery -A app.celery_app inspect active`
- **Registered tasks**: `celery -A app.celery_app inspect registered`

Use the health endpoint for load balancer or monitoring probes when workers run in separate containers.

## Graceful Shutdown

Workers handle `SIGTERM`; in-flight tasks complete before shutdown. Use `celery control shutdown` for coordinated stop.
