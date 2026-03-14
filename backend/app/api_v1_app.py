"""API v1 sub-application with OpenAPI docs at /api/v1/docs.
WO-50: Build API Documentation and Error Handling
AC-API-007.1: Swagger at /api/v1/docs, openapi.json at /api/v1/openapi.json
"""

from fastapi import FastAPI

from app.routers import api_v1, api_v1_theories

# Sub-app for API v1 - mounted at /api/v1, so docs at /api/v1/docs, openapi at /api/v1/openapi.json
api_v1_app = FastAPI(
    title="ArchiMeades Public API v1",
    description="""
External researcher API for gravitational theory predictions.

## Authentication
Register at `POST /api/v1/register` to receive an API key. Use as Bearer token:
```
Authorization: Bearer grav_xxxxxxxx...
```

## Rate Limits
- 1000 requests/hour per API key
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

api_v1_app.include_router(api_v1.router)
api_v1_app.include_router(api_v1_theories.router)
