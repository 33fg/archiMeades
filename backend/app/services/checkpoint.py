"""WO-39: Job checkpoint and partial result storage.

AC-JOB-004.4: Partial results and error state saved for failed jobs.
AC-JOB-005: Checkpoint every 5 min (MCMC) or 1000 evals (scan).
7-day retention with automatic cleanup.
"""

import json
from datetime import datetime, timezone

from app.services.s3 import build_key, get_object, put_object

CHECKPOINT_RETENTION_DAYS = 7


def job_checkpoint_key(job_id: str) -> str:
    """S3 key for job checkpoint (latest state for resumption)."""
    return build_key("jobs", job_id, "checkpoint.json")


def job_partial_result_key(job_id: str) -> str:
    """S3 key for partial result on failure (AC-JOB-004.4)."""
    return build_key("jobs", job_id, "partial_result.json")


def save_checkpoint(job_id: str, data: dict) -> str:
    """Save checkpoint to S3. Returns S3 key."""
    key = job_checkpoint_key(job_id)
    data["checkpointed_at"] = datetime.now(timezone.utc).isoformat()
    body = json.dumps(data).encode("utf-8")
    put_object(key, body, content_type="application/json")
    return key


def load_checkpoint(job_id: str) -> dict | None:
    """Load checkpoint from S3. Returns None if not found."""
    try:
        key = job_checkpoint_key(job_id)
        body = get_object(key)
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None


def save_partial_result(job_id: str, data: dict, error_message: str | None = None) -> str:
    """Save partial result on failure (AC-JOB-004.4). Returns S3 key."""
    key = job_partial_result_key(job_id)
    data["saved_at"] = datetime.now(timezone.utc).isoformat()
    if error_message:
        data["error_message"] = error_message
    body = json.dumps(data).encode("utf-8")
    put_object(key, body, content_type="application/json")
    return key
