"""Base model patterns: UUID primary keys, timestamps, soft delete."""

from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BaseTable(TimestampMixin, SQLModel):
    """Base for all table models with UUID primary key."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)


class SoftDeleteMixin(SQLModel):
    """Mixin for soft delete support."""

    deleted_at: datetime | None = None
