# Backend + Celery worker image.
# Build: docker build -t gravitational-backend .
# Used by docker-compose celery service.

FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency install
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml README.md ./
COPY backend/ backend/

# Install dependencies
RUN uv pip install --system -e ".[numpyro]"

WORKDIR /app/backend

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default: run celery worker (override in docker-compose)
CMD ["celery", "-A", "app.celery_app", "worker", "-l", "info", "-Q", "gravitational,dgx"]
