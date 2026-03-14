#!/bin/bash
# Run Alembic migrations. Use if backend fails with "no such column" errors.
# From project root: ./scripts/migrate-db.sh

cd "$(dirname "$0")/.."
cd backend
alembic upgrade head
