"""WO-38: MCMC Celery task - NumPyro HMC-NUTS dispatched by cost-based routing.
WO-39: Partial result preservation on failure (AC-JOB-004.4).
"""

import json
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.celery_app import app
from app.core.config import settings
from app.models.job import Job, JobStatus
from app.services.checkpoint import save_partial_result

_sync_url = settings.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")
_engine = create_engine(_sync_url, connect_args={"check_same_thread": False} if "sqlite" in _sync_url else {})
_SessionLocal = sessionmaker(_engine, class_=Session, expire_on_commit=False)


def _mark_failed(session, job_id: str, error_message: str, partial_data: dict | None = None) -> None:
    """WO-39: Mark job failed and save partial result to S3 (AC-JOB-004.4)."""
    job = session.exec(select(Job).where(Job.id == job_id)).scalars().first()
    if not job:
        return
    job.status = JobStatus.FAILED
    job.error_message = error_message
    job.completed_at = datetime.now(timezone.utc).isoformat()
    if partial_data:
        try:
            key = save_partial_result(job_id, partial_data, error_message)
            job.result_ref = json.dumps({"partial_result_s3_key": key, "error": error_message})
        except Exception:
            job.result_ref = json.dumps({"error": error_message})
    else:
        job.result_ref = json.dumps({"error": error_message})
    session.add(job)
    session.commit()


@app.task(
    bind=True,
    name="app.tasks.mcmc.run_mcmc_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    time_limit=7200,  # 2 hours max for large MCMC runs
)
def run_mcmc_task(self, job_id: str) -> dict:
    """Run NumPyro MCMC from job payload. Updates job progress and result_ref."""
    with _SessionLocal() as session:
        job = session.exec(select(Job).where(Job.id == job_id)).scalars().first()
        if not job:
            return {"error": "Job not found", "job_id": job_id}
        if job.status == JobStatus.CANCELLED:
            return {"cancelled": True, "job_id": job_id}

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc).isoformat()
        job.progress_percent = 10.0
        session.add(job)
        session.commit()

    payload = job.payload_json or {}
    theory_id = payload.get("theory_id", "lcdm")
    dataset_id = payload.get("dataset_id", "synthetic")
    prior_spec = payload.get("prior_spec") or {}
    num_samples = payload.get("num_samples", 1000)
    num_warmup = payload.get("num_warmup", 500)
    num_chains = payload.get("num_chains", 1)
    sampler = payload.get("sampler", "numpyro")

    try:
        from app.mcmc.sampler import run_mcmc
    except ImportError as e:
        with _SessionLocal() as session:
            job = session.exec(select(Job).where(Job.id == job_id)).scalars().first()
            if job:
                job.status = JobStatus.FAILED
                job.error_message = f"NumPyro not installed: {e}"
                job.completed_at = datetime.now(timezone.utc).isoformat()
                session.add(job)
                session.commit()
        return {"error": str(e), "job_id": job_id}

    # Update progress before long run
    with _SessionLocal() as session:
        job = session.exec(select(Job).where(Job.id == job_id)).scalars().first()
        if job and job.status == JobStatus.RUNNING:
            job.progress_percent = 25.0
            session.add(job)
            session.commit()

    try:
        result = run_mcmc(
            theory_id=theory_id,
            dataset_id=dataset_id,
            prior_spec=prior_spec,
            num_samples=num_samples,
            num_warmup=num_warmup,
            num_chains=num_chains,
            sampler=sampler,
        )
    except Exception as e:
        with _SessionLocal() as session:
            _mark_failed(
                session,
                job_id,
                str(e),
                partial_data={
                    "job_type": "mcmc",
                    "payload": payload,
                    "theory_id": theory_id,
                    "dataset_id": dataset_id,
                },
            )
        return {"error": str(e), "job_id": job_id}

    # Progress 75% - run complete, updating DB
    with _SessionLocal() as session:
        job = session.exec(select(Job).where(Job.id == job_id)).scalars().first()
        if job and job.status == JobStatus.RUNNING:
            job.progress_percent = 75.0
            session.add(job)
            session.commit()

    with _SessionLocal() as session:
        job = session.exec(select(Job).where(Job.id == job_id)).scalars().first()
        if not job:
            return {"job_id": job_id, "result": "completed", "ok": True}
        if job.status == JobStatus.CANCELLED:
            return {"cancelled": True, "job_id": job_id}
        job.status = JobStatus.COMPLETED
        job.progress_percent = 100.0
        job.completed_at = datetime.now(timezone.utc).isoformat()
        job.result_ref = json.dumps(
            {
                "status": "completed",
                "posterior_samples": result["posterior_samples"],
                "param_names": result["param_names"],
                "diagnostics": result.get("diagnostics"),
            }
        )
        session.add(job)
        session.commit()

    return {"job_id": job_id, "result": "completed", "ok": True}
