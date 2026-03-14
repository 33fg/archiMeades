"""JWT auth - token extraction, validation (mock + Cognito), user resolution.
WO-10: Backend JWT Authentication and Authorization
WO-48: API key Bearer auth for external researchers
"""

from dataclasses import dataclass
from typing import Any

import httpx
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.services.api_key_service import hash_api_key, is_api_key_format


@dataclass
class CurrentUser:
    """Authenticated user for request scope (from JWT or mock)."""

    id: str
    email: str
    cognito_sub: str
    name: str | None
    role: str


def extract_bearer_token(request: Request) -> str | None:
    """Extract Bearer token from Authorization header."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return auth[7:].strip() or None


# ---- Mock token support (local dev) ----
def _is_mock_token(token: str) -> bool:
    return token.startswith("mock-jwt-")


def _parse_mock_token(token: str) -> CurrentUser:
    """Accept mock tokens from frontend AuthContext (no crypto validation)."""
    return CurrentUser(
        id="mock-dev",
        email="dev@gravitational.local",
        cognito_sub="mock-sub",
        name="Dev User",
        role="researcher",
    )


# ---- Cognito JWT validation ----
_jwks_cache: dict[str, Any] | None = None
_jwks_cache_time: float = 0.0
JWKS_CACHE_TTL_SECONDS = 86400  # 24h - allows key rotation


def _fetch_jwks() -> dict[str, Any]:
    """Fetch and cache Cognito JWKS with TTL for key rotation."""
    import time

    global _jwks_cache, _jwks_cache_time
    now = time.time()
    if _jwks_cache is not None and (now - _jwks_cache_time) < JWKS_CACHE_TTL_SECONDS:
        return _jwks_cache
    url = settings.cognito_jwks_url
    if not url:
        raise ValueError("cognito_jwks_url not configured")
    with httpx.Client() as client:
        resp = client.get(url)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_cache_time = time.time()
    return _jwks_cache


def _get_signing_key(token: str) -> Any:
    """Get JWK for token's kid from JWKS."""
    unverified = jwt.get_unverified_headers(token)
    kid = unverified.get("kid")
    if not kid:
        raise JWTError("Missing kid in token header")
    jwks = _fetch_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    raise JWTError(f"Unknown kid: {kid}")


def _validate_cognito_token(token: str) -> dict[str, Any]:
    """Validate Cognito JWT and return decoded claims."""
    if not settings.cognito_user_pool_id or not settings.cognito_client_id:
        raise ValueError("Cognito not configured")
    issuer = (
        f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/"
        f"{settings.cognito_user_pool_id}"
    )
    key = _get_signing_key(token)
    payload = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        audience=settings.cognito_client_id,
        issuer=issuer,
    )
    return payload


def _claims_to_user(claims: dict[str, Any]) -> CurrentUser:
    """Build CurrentUser from Cognito claims."""
    sub = claims.get("sub") or ""
    email = claims.get("email") or claims.get("cognito:username") or ""
    groups = claims.get("cognito:groups") or []
    role = "researcher"
    if "admin" in groups:
        role = "admin"
    elif "viewer" in groups:
        role = "viewer"
    return CurrentUser(
        id=sub,
        email=email,
        cognito_sub=sub,
        name=claims.get("name"),
        role=role,
    )


def resolve_user_from_token(token: str) -> CurrentUser:
    """Resolve CurrentUser from validated token (mock or Cognito)."""
    if _is_mock_token(token):
        return _parse_mock_token(token)
    if settings.cognito_jwks_url:
        claims = _validate_cognito_token(token)
        return _claims_to_user(claims)
    # No Cognito configured but token is not mock - treat as invalid
    raise UnauthorizedError("Invalid token: Cognito not configured")


async def resolve_user_from_api_key(
    token: str, session: AsyncSession
) -> CurrentUser | None:
    """Resolve CurrentUser from API key. Returns None if invalid/expired."""
    if not is_api_key_format(token):
        return None
    from app.repositories.api_key import APIKeyRepository

    repo = APIKeyRepository(session)
    key_hash = hash_api_key(token)
    key = await repo.find_by_key_hash(key_hash)
    if not key:
        return None
    return CurrentUser(
        id=str(key.id),
        email=key.email,
        cognito_sub="api-key",
        name=key.name,
        role="researcher",
    )
