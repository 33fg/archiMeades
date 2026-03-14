#!/usr/bin/env python3
"""Requeue stuck PENDING jobs to the gravitational queue.
Run this after switching to the dedicated gravitational queue.
Usage: cd project_root && .venv/bin/python scripts/requeue-stuck-jobs.py
"""

import os
import sys

_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(_root, "backend"))
os.chdir(os.path.join(_root, "backend"))  # DB path ./gravitational.db is relative to backend/


def main():
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker
    from sqlmodel import Session

    from app.core.config import settings
    from app.models.job import Job, JobStatus
    from app.tasks.mcmc import run_mcmc_task

    sync_url = settings.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")
    engine = create_engine(
        sync_url,
        connect_args={"check_same_thread": False} if "sqlite" in sync_url else {},
    )
    SessionLocal = sessionmaker(engine, class_=Session, expire_on_commit=False)

    with SessionLocal() as session:
        stmt = (
            select(Job)
            .where(Job.status == JobStatus.PENDING, Job.job_type == "mcmc")
            .order_by(Job.created_at.asc())
        )
        jobs = list(session.exec(stmt).scalars().all())

    if not jobs:
        print("No stuck PENDING mcmc jobs found.")
        return

    print(f"Requeuing {len(jobs)} stuck PENDING mcmc jobs to gravitational queue...")
    queue = getattr(settings, "celery_queue", "gravitational") or "gravitational"

    for job in jobs:
        job_id = str(job.id)
        res = run_mcmc_task.apply_async(args=[job_id], queue=queue)
        with SessionLocal() as session:
            j = session.get(Job, job_id)
            if j and j.status == JobStatus.PENDING:
                j.celery_task_id = res.id
                session.add(j)
                session.commit()
                print(f"  Requeued {job_id[:8]}... -> task {res.id[:8]}...")
            else:
                print(f"  Skipped {job_id[:8]}... (no longer PENDING)")

    print("Done. Ensure gravitational_worker is running (npm run dev).")


if __name__ == "__main__":
    main()
