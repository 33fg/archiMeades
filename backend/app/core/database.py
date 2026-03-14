"""Database engine and session management for PostgreSQL with SQLModel."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings
from app.models import *  # noqa: F401, F403 - Register all models  # type: ignore


_connect_args: dict = {}
if "sqlite" in settings.database_url:
    _connect_args = {"check_same_thread": False}
elif "postgresql" in settings.database_url and settings.db_ssl_mode == "require":
    # WO-1: SSL/TLS for Aurora PostgreSQL
    _connect_args = {"ssl": True}

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=_connect_args,
    pool_pre_ping="postgresql" in settings.database_url,
    pool_size=settings.db_pool_size if "postgresql" in settings.database_url else 1,
    max_overflow=settings.db_max_overflow if "postgresql" in settings.database_url else 0,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI: yield a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables. Use Alembic migrations in production."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
