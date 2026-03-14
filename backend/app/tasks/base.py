"""Base task utilities - progress, cancellation check, error handling.
WO-12: Set Up Celery Task Queue with Redis
"""

from typing import Any, TypeVar

from sqlmodel import Session, SQLModel, select

ModelT = TypeVar("ModelT", bound=SQLModel)


def check_cancelled(
    session: Session,
    model_class: type[ModelT],
    id_value: str,
    id_attr: str = "id",
    status_attr: str = "status",
    cancelled_value: str = "cancelled",
) -> bool:
    """Return True if the entity is marked cancelled. Use in task loops to exit early."""
    stmt = select(model_class).where(getattr(model_class, id_attr) == id_value)
    result = session.exec(stmt).first()
    if result is None:
        return False
    return getattr(result, status_attr, None) == cancelled_value


def update_progress(
    session: Session,
    model_class: type[ModelT],
    id_value: str,
    id_attr: str = "id",
    **kwargs: Any,
) -> ModelT | None:
    """Update entity fields (progress_percent, status, etc.). Returns entity or None."""
    stmt = select(model_class).where(getattr(model_class, id_attr) == id_value)
    obj = session.exec(stmt).first()
    if obj is None:
        return None
    for key, value in kwargs.items():
        if hasattr(obj, key):
            setattr(obj, key, value)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def mark_failed(
    session: Session,
    model_class: type[ModelT],
    id_value: str,
    error_message: str,
    id_attr: str = "id",
    status_attr: str = "status",
    error_attr: str = "error_message",
    failed_value: str = "failed",
) -> ModelT | None:
    """Mark entity as failed with error message."""
    return update_progress(
        session,
        model_class,
        id_value,
        id_attr=id_attr,
        **{status_attr: failed_value, error_attr: error_message},
    )
