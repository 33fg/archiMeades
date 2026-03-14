"""API v1 - external researcher access with API key auth.
WO-48: API Authentication and Rate Limiting Infrastructure
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import get_current_user_required, get_db
from app.core.exceptions import UnauthorizedError
from app.repositories.api_key import APIKeyRepository
from app.services.api_key_service import generate_api_key
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="", tags=["api-v1"])


class RegisterRequest(BaseModel):
    """AC-API-004.3: Registration for API key."""

    name: str
    email: str
    affiliation: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Jane Researcher",
                    "email": "jane@university.edu",
                    "affiliation": "Department of Physics",
                }
            ]
        }
    }


class RegisterResponse(BaseModel):
    """API key returned on registration. Show once - store securely."""

    api_key: str
    message: str = (
        "Store this key securely. It will not be shown again. "
        "Use as Bearer token: Authorization: Bearer <api_key>"
    )
    rate_limit_per_hour: int
    expires_at: str


class QuotaRequestRequest(BaseModel):
    """Request for higher rate limit."""

    requested_limit_per_hour: int
    reason: str | None = None


class QuotaRequestResponse(BaseModel):
    """Response for quota request."""

    message: str
    current_limit: int
    requested_limit: int
    status: str = "pending_review"


@router.post("/register", response_model=RegisterResponse)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_db),
):
    """Register for API key. AC-API-004.3: Key generated and returned immediately.
    In production, key could be emailed within 24 hours.
    """
    generated = generate_api_key()
    repo = APIKeyRepository(session)
    key = await repo.create_key(
        key_hash=generated.key_hash,
        name=body.name,
        email=body.email,
        affiliation=body.affiliation,
    )
    return RegisterResponse(
        api_key=generated.raw_key,
        rate_limit_per_hour=key.rate_limit_per_hour,
        expires_at=key.expires_at.isoformat(),
    )


@router.post("/quota_request", response_model=QuotaRequestResponse)
async def quota_request(
    body: QuotaRequestRequest,
    user=Depends(get_current_user_required),
    session: AsyncSession = Depends(get_db),
):
    """Request increased rate limit. AC-API-005.4. Requires valid API key."""
    if user.cognito_sub != "api-key":
        raise UnauthorizedError("This endpoint requires API key authentication")
    repo = APIKeyRepository(session)
    key = await repo.get_by_id(user.id)
    if not key:
        raise UnauthorizedError("API key not found")
    return QuotaRequestResponse(
        message="Your quota increase request has been submitted for review.",
        current_limit=key.rate_limit_per_hour,
        requested_limit=body.requested_limit_per_hour,
    )
