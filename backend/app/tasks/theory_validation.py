"""Theory validation Celery task - WO-21.
Runs interface validation and updates theory record.
"""

import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.celery_app import app
from app.core.config import settings
from app.models.theory import Theory
from app.services.theory_validation import validate_theory_interface

# Sync engine for Celery worker
_sync_url = settings.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")
_engine = create_engine(_sync_url, connect_args={"check_same_thread": False} if "sqlite" in _sync_url else {})
_SessionLocal = sessionmaker(_engine, class_=Session, expire_on_commit=False)


@app.task(bind=True, name="app.tasks.theory_validation.validate_theory_task")
def validate_theory_task(self, theory_id: str) -> dict:
    """Validate theory interface and update theory record."""
    with _SessionLocal() as session:
        theory = session.exec(select(Theory).where(Theory.id == theory_id)).first()
        if not theory:
            return {"error": "Theory not found", "theory_id": theory_id}
        if not theory.code:
            report = {"error": "No code to validate"}
            theory.validation_passed = False
            theory.validation_report = json.dumps(report)
            session.add(theory)
            session.commit()
            return {"theory_id": theory_id, "validation_passed": False, "report": report}

        result = validate_theory_interface(theory.code)
        report = {
            "passed": result.passed,
            "missing_methods": result.missing_methods,
            "errors": result.errors,
        }
        theory.validation_passed = result.passed
        theory.validation_report = json.dumps(report)
        session.add(theory)
        session.commit()
        return {"theory_id": theory_id, "validation_passed": result.passed, "report": report}
