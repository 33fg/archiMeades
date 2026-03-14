"""Theories API - CRUD for gravitational theory definitions.
WO-21: Theory registration and validation.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.repositories.theory import TheoryRepository
from app.services.theory_validation import validate_theory_interface
from app.tasks.theory_validation import validate_theory_task
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/theories", tags=["theories"])


class TheoryCreate(BaseModel):
    """Schema for creating a theory."""

    name: str
    description: str | None = None
    equation_spec: str | None = None


class TheoryUpdate(BaseModel):
    """Schema for updating a theory (partial)."""

    name: str | None = None
    description: str | None = None
    equation_spec: str | None = None


class TheoryRead(BaseModel):
    """Schema for reading a theory."""

    id: str
    name: str
    identifier: str | None = None
    description: str | None = None
    equation_spec: str | None = None

    model_config = {"from_attributes": True}


class TheoryRegister(BaseModel):
    """Schema for theory registration - WO-21."""

    identifier: str
    version: str
    code: str


class ValidationStatusRead(BaseModel):
    """Schema for validation status - WO-21."""

    theory_id: str
    validation_passed: bool | None
    validation_report: dict | None


@router.post("/register", status_code=202)
async def register_theory(
    data: TheoryRegister,
    session: AsyncSession = Depends(get_db),
):
    """Register a theory with code. Runs interface validation async, returns 202 with status URL."""
    from app.core.exceptions import ValidationError

    # Quick interface check - fail fast if syntax/missing methods
    result = validate_theory_interface(data.code)
    if not result.passed:
        raise ValidationError(
            "Interface validation failed",
            detail={
                "missing_methods": result.missing_methods,
                "errors": result.errors,
            },
        )

    repo = TheoryRepository(session)
    existing = await repo.get_by_identifier(data.identifier)
    if existing:
        raise ValidationError(
            f"Theory identifier '{data.identifier}' already registered",
            detail={"identifier": data.identifier},
        )

    theory = await repo.create(
        name=data.identifier,
        identifier=data.identifier,
        version=data.version,
        code=data.code,
        validation_passed=False,
    )
    await session.flush()
    from app.services.provenance_sync import sync_theory

    sync_theory(theory.id, identifier=data.identifier, version=data.version)
    validate_theory_task.delay(theory.id)

    return {
        "message": "Validation job enqueued",
        "theory_id": theory.id,
        "status_url": f"/api/theories/{theory.id}/validation-status",
    }


@router.get("/{theory_id}/validation-status", response_model=ValidationStatusRead)
async def get_validation_status(
    theory_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get theory validation status and report - WO-21."""
    import json

    from app.core.exceptions import ResourceNotFoundError

    repo = TheoryRepository(session)
    theory = await repo.get_by_id(theory_id)
    if theory is None:
        raise ResourceNotFoundError("Theory not found", detail={"theory_id": theory_id})

    report = None
    if theory.validation_report:
        try:
            report = json.loads(theory.validation_report)
        except (json.JSONDecodeError, TypeError):
            report = {"raw": theory.validation_report}

    return ValidationStatusRead(
        theory_id=theory.id,
        validation_passed=theory.validation_passed,
        validation_report=report,
    )


@router.get("", response_model=list[TheoryRead])
async def list_theories(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    """List theories with pagination."""
    repo = TheoryRepository(session)
    theories = await repo.list(limit=limit, offset=offset, order_by="-created_at")
    return [TheoryRead.model_validate(t) for t in theories]


@router.post("", response_model=TheoryRead)
async def create_theory(
    data: TheoryCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new theory."""
    from app.services.provenance_sync import sync_theory

    repo = TheoryRepository(session)
    theory = await repo.create(**data.model_dump())
    sync_theory(theory.id, identifier=getattr(theory, "identifier", None))
    return theory


@router.patch("/{theory_id}", response_model=TheoryRead)
async def update_theory(
    theory_id: str,
    data: TheoryUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update a theory by ID (partial update)."""
    from app.core.exceptions import ResourceNotFoundError
    repo = TheoryRepository(session)
    theory = await repo.update(theory_id, **data.model_dump(exclude_unset=True))
    if theory is None:
        raise ResourceNotFoundError("Theory not found", detail={"theory_id": theory_id})
    return theory


@router.get("/{theory_id}", response_model=TheoryRead)
async def get_theory(
    theory_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get a theory by ID."""
    repo = TheoryRepository(session)
    theory = await repo.get_by_id(theory_id)
    if theory is None:
        from app.core.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("Theory not found", detail={"theory_id": theory_id})
    return theory


@router.delete("/{theory_id}", status_code=204)
async def delete_theory(
    theory_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Delete a theory by ID."""
    from app.core.exceptions import ConflictError, ResourceNotFoundError
    from app.repositories.simulation import SimulationRepository

    theory_repo = TheoryRepository(session)
    theory = await theory_repo.get_by_id(theory_id)
    if theory is None:
        raise ResourceNotFoundError("Theory not found", detail={"theory_id": theory_id})

    sim_repo = SimulationRepository(session)
    sims = await sim_repo.list(theory_id=theory_id, limit=1)
    if sims:
        raise ConflictError(
            "Cannot delete theory: it has simulations. Delete or reassign the simulations first.",
            detail={"theory_id": theory_id},
        )

    deleted = await theory_repo.delete(theory_id)
    assert deleted
