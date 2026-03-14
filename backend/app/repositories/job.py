"""Job repository for Celery task status.
WO-38: Queue listing with estimated start time.
"""

from sqlalchemy import select

from app.models.job import Job, JobStatus, TargetBackend
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Repository for Job (Celery task metadata)."""

    def __init__(self, session) -> None:
        super().__init__(session, Job)

    async def list_active(self, limit: int = 50) -> list[Job]:
        """List jobs with status pending or running, newest first."""
        stmt = (
            select(Job)
            .where(Job.status.in_([JobStatus.PENDING, JobStatus.RUNNING]))
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_status(self, status: str, limit: int = 50) -> list[Job]:
        """List jobs by status, newest first."""
        stmt = (
            select(Job)
            .where(Job.status == status)
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_queue(
        self,
        target_backend: str | None = None,
        limit: int = 50,
    ) -> list[Job]:
        """WO-38: List queued jobs (pending for DGX) ordered by priority then created_at."""
        stmt = (
            select(Job)
            .where(Job.status == JobStatus.PENDING)
            .order_by(
                Job.priority.asc(),  # interactive < batch < background (string sort)
                Job.created_at.asc(),
            )
            .limit(limit)
        )
        if target_backend:
            stmt = stmt.where(Job.target_backend == target_backend)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_pending_for_backend(self, target_backend: str | None = None) -> int:
        """WO-38: Count pending jobs for a backend (queue depth). If target_backend is None, count all pending."""
        from sqlalchemy import func

        stmt = select(func.count(Job.id)).where(Job.status == JobStatus.PENDING)
        if target_backend:
            stmt = stmt.where(Job.target_backend == target_backend)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0
