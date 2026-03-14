"""API key and usage models for external researcher access.
WO-48: API Authentication and Rate Limiting Infrastructure
"""

from datetime import datetime

from sqlmodel import Field

from app.models.base import BaseTable


class APIKey(BaseTable, table=True):
    """API key for external researcher access. Key stored as SHA-256 hash."""

    __tablename__ = "api_keys"

    key_hash: str = Field(unique=True, index=True)  # SHA-256 of raw key
    name: str = Field(index=True)
    email: str = Field(index=True)
    affiliation: str | None = None
    rate_limit_per_hour: int = Field(default=1000)  # AC-API-005.1
    expires_at: datetime = Field(index=True)
    last_used_at: datetime | None = None


class APIUsage(BaseTable, table=True):
    """Usage log for API requests. AC-API-004.4."""

    __tablename__ = "api_usage"

    api_key_id: str = Field(foreign_key="api_keys.id", index=True)
    endpoint: str = Field(index=True)
    theory_id: str | None = Field(default=None, index=True)
    parameters_json: str | None = None  # JSON of request params for analytics
