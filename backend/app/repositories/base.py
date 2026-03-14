"""Base repository class with generic CRUD and common query patterns.
WO-6: Implement Repository Pattern and ORM Layer
"""

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.models.base import BaseTable

ModelT = TypeVar("ModelT", bound=BaseTable)


class BaseRepository(Generic[ModelT]):
    """Generic repository with CRUD operations, pagination, and eager loading."""

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    async def create(self, **kwargs: Any) -> ModelT:
        """Create and return a new record."""
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def exists(self, id: str) -> bool:
        """Check if a record exists by primary key."""
        result = await self.session.execute(
            select(self.model.id).where(self.model.id == id).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def get_by_id(
        self,
        id: str,
        *,
        options: tuple[Any, ...] | None = None,
    ) -> ModelT | None:
        """Get a single record by primary key. Use options for eager loading (e.g. selectinload)."""
        stmt = select(self.model).where(self.model.id == id)
        if options:
            for opt in options:
                stmt = stmt.options(opt)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        order_by: str | None = None,
        options: tuple[Any, ...] | None = None,
        **filters: Any,
    ) -> Sequence[ModelT]:
        """List records with optional filtering, pagination, and eager loading."""
        stmt = select(self.model)
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
        if order_by and hasattr(self.model, order_by.lstrip("-")):
            col = getattr(self.model, order_by.lstrip("-"))
            stmt = stmt.order_by(col.desc() if order_by.startswith("-") else col)
        if options:
            for opt in options:
                stmt = stmt.options(opt)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, id: str, **kwargs: Any) -> ModelT | None:
        """Update a record and return it, or None if not found."""
        obj = await self.get_by_id(id)
        if obj is None:
            return None
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: str) -> bool:
        """Delete a record. Returns True if found and deleted."""
        obj = await self.get_by_id(id)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True
