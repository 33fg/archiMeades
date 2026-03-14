"""Jobs API - Celery task status polling and management.
WO-38: Job submission, cost-based routing, queue endpoint.
WO-39: Job spec persisted before execution (AC-JOB-004.1).
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import app as celery_app
from app.core.config import settings
from app.core.dependencies import get_db
from app.models.job import Job, JobPriority, JobStatus, TargetBackend
from app.repositories.job import JobRepository
from app.services.job_routing import (
    estimate_job_cost,
    route_job,
)
from app.tasks.mcmc import run_mcmc_task
from app.tasks.sample import sample_task

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobStatusRead(BaseModel):
    """Job status response."""

    id: str
    celery_task_id: str | None
    job_type: str
    status: str
    progress_percent: float
    error_message: str | None
    result_ref: str | None = None  # JSON string when completed (e.g. MCMC posterior)
    started_at: str | None = None
    completed_at: str | None = None
    priority: str | None = None
    estimated_flops: float | None = None
    target_backend: str | None = None
    queue_depth_warning: bool | None = None

    model_config = {"from_attributes": True}


class JobCreate(BaseModel):
    """Create and enqueue a sample job."""

    job_type: str = "sample"


class ComputeJobSubmit(BaseModel):
    """WO-38: Submit compute job with cost estimation and routing."""

    job_type: str  # mcmc | scan | theory_validation
    priority: str = JobPriority.BATCH
    payload: dict[str, Any]


def _enqueue_compute_task(job_type: str, job_id: str, target_backend: str) -> str:
    """Enqueue Celery task for compute job. Returns celery_task_id."""
    queue = (
        settings.dgx_celery_queue if target_backend == TargetBackend.DGX_SPARK else settings.celery_queue
    )
    if job_type == "mcmc":
        res = run_mcmc_task.apply_async(args=[job_id], queue=queue or settings.celery_queue)
        return res.id
    raise HTTPException(501, f"Async job type '{job_type}' not yet implemented")


@router.post("/submit", response_model=JobStatusRead)
async def submit_compute_job(
    data: ComputeJobSubmit,
    session: AsyncSession = Depends(get_db),
):
    """WO-38: Submit compute job with cost estimation and routing. Returns job ID immediately (AC-JOB-001.4)."""
    if data.job_type not in ("mcmc", "scan", "theory_validation"):
        raise HTTPException(422, "job_type must be mcmc, scan, or theory_validation")
    flops, memory_mb = estimate_job_cost(data.job_type, data.payload)
    target_backend, _ = route_job(flops, memory_mb)
    repo = JobRepository(session)
    queue_depth = (
        await repo.count_pending_for_backend(TargetBackend.DGX_SPARK)
        if target_backend == TargetBackend.DGX_SPARK
        else 0
    )
    queue_depth_warning = queue_depth > 10  # AC-JOB-002.3
    job = await repo.create(
        job_type=data.job_type,
        status=JobStatus.PENDING,
        priority=data.priority,
        estimated_flops=flops,
        estimated_memory_mb=memory_mb,
        target_backend=target_backend,
        payload_json=data.payload,
    )
    await session.commit()  # AC-JOB-004.1: Persist before execution begins
    try:
        task_id = _enqueue_compute_task(data.job_type, job.id, target_backend)
        await repo.update(job.id, celery_task_id=task_id)
        await session.commit()
    except HTTPException:
        await repo.update(job.id, status=JobStatus.FAILED, error_message="Task dispatch failed")
        await session.commit()
        raise
    job = await repo.get_by_id(job.id)
    out = JobStatusRead.model_validate(job)
    out.queue_depth_warning = queue_depth_warning
    return out


@router.get("/queue")
async def get_queue(
    target_backend: str | None = None,
    limit: int = 50,
    session: AsyncSession = Depends(get_db),
):
    """WO-38: List queued jobs with estimated start. AC-JOB-002.4."""
    repo = JobRepository(session)
    jobs = await repo.list_queue(target_backend=target_backend, limit=limit)
    depth = await repo.count_pending_for_backend(target_backend)
    return {
        "jobs": [JobStatusRead.model_validate(j) for j in jobs],
        "queue_depth": depth,
        "queue_depth_warning": depth > 10,
    }


@router.get("", response_model=list[JobStatusRead])
async def list_jobs(
    status: str | None = None,
    limit: int = 50,
    session: AsyncSession = Depends(get_db),
):
    """List jobs, optionally filtered by status. Default: active (pending, running)."""
    repo = JobRepository(session)
    if status:
        jobs = await repo.list_by_status(status, limit=limit)
    else:
        jobs = await repo.list_active(limit=limit)
    return jobs


@router.get("/workers/health")
async def workers_health():
    """Check Celery worker connectivity. Returns ping status from all workers."""
    inspect = celery_app.control.inspect()
    ping = inspect.ping()
    if ping:
        return {"status": "ok", "workers": list(ping.keys())}
    return {"status": "unavailable", "workers": []}


@router.post("", response_model=JobStatusRead)
async def create_job(
    data: JobCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a job record and enqueue the Celery task."""
    repo = JobRepository(session)
    job = await repo.create(job_type=data.job_type, status=JobStatus.PENDING)
    await session.flush()
    task = sample_task.delay(job.id)
    await repo.update(job.id, celery_task_id=task.id)
    await session.commit()  # Commit before worker picks up task
    await session.refresh(job)
    return job


@router.get("/{job_id}/status", response_model=JobStatusRead)
async def get_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get job status and progress."""
    repo = JobRepository(session)
    job = await repo.get_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Request job cancellation."""
    repo = JobRepository(session)
    job = await repo.get_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
        return {"message": "Job already finished", "status": job.status}
    await repo.update(job_id, status=JobStatus.CANCELLED)
    await session.commit()  # Commit so worker sees CANCELLED before revoke
    if job.celery_task_id:
        celery_app.control.revoke(job.celery_task_id, terminate=True)
    return {"message": "Cancellation requested", "status": JobStatus.CANCELLED}
