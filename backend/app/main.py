"""FastAPI application - Gravitational Physics Simulations Platform."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.exceptions import AppException
from app.core.api_key_middleware import APIKeyResolutionMiddleware
from app.core.security import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.usage_logging_middleware import UsageLoggingMiddleware
from app.routers import (
    api_v1,
    api_v1_theories,
    auth,
    health,
    theories,
    jobs,
    simulations,
    observations,
    observables,
    storage,
    outputs,
    provenance,
    physics_numerics,
    physics_methods,
    likelihood,
    scans,
    mcmc,
)


def setup_logging() -> None:
    """Configure structured JSON logging with contextvars for request_id propagation."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer() if not settings.debug else structlog.dev.ConsoleRenderer(),
        ],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    setup_logging()
    log = structlog.get_logger()
    log.info("Starting Gravitational Physics Simulations Platform")
    await init_db()
    # Run Alembic migrations so schema stays current (e.g. after model changes)
    try:
        import os
        from alembic import command
        from alembic.config import Config

        # alembic.ini lives in backend/ (parent of app/)
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_cfg = Config(os.path.join(backend_dir, "alembic.ini"))
        command.upgrade(alembic_cfg, "head")
        log.info("Migrations applied")
    except Exception as e:
        log.warning("Migrations skipped", error=str(e))
    # WO-20: Init Neo4j schema (indexes) if available
    try:
        from app.core.neo4j import check_neo4j_available, init_neo4j_schema, neo4j_session

        if check_neo4j_available():
            with neo4j_session() as session:
                init_neo4j_schema(session)
            log.info("Neo4j schema initialized")
    except Exception as e:
        log.debug("Neo4j init skipped", error=str(e))
    yield
    log.info("Shutting down")
    await close_db()


app = FastAPI(
    title="Gravitational Physics Simulations API",
    description="Research platform for defining gravitational theories, running GPU simulations, and MCMC inference.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
# WO-48: API key resolution first (sets api_key_id for rate limit), then rate limit, then usage logging
app.add_middleware(UsageLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
app.add_middleware(APIKeyResolutionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """AC-API-006.1: Field-level validation errors with actionable messages."""
    errors = exc.errors()
    field_errors = []
    for e in errors:
        loc = ".".join(str(x) for x in e.get("loc", []) if x != "body")
        msg = e.get("msg", "Invalid value")
        field_errors.append({"field": loc or "body", "message": msg})
    return JSONResponse(
        status_code=422,
        content={
            "type": "https://api.gravitational.example/errors/ValidationError",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed. Check the 'errors' array for field-specific messages.",
            "errors": field_errors,
        },
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Map AppException to RFC 7807 Problem Details JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"https://api.gravitational.example/errors/{exc.__class__.__name__}",
            "title": exc.__class__.__name__,
            "status": exc.status_code,
            "detail": exc.message,
            **exc.detail,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Log unhandled exceptions and return 500. AC-API-006.4: Unique error ID for support."""
    import traceback
    import uuid

    log = structlog.get_logger()
    error_id = str(uuid.uuid4())[:8]
    log.exception(
        "Unhandled exception",
        path=request.url.path,
        error=str(exc),
        error_id=error_id,
    )
    detail = str(exc) if settings.debug else "Internal Server Error"
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://api.gravitational.example/errors/InternalServerError",
            "title": "Internal Server Error",
            "status": 500,
            "detail": detail,
            "error_id": error_id,
            **({"traceback": traceback.format_exc()} if settings.debug else {}),
        },
    )


app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router)
app.include_router(theories.router)
app.include_router(simulations.router)
app.include_router(observations.router)
app.include_router(storage.router)
app.include_router(outputs.router)
app.include_router(jobs.router)
app.include_router(provenance.router)
app.include_router(physics_numerics.router)
app.include_router(physics_methods.router)
app.include_router(observables.router)
app.include_router(likelihood.router)
app.include_router(scans.router)
app.include_router(mcmc.router)
app.include_router(mcmc.router)
# WO-50: API v1 sub-app with docs at /api/v1/docs
from app.api_v1_app import api_v1_app

app.mount("/api/v1", api_v1_app)
