"""Celery Beat scheduled tasks - health checks, cleanup, job recovery.
WO-12: Set Up Celery Task Queue with Redis
WO-39: System restart recovery - re-enqueue orphaned PENDING, mark stale RUNNING (AC-JOB-004.2).
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.celery_app import app
from app.core.config import settings
from app.models.job import Job, JobStatus, TargetBackend
from app.tasks.mcmc import run_mcmc_task

_sync_url = settings.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")
_engine = create_engine(_sync_url, connect_args={"check_same_thread": False} if "sqlite" in _sync_url else {})
_SessionLocal = sessionmaker(_engine, class_=Session, expire_on_commit=False)

STALE_RUNNING_THRESHOLD_HOURS = 6


@app.task(name="app.tasks.beat.periodic_health_check")
def periodic_health_check() -> dict:
    """Scheduled health check - runs every 5 minutes via Beat."""
    return {"status": "ok", "scheduler": "celery-beat"}


@app.task(name="app.tasks.beat.recover_orphaned_jobs")
def recover_orphaned_jobs() -> dict:
    """WO-39: Re-enqueue orphaned PENDING jobs, mark stale RUNNING as failed (AC-JOB-004.2)."""
    with _SessionLocal() as session:
        re_enqueued = 0
        marked_stale = 0

        # PENDING jobs: re-enqueue if never enqueued or task is gone (AC-JOB-004.2)
        pending = session.exec(
            select(Job).where(Job.status == JobStatus.PENDING).order_by(Job.created_at.asc())
        ).scalars().all()
        for job in pending:
            needs_enqueue = False
            if not job.celery_task_id:
                needs_enqueue = True  # Never enqueued (e.g. failed between create and enqueue)
            else:
                res = app.AsyncResult(job.celery_task_id)
                if res.state in ("REVOKED", "FAILURE"):
                    needs_enqueue = True  # Task gone or failed
            if needs_enqueue and job.job_type == "mcmc":
                queue = (
                    settings.dgx_celery_queue
                    if job.target_backend == TargetBackend.DGX_SPARK
                    else settings.celery_queue
                )
                new_task = run_mcmc_task.apply_async(args=[job.id], queue=queue or settings.celery_queue)
                job.celery_task_id = new_task.id
                session.add(job)
                re_enqueued += 1

        # RUNNING jobs: mark as failed if stale (worker likely died)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=STALE_RUNNING_THRESHOLD_HOURS)
        running = session.exec(
            select(Job).where(Job.status == JobStatus.RUNNING)
        ).scalars().all()
        for job in running:
            started = job.started_at
            if started:
                try:
                    started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    if started_dt < cutoff:
                        job.status = JobStatus.FAILED
                        job.error_message = "Worker disconnected (stale RUNNING)"
                        job.completed_at = datetime.now(timezone.utc).isoformat()
                        session.add(job)
                        marked_stale += 1
                except (ValueError, TypeError):
                    pass

        session.commit()

    return {"re_enqueued": re_enqueued, "marked_stale": marked_stale}
