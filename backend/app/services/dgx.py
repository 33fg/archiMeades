"""DGX GPU cluster status and capacity checks.
Used for health telemetry and rate limit fallback when at capacity.
AC-API-005.3: When DGX at capacity, rate limits reduce to 500 req/hr.
"""

import time
from dataclasses import dataclass

import httpx

from app.core.config import settings

# Cache DGX status to avoid hitting endpoint on every request
_cached_status: "DGXStatus | None" = None
_cache_time: float = 0.0
CACHE_TTL_SECONDS = 60  # Refresh every minute

# Redis key for external "at capacity" signal (set by DGX monitor or worker)
DGX_AT_CAPACITY_REDIS_KEY = "dgx:at_capacity"


@dataclass
class DGXStatus:
    """DGX cluster status."""

    available: bool
    at_capacity: bool
    message: str
    cluster_size: int = 1


def _check_redis_at_capacity() -> bool:
    """Check Redis for external at_capacity signal (TTL ~2 min)."""
    try:
        import redis

        client = redis.from_url(settings.redis_url)
        val = client.get(DGX_AT_CAPACITY_REDIS_KEY)
        client.close()
        return val is not None and str(val).lower() in ("1", "true", "yes")
    except Exception:
        return False


def _fetch_dgx_status() -> DGXStatus:
    """Fetch DGX status from health endpoint and/or Redis."""
    if not settings.dgx_enabled:
        return DGXStatus(available=False, at_capacity=False, message="disabled", cluster_size=0)

    at_capacity = _check_redis_at_capacity()

    base = settings.dgx_base_url or f"http://{settings.dgx_host}:8000"
    url = f"{base.rstrip('/')}{settings.dgx_health_path}"
    try:
        with httpx.Client(timeout=settings.dgx_timeout) as client:
            r = client.get(url)
            r.raise_for_status()
            data = r.json() if r.content else {}
            at_capacity = at_capacity or data.get("at_capacity", False)
            status_ok = data.get("status") == "ok" or r.status_code == 200
            cluster_size = int(data.get("cluster_size", 1))
            return DGXStatus(
                available=status_ok,
                at_capacity=at_capacity,
                message="ok" if status_ok else "degraded",
                cluster_size=max(1, cluster_size),
            )
    except Exception as e:
        # If HTTP fails, still respect Redis at_capacity for rate limiting
        return DGXStatus(
            available=False,
            at_capacity=at_capacity,
            message=f"unavailable: {e!s}",
            cluster_size=0,
        )


def get_dgx_status() -> DGXStatus:
    """Get DGX status with caching."""
    global _cached_status, _cache_time
    now = time.time()
    if _cached_status is None or (now - _cache_time) > CACHE_TTL_SECONDS:
        _cached_status = _fetch_dgx_status()
        _cache_time = now
    return _cached_status


def is_dgx_at_capacity() -> bool:
    """True when DGX is at capacity - use for rate limit fallback (500 req/hr)."""
    return get_dgx_status().at_capacity


def check_dgx_health() -> str:
    """Returns 'ok', 'at_capacity', 'unavailable', or 'disabled' for health/telemetry."""
    status = get_dgx_status()
    if not settings.dgx_enabled:
        return "disabled"
    if status.available and not status.at_capacity:
        return "ok"
    if status.at_capacity:
        return "at_capacity"
    return "unavailable"


def get_dgx_cluster_size() -> int:
    """Number of DGX nodes in cluster (1 when single node, or disabled)."""
    return get_dgx_status().cluster_size
