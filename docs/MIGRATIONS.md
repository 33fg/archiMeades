# Alembic Migrations

WO-2: Database migration workflow, testing, and patterns.

## Overview

- **Alembic** with SQLModel metadata integration
- **env.py** uses `DATABASE_URL` from app config (sync URL for migrations)
- **Autogenerate** for schema diffs from models

## Workflow

### 1. Create migration

After changing SQLModel models:

```bash
cd gravitational/backend
alembic revision --autogenerate -m "add_column_to_theories"
```

Review the generated file in `alembic/versions/`. Edit if needed (e.g. data migrations, renames).

### 2. Review

- Check upgrade/downgrade logic
- For data migrations, add batch logic (see below)
- Ensure downgrade reverses upgrade cleanly

### 3. Test

```bash
# Upgrade
DATABASE_URL=sqlite:///./test_mig.db alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# Upgrade again
alembic upgrade head
```

Or run the test suite:

```bash
pytest backend/tests/test_migrations.py -v
```

### 4. Deploy

Migrations run in CI/CD before app deploy. For manual:

```bash
alembic upgrade head
```

## Batching for Large Data Migrations

When transforming many rows, process in batches to avoid memory and lock issues:

```python
def upgrade():
    conn = op.get_bind()
    batch_size = 1000
    offset = 0
    while True:
        result = conn.execute(
            sa.text("SELECT id, old_col FROM my_table LIMIT :limit OFFSET :offset"),
            {"limit": batch_size, "offset": offset}
        )
        rows = result.fetchall()
        if not rows:
            break
        for row in rows:
            conn.execute(
                sa.text("UPDATE my_table SET new_col = :val WHERE id = :id"),
                {"val": transform(row.old_col), "id": row.id}
            )
        offset += batch_size
```

## Progress Logging

For long-running data migrations, log progress:

```python
import logging
log = logging.getLogger("alembic.runtime.migration")

def upgrade():
    conn = op.get_bind()
    total = conn.execute(sa.text("SELECT COUNT(*) FROM my_table")).scalar()
    processed = 0
    for batch in batches(conn, "my_table", batch_size=1000):
        # process batch
        processed += len(batch)
        log.info("Progress: %d / %d (%.1f%%)", processed, total, 100 * processed / total)
```

## Commands

| Command | Description |
|---------|-------------|
| `alembic current` | Show current revision |
| `alembic history` | Show revision history |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back one revision |
| `alembic downgrade base` | Roll back all migrations |
| `alembic revision --autogenerate -m "msg"` | Generate migration from model diff |

## Environment

Set `DATABASE_URL` for the target database. Alembic converts async URLs (`+aiosqlite`, `+asyncpg`) to sync automatically.
