"""Sample Celery task for job status tracking."""

from app.celery_app import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, select

from app.core.config import settings
from app.models.job import Job, JobStatus

# Sync engine for Celery worker (workers run in separate process, need sync DB)
_sync_url = settings.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")
_engine = create_engine(_sync_url)
_SessionLocal = sessionmaker(_engine, class_=Session, expire_on_commit=False)


@app.task(
    bind=True,
    name="app.tasks.sample_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def sample_task(self, job_id: str) -> dict:
    """Sample task that updates job progress - demonstrates job status tracking."""
    with _SessionLocal() as session:
        job = session.exec(select(Job).where(Job.id == job_id)).first()
        if not job:
            return {"error": "Job not found"}
        job.status = JobStatus.RUNNING
        job.celery_task_id = self.request.id
        session.add(job)
        session.commit()

    # Simulate work
    for i in range(1, 11):
        with _SessionLocal() as session:
            job = session.exec(select(Job).where(Job.id == job_id)).first()
            if job and job.status == JobStatus.CANCELLED:
                return {"cancelled": True}
            if job:
                job.progress_percent = i * 10.0
                session.add(job)
                session.commit()

    with _SessionLocal() as session:
        job = session.exec(select(Job).where(Job.id == job_id)).first()
        if job:
            job.status = JobStatus.COMPLETED
            job.progress_percent = 100.0
            session.add(job)
            session.commit()

    return {"job_id": job_id, "status": "completed"}
