"""Pytest configuration and fixtures."""

import os
import subprocess

import pytest

# Use test database before app imports
_test_db = "sqlite+aiosqlite:///./test.db"
os.environ.setdefault("DATABASE_URL", _test_db)

# Run migrations on test DB so schema matches models (WO-21 theory fields, etc.)
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_alembic_ini = os.path.join(_backend_dir, "alembic.ini")
_sync_url = _test_db.replace("+aiosqlite", "")
subprocess.run(
    ["alembic", "-c", _alembic_ini, "upgrade", "head"],
    env={**os.environ, "ALEMBIC_DATABASE_URL": _sync_url},
    cwd=os.path.dirname(_backend_dir),
    capture_output=True,
    check=False,
)


@pytest.fixture(autouse=True)
def _set_test_env(monkeypatch):
    """Ensure test env vars for all tests."""
    monkeypatch.setenv("DATABASE_URL", _test_db)
