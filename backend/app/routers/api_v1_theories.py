"""API v1 theory query and observable prediction endpoints.
WO-49: Implement Theory Query and Observable Prediction Endpoints
"""

import subprocess
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user_required, get_db
from app.core.exceptions import UnauthorizedError
from app.repositories.theory import TheoryRepository
from app.services.theory_execution import (
    DEFAULT_PARAMS,
    compute_hubble_parameter,
    compute_luminosity_distance,
    get_callables,
    has_observable,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="", tags=["api-v1-theories"])

MAX_BATCH_REDSHIFTS = 10_000  # AC-API-003.1


def _get_git_commit() -> str:
    """Code version (git commit hash) for provenance. AC-API-008.1"""
    try:
        import os

        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=root,
        )
        return (r.stdout or "").strip()[:12] or "unknown"
    except Exception:
        return "unknown"


def _bibtex_citation(theory_name: str, theory_version: str | None) -> str:
    """BibTeX citation for theory. AC-API-001.4, AC-API-008.2"""
    ver = theory_version or "1.0"
    return f"""@software{{{theory_name.replace(" ", "_").lower()}_{ver.replace(".", "_")},
  author = {{ArchiMeades Platform}},
  title = {{{theory_name} (v{ver})}},
  year = {{2026}},
  url = {{https://github.com/33fg/archiMeades}}
}}"""


class TheoryListItem(BaseModel):
    """AC-API-001.1: Theory list item."""

    identifier: str
    name: str
    version: str | None
    description: str | None
    supported_observables: list[str]


class TheoryDetail(BaseModel):
    """AC-API-001.2: Theory detail with parameters and citation."""

    identifier: str
    name: str
    version: str | None
    description: str | None
    parameters: dict[str, float]
    citation: str


class PredictionRequest(BaseModel):
    """Request body for luminosity_distance, hubble_parameter. AC-API-003.1: max 10,000."""

    redshifts: list[float] = Field(..., min_length=1, max_length=MAX_BATCH_REDSHIFTS)
    parameters: dict[str, float] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "redshifts": [0.1, 0.5, 1.0],
                    "parameters": {"H0": 70.0, "Om": 0.3},
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """AC-API-008: Response with provenance metadata."""

    theory: str
    version: str | None
    observable: str
    values: list[float]
    redshifts: list[float]
    parameters_used: dict[str, float]
    code_version: str
    computation_timestamp: str
    precision: str
    backend: str
    citation: str


def _require_api_key(user):
    if user.cognito_sub != "api-key":
        raise UnauthorizedError("This endpoint requires API key authentication")


@router.get("/theories", response_model=list[TheoryListItem])
async def list_theories(
    user=Depends(get_current_user_required),
    session: AsyncSession = Depends(get_db),
):
    """AC-API-001.1: List all registered theories with supported observables."""
    _require_api_key(user)
    repo = TheoryRepository(session)
    theories = await repo.list(limit=500)
    result: list[TheoryListItem] = []
    for t in theories:
        supported: list[str] = []
        if t.code:
            try:
                callables = get_callables(t.code)
                if "luminosity_distance" in callables:
                    supported.append("luminosity_distance")
                if "age_of_universe" in callables:
                    supported.append("age_of_universe")
                if "hubble_parameter" in callables:
                    supported.append("hubble_parameter")
            except Exception:
                pass
        result.append(
            TheoryListItem(
                identifier=t.identifier or t.name,
                name=t.name,
                version=t.version,
                description=t.description,
                supported_observables=supported,
            )
        )
    return result


@router.get("/theory/{identifier}", response_model=TheoryDetail)
async def get_theory(
    identifier: str,
    user=Depends(get_current_user_required),
    session: AsyncSession = Depends(get_db),
):
    """AC-API-001.2: Theory details. AC-API-001.3: 404 when not found."""
    _require_api_key(user)
    repo = TheoryRepository(session)
    theory = await repo.get_by_identifier(identifier)
    if not theory:
        all_ids = [t.identifier or t.name for t in (await repo.list(limit=100))]
        raise HTTPException(
            status_code=404,
            detail={"message": "Theory not found", "available_theories": all_ids},
        )
    return TheoryDetail(
        identifier=theory.identifier or theory.name,
        name=theory.name,
        version=theory.version,
        description=theory.description,
        parameters=DEFAULT_PARAMS,
        citation=_bibtex_citation(theory.name, theory.version),
    )


@router.post("/theory/{identifier}/luminosity_distance", response_model=PredictionResponse)
async def luminosity_distance(
    identifier: str,
    body: PredictionRequest,
    user=Depends(get_current_user_required),
    session: AsyncSession = Depends(get_db),
):
    """AC-API-002.1: Luminosity distances in Mpc."""
    _require_api_key(user)
    repo = TheoryRepository(session)
    theory = await repo.get_by_identifier(identifier)
    if not theory:
        raise HTTPException(status_code=404, detail="Theory not found")
    if not theory.code:
        raise HTTPException(status_code=400, detail="Theory has no executable code")
    if not has_observable(get_callables(theory.code), "luminosity_distance"):
        raise HTTPException(
            status_code=400,
            detail="Observable luminosity_distance not supported by this theory",
        )
    try:
        result = compute_luminosity_distance(
            theory.code, body.redshifts, body.parameters
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    params = {**DEFAULT_PARAMS, **(body.parameters or {})}
    return PredictionResponse(
        theory=theory.name,
        version=theory.version,
        observable="luminosity_distance",
        values=result.values,
        redshifts=body.redshifts,
        parameters_used=params,
        code_version=_get_git_commit(),
        computation_timestamp=datetime.now(timezone.utc).isoformat(),
        precision=result.precision,
        backend=result.backend,
        citation=_bibtex_citation(theory.name, theory.version),
    )


@router.post("/theory/{identifier}/hubble_parameter", response_model=PredictionResponse)
async def hubble_parameter(
    identifier: str,
    body: PredictionRequest,
    user=Depends(get_current_user_required),
    session: AsyncSession = Depends(get_db),
):
    """AC-API-002.2: H(z) in km/s/Mpc."""
    _require_api_key(user)
    repo = TheoryRepository(session)
    theory = await repo.get_by_identifier(identifier)
    if not theory:
        raise HTTPException(status_code=404, detail="Theory not found")
    if not theory.code:
        raise HTTPException(status_code=400, detail="Theory has no executable code")
    if not has_observable(get_callables(theory.code), "hubble_parameter"):
        raise HTTPException(
            status_code=400,
            detail="Observable hubble_parameter not supported by this theory",
        )
    try:
        result = compute_hubble_parameter(
            theory.code, body.redshifts, body.parameters
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    params = {**DEFAULT_PARAMS, **(body.parameters or {})}
    return PredictionResponse(
        theory=theory.name,
        version=theory.version,
        observable="hubble_parameter",
        values=result.values,
        redshifts=body.redshifts,
        parameters_used=params,
        code_version=_get_git_commit(),
        computation_timestamp=datetime.now(timezone.utc).isoformat(),
        precision=result.precision,
        backend=result.backend,
        citation=_bibtex_citation(theory.name, theory.version),
    )
