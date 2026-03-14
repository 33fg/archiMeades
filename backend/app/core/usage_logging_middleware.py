"""Usage logging middleware - logs API requests when API key is used.
WO-48: AC-API-004.4 - log timestamp, endpoint, theory, parameters
"""

import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import async_session_factory


class UsageLoggingMiddleware(BaseHTTPMiddleware):
    """Log API usage to api_usage table when request uses API key."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        api_key_id = getattr(request.state, "api_key_id", None)
        if not api_key_id:
            return response

        theory_id = request.query_params.get("theory_id")
        params_json = None
        if request.query_params:
            params_json = json.dumps(dict(request.query_params))

        async with async_session_factory() as session:
            from app.repositories.api_key import APIUsageRepository

            repo = APIUsageRepository(session)
            await repo.log_request(
                api_key_id=api_key_id,
                endpoint=request.url.path,
                theory_id=theory_id,
                parameters_json=params_json,
            )
            await session.commit()

        return response
