"""API key resolution middleware - resolves Bearer API key before rate limit.
WO-48: API Authentication and Rate Limiting Infrastructure
AC-API-004.1: 401 when no API key for /api/v1/ (except /register)
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.database import async_session_factory
from app.services.api_key_service import hash_api_key, is_api_key_format


def _requires_api_key(path: str) -> bool:
    """True if path is /api/v1/ and not /api/v1/register."""
    if not path.startswith("/api/v1/"):
        return False
    if path == "/api/v1/register" or path.startswith("/api/v1/register?"):
        return False
    return True


async def resolve_api_key_for_request(request: Request) -> None:
    """If Bearer token is API key format, lookup and set request.state."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return
    token = auth[7:].strip()
    if not is_api_key_format(token):
        return
    key_hash = hash_api_key(token)
    async with async_session_factory() as session:
        from app.repositories.api_key import APIKeyRepository

        repo = APIKeyRepository(session)
        key = await repo.find_by_key_hash(key_hash)
        if key:
            request.state.api_key_id = str(key.id)
            request.state.api_key_rate_limit_per_hour = key.rate_limit_per_hour


class APIKeyResolutionMiddleware(BaseHTTPMiddleware):
    """Resolve API key from Bearer token and set request.state for rate limiting.
    AC-API-004.1: Return 401 for /api/v1/ (except register) when no valid API key.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        await resolve_api_key_for_request(request)
        if _requires_api_key(request.url.path):
            api_key_id = getattr(request.state, "api_key_id", None)
            if not api_key_id:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "API key required. Register at POST /api/v1/register with name, email, and optionally affiliation to receive an API key."
                    },
                )
        return await call_next(request)
