"""Celery tasks."""

from app.tasks.sample import sample_task

__all__ = ["sample_task"]
