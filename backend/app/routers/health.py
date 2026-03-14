"""Health check endpoints - WO-19: database, Redis, S3, Neo4j connectivity."""

from fastapi import APIRouter

from app.core.config import settings
from app.core.database import engine

router = APIRouter()


async def _check_db_async() -> str:
    """Check database connectivity. Returns 'ok' or 'unavailable'."""
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "unavailable"


def _check_redis() -> str:
    """Check Redis connectivity. Returns 'ok' or 'unavailable'."""
    try:
        import redis

        client = redis.from_url(settings.redis_url)
        client.ping()
        client.close()
        return "ok"
    except Exception:
        return "unavailable"


def _check_neo4j() -> str:
    """Check Neo4j connectivity. Returns 'ok' or 'unavailable'."""
    try:
        from app.core.neo4j import check_neo4j_available

        return "ok" if check_neo4j_available() else "unavailable"
    except Exception:
        return "unavailable"


def _check_dgx() -> tuple[str, int, str]:
    """Check DGX GPU cluster. Returns (status, cluster_size, error_message)."""
    try:
        from app.services.dgx import check_dgx_health, get_dgx_cluster_size, get_dgx_status

        status = check_dgx_health()
        size = get_dgx_cluster_size()
        dgx_status = get_dgx_status()
        err = dgx_status.message if status == "unavailable" else ""
        return status, size, err
    except Exception as e:
        return "unavailable", 0, str(e)


def _check_s3() -> str:
    """Check S3 connectivity. Returns 'ok' or 'unavailable'."""
    try:
        import boto3
        from botocore.exceptions import ClientError

        kwargs = {"region_name": settings.aws_region}
        if settings.aws_endpoint_url:
            kwargs["endpoint_url"] = settings.aws_endpoint_url
        client = boto3.client("s3", **kwargs)
        client.head_bucket(Bucket=settings.s3_bucket)
        return "ok"
    except (ClientError, Exception):
        return "unavailable"


@router.get("")
async def health_check() -> dict:
    """Liveness and readiness: database, Redis, S3, Neo4j, DGX connectivity."""
    db_status = await _check_db_async()
    redis_status = _check_redis()
    s3_status = _check_s3()
    neo4j_status = _check_neo4j()
    dgx_status, dgx_cluster_size, dgx_error = _check_dgx()

    core_ok = (db_status, redis_status)
    optional_ok = (s3_status, neo4j_status)
    # DGX ok = ok or at_capacity (reachable)
    dgx_ok = dgx_status in ("ok", "at_capacity")
    components_ok = sum(1 for s in core_ok + optional_ok if s == "ok")
    if db_status != "ok":
        status = "unhealthy"
    elif all(s == "ok" for s in core_ok) and components_ok >= 2:
        status = "ok"
    else:
        status = "degraded"

    return {
        "status": status,
        "service": "gravitational-api",
        "database": db_status,
        "redis": redis_status,
        "s3": s3_status,
        "neo4j": neo4j_status,
        "dgx": dgx_status,
        "dgx_cluster_size": dgx_cluster_size,
        "dgx_error": dgx_error,
        "dgx_host": settings.dgx_host,
    }
