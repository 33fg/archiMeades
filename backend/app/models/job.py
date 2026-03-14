"""Generic job metadata for Celery task tracking.
WO-38: Job submission and cost-based routing - priority, retry, estimated_flops, target_backend.
WO-39: Job persistence, checkpointing, recovery - checkpoint_s3_key, partial result preservation.
"""

from sqlalchemy import Column, JSON
from sqlmodel import Field

from app.models.base import BaseTable


class JobStatus:
    """Job status constants."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority:
    """WO-38: Job priority for queue ordering."""

    INTERACTIVE = "interactive"
    BATCH = "batch"
    BACKGROUND = "background"


class TargetBackend:
    """WO-38: Compute backend routing."""

    MAC_GPU = "mac_gpu"
    DGX_SPARK = "dgx_spark"


class Job(BaseTable, table=True):
    """Job metadata for async task tracking (Celery).
    WO-38: Extended with priority, retry, cost estimation, routing.
    """

    __tablename__ = "jobs"

    celery_task_id: str | None = Field(default=None, index=True)
    job_type: str = Field(default="generic", index=True)  # generic, simulation, mcmc, scan, theory_validation
    status: str = Field(default=JobStatus.PENDING, index=True)
    progress_percent: float = Field(default=0.0)
    error_message: str | None = None
    result_ref: str | None = None  # S3 key or DB ref to result
    started_at: str | None = None
    completed_at: str | None = None

    # WO-38: Cost-based routing and queue management
    priority: str = Field(default=JobPriority.BATCH, index=True)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    estimated_flops: float | None = Field(default=None)
    estimated_memory_mb: float | None = Field(default=None)
    target_backend: str | None = Field(default=None, index=True)  # mac_gpu | dgx_spark
    payload_json: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))  # job params for worker
    user_id: str | None = Field(default=None, index=True)  # for per-user DGX limits

    # WO-39: Checkpoint and partial result storage (S3 keys)
    checkpoint_s3_key: str | None = Field(default=None)  # latest checkpoint for resumption
