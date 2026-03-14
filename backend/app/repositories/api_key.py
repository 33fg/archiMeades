"""API key repository - lookup by hash, create, update.
WO-48: API Authentication and Rate Limiting Infrastructure
"""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.api_key import APIKey, APIUsage
from app.repositories.base import BaseRepository


class APIKeyRepository(BaseRepository[APIKey]):
    """Repository for APIKey model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, APIKey)

    async def find_by_key_hash(self, key_hash: str) -> APIKey | None:
        """Find API key by SHA-256 hash. Returns None if expired."""
        result = await self.session.execute(
            select(APIKey).where(APIKey.key_hash == key_hash)
        )
        key = result.scalar_one_or_none()
        if key and key.expires_at < datetime.utcnow():
            return None
        return key

    async def create_key(
        self,
        key_hash: str,
        name: str,
        email: str,
        affiliation: str | None = None,
    ) -> APIKey:
        """Create new API key with default rate limit and 1-year expiry."""
        expires_at = datetime.utcnow() + timedelta(days=settings.api_key_expiry_days)
        key = APIKey(
            key_hash=key_hash,
            name=name,
            email=email,
            affiliation=affiliation,
            rate_limit_per_hour=settings.api_key_default_rate_limit,
            expires_at=expires_at,
        )
        self.session.add(key)
        await self.session.flush()
        return key

    async def update_last_used(self, key_id: str) -> None:
        """Update last_used_at timestamp."""
        result = await self.session.execute(select(APIKey).where(APIKey.id == key_id))
        key = result.scalar_one_or_none()
        if key:
            key.last_used_at = datetime.utcnow()


class APIUsageRepository(BaseRepository[APIUsage]):
    """Repository for APIUsage model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, APIUsage)

    async def log_request(
        self,
        api_key_id: str,
        endpoint: str,
        theory_id: str | None = None,
        parameters_json: str | None = None,
    ) -> None:
        """Log an API request for usage analytics."""
        usage = APIUsage(
            api_key_id=api_key_id,
            endpoint=endpoint,
            theory_id=theory_id,
            parameters_json=parameters_json,
        )
        self.session.add(usage)
