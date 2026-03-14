"""Alembic migration tests - upgrade and downgrade paths.
WO-2: Implement Alembic Migrations Framework
"""

import os
import tempfile

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


@pytest.fixture
def temp_db_url():
    """Create a temporary SQLite database for migration tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield f"sqlite:///{path}"
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def alembic_config(temp_db_url):
    """Alembic config and env override for temp database."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # env.py uses ALEMBIC_DATABASE_URL when set (avoids cached settings)
    os.environ["ALEMBIC_DATABASE_URL"] = temp_db_url
    config = Config(os.path.join(backend_dir, "alembic.ini"))
    config.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
    yield config
    os.environ.pop("ALEMBIC_DATABASE_URL", None)


def test_upgrade_head(alembic_config, temp_db_url):
    """Upgrade to head creates expected tables."""
    command.upgrade(alembic_config, "head")
    engine = create_engine(temp_db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "theories" in tables
    assert "simulations" in tables
    assert "observations" in tables
    engine.dispose()


def test_downgrade_base(alembic_config, temp_db_url):
    """Downgrade to base removes all tables."""
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    engine = create_engine(temp_db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" not in tables
    assert "theories" not in tables
    engine.dispose()


def test_upgrade_downgrade_roundtrip(alembic_config, temp_db_url):
    """Upgrade to head, downgrade one, upgrade again succeeds."""
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "-1")
    command.upgrade(alembic_config, "head")
    engine = create_engine(temp_db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        assert result.scalar() == 0  # Empty table, but exists
    engine.dispose()
