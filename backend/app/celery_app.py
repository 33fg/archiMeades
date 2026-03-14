"""Celery application configuration - Redis broker, result backend.
WO-12: Set Up Celery Task Queue with Redis
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

app = Celery(
    "gravitational",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks", "app.tasks.beat", "app.tasks.simulation", "app.tasks.theory_validation", "app.tasks.mcmc"],
)
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=86400,  # 24h TTL
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Retry defaults: exponential backoff
app.conf.task_default_retry_delay = 60  # 1 min
app.conf.task_max_retries = 3

# Default queue and DGX routing
app.conf.task_default_queue = settings.celery_queue
if settings.dgx_celery_queue:
    app.conf.task_routes = {
        "app.tasks.simulation.run_simulation_task": {"queue": settings.dgx_celery_queue},
        "app.tasks.mcmc.run_mcmc_task": {"queue": settings.dgx_celery_queue},
    }

# Celery Beat schedule
app.conf.beat_schedule = {
    "health-check-periodic": {
        "task": "app.tasks.beat.periodic_health_check",
        "schedule": crontab(minute="*/5"),  # every 5 minutes
    },
    "recover-orphaned-jobs": {
        "task": "app.tasks.beat.recover_orphaned_jobs",
        "schedule": crontab(minute="*/15"),  # WO-39: every 15 minutes
    },
}
