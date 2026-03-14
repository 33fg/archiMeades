"""Security middleware: rate limiting, security headers, request ID.
WO-11: Implement Security Middleware and Rate Limiting
WO-8: Request logging middleware for observability
"""

import time
import uuid
from collections import defaultdict

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


def _get_client_ip(request: Request) -> str:
    """Get client IP (supports X-Forwarded-For behind proxy)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "anonymous"


def _rate_limit_key_fn(request: Request) -> tuple[str, int, int]:
    """Return (key, limit, window_seconds). WO-48: per-API-key when present.
    AC-API-005.3: When DGX at capacity, reduce to 500 req/hr for fair sharing."""
    api_key_id = getattr(request.state, "api_key_id", None)
    if api_key_id:
        limit_per_hour = getattr(
            request.state, "api_key_rate_limit_per_hour", 1000
        )
        try:
            from app.services.dgx import is_dgx_at_capacity

            if is_dgx_at_capacity():
                limit_per_hour = min(limit_per_hour, 500)
        except Exception:
            pass
        return f"apikey:{api_key_id}", limit_per_hour, 3600
    return f"ip:{_get_client_ip(request)}", 120, 60  # 120/min for IP


def _rate_limit_reset_ts(window_seconds: int) -> int:
    """Unix timestamp when current rate limit window resets."""
    return int(time.time() // window_seconds) * window_seconds + window_seconds


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting: Redis when available, else in-memory.
    WO-48: Per-API-key (1000/hour) when Bearer API key present, else per-IP (120/min).
    """

    def __init__(self, app, requests_per_minute: int = 120, key_fn=None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.key_fn = key_fn  # Unused when using _rate_limit_key_fn
        self._requests: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._redis = None
        try:
            import redis

            self._redis = redis.from_url(settings.redis_url)
            self._redis.ping()
        except Exception:
            self._redis = None

    def _redis_check(self, key: str, limit: int, window: int) -> tuple[int, bool]:
        """Return (count, allowed). Uses Redis INCR with configurable window."""
        window_id = int(time.time() // window)
        rkey = f"ratelimit:{key}:{window_id}"
        try:
            pipe = self._redis.pipeline()
            pipe.incr(rkey)
            pipe.expire(rkey, window + 60)
            results = pipe.execute()
            count = results[0]
            return count, count <= limit
        except Exception:
            return 0, True  # Fail open

    def _memory_check(
        self, key: str, limit: int, window: int
    ) -> tuple[int, bool]:
        """Return (count, allowed). In-memory sliding window."""
        now = time.time()
        cutoff = now - window
        self._requests[key] = [
            (t, w) for t, w in self._requests[key] if t > cutoff and w == window
        ]
        count = len(self._requests[key])
        if count >= limit:
            return count, False
        self._requests[key].append((now, window))
        return count, True

    async def dispatch(self, request: Request, call_next) -> Response:
        key, limit, window = _rate_limit_key_fn(request)
        reset_ts = _rate_limit_reset_ts(window)
        headers_base = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Reset": str(reset_ts),
        }

        if self._redis:
            count, allowed = self._redis_check(key, limit, window)
        else:
            count, allowed = self._memory_check(key, limit, window)

        if not allowed:
            return Response(
                content='{"detail":"Rate limit exceeded. Register at /api/v1/register for a key."}',
                status_code=429,
                media_type="application/json",
                headers={
                    **headers_base,
                    "Retry-After": str(reset_ts - int(time.time())),
                    "X-RateLimit-Remaining": "0",
                },
            )

        remaining = max(0, limit - count)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_ts)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers: X-Content-Type-Options, X-Frame-Options, HSTS, CSP, etc."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # CSP: allow self, inline scripts for dev; tighten for production
        csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Content-Security-Policy"] = csp
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Generate and propagate request ID for tracing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log each request: method, path, status, duration, request_id. Binds request_id to structlog context."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = getattr(request.state, "request_id", None) or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        log = structlog.get_logger()
        log.info(
            "request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            request_id=request_id,
        )
        return response
