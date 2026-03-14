"""Observations API - list and manage observational datasets.

WO-29: Dataset management API - GET /datasets, GET /datasets/{id}, POST /upload.
"""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.repositories.observation import ObservationRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/observations", tags=["observations"])


class ObservationCreate(BaseModel):
    """Schema for creating an observation."""

    name: str
    description: str | None = None
    source: str | None = None
    metadata_json: str | None = None


class ObservationUpdate(BaseModel):
    """Schema for updating an observation (partial)."""

    name: str | None = None
    description: str | None = None
    source: str | None = None
    metadata_json: str | None = None


class ObservationRead(BaseModel):
    """Schema for reading an observation."""

    id: str
    name: str
    description: str | None
    source: str | None
    metadata_json: str | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ObservationRead])
async def list_observations(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    """List observations with pagination."""
    repo = ObservationRepository(session)
    obs = await repo.list(limit=limit, offset=offset, order_by="-created_at")
    return list(obs)


@router.post("", response_model=ObservationRead)
async def create_observation(
    data: ObservationCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new observation."""
    from app.services.provenance_sync import sync_observation

    repo = ObservationRepository(session)
    obs = await repo.create(**data.model_dump())
    sync_observation(obs.id)
    return obs


# ---- WO-29: Dataset management (built-in + custom) ----
# NOTE: Must be before /{observation_id} so /datasets is not matched as observation_id


class DatasetSummary(BaseModel):
    """Summary of a dataset for listing."""

    id: str
    name: str
    type: str  # "builtin" | "custom"
    num_points: int | None = None
    observable_type: str | None = None
    citation: str | None = None
    unavailable_hint: str | None = None  # e.g. "~800K (download required)" when load fails


class DatasetDetail(BaseModel):
    """Full dataset metadata for detail view."""

    id: str
    name: str
    type: str
    num_points: int
    observable_type: str
    citation: str
    redshift_min: float | None = None
    redshift_max: float | None = None
    covariance_shape: list[int] | None = None


# Hint when builtin dataset fails to load (e.g. file not downloaded)
BUILTIN_UNAVAILABLE_HINTS: dict[str, str] = {
    "sdss_dr17_mpajhu": "~800K (download required)",
}


@router.get("/datasets", response_model=list[DatasetSummary])
async def list_datasets(session: AsyncSession = Depends(get_db)):
    """WO-29: List all available datasets (built-in + custom)."""
    from app.datasets import BUILTIN_DATASET_NAMES, list_builtin_datasets, load_dataset

    result: list[DatasetSummary] = []
    for ds_id in list_builtin_datasets():
        try:
            ds = load_dataset(ds_id)
            result.append(
                DatasetSummary(
                    id=ds_id,
                    name=BUILTIN_DATASET_NAMES.get(ds_id, ds_id),
                    type="builtin",
                    num_points=ds.num_points,
                    observable_type=ds.observable_type,
                    citation=ds.citation,
                )
            )
        except Exception:
            result.append(
                DatasetSummary(
                    id=ds_id,
                    name=BUILTIN_DATASET_NAMES.get(ds_id, ds_id),
                    type="builtin",
                    num_points=None,
                    unavailable_hint=BUILTIN_UNAVAILABLE_HINTS.get(ds_id),
                )
            )
    repo = ObservationRepository(session)
    custom = await repo.list(limit=500, offset=0)
    for obs in custom:
        meta = {}
        if obs.metadata_json:
            try:
                import json

                meta = json.loads(obs.metadata_json) or {}
            except Exception:
                pass
        result.append(
            DatasetSummary(
                id=obs.id,
                name=obs.name,
                type="custom",
                num_points=meta.get("num_points"),
                observable_type=meta.get("observable_type"),
                citation=meta.get("citation"),
            )
        )
    return result


@router.get("/datasets/{dataset_id}", response_model=DatasetDetail)
async def get_dataset_detail(
    dataset_id: str,
    session: AsyncSession = Depends(get_db),
):
    """WO-29: Get dataset metadata and statistics."""
    from app.datasets import BUILTIN_DATASET_NAMES, load_dataset

    if dataset_id in BUILTIN_DATASET_NAMES or dataset_id in ("pantheon",):
        try:
            ds = load_dataset(dataset_id)
            return DatasetDetail(
                id=dataset_id,
                name=BUILTIN_DATASET_NAMES.get(dataset_id, dataset_id),
                type="builtin",
                num_points=ds.num_points,
                observable_type=ds.observable_type,
                citation=ds.citation,
                redshift_min=float(ds.redshift.min()),
                redshift_max=float(ds.redshift.max()),
                covariance_shape=list(ds.systematic_covariance.shape),
            )
        except Exception as e:
            raise ResourceNotFoundError(
                f"Dataset '{dataset_id}' unavailable",
                detail={"error": str(e)},
            ) from e
    repo = ObservationRepository(session)
    obs = await repo.get_by_id(dataset_id)
    if obs is None:
        raise ResourceNotFoundError("Dataset not found", detail={"dataset_id": dataset_id})
    meta = {}
    if obs.metadata_json:
        try:
            import json

            meta = json.loads(obs.metadata_json) or {}
        except Exception:
            pass
    return DatasetDetail(
        id=obs.id,
        name=obs.name,
        type="custom",
        num_points=meta.get("num_points", 0),
        observable_type=meta.get("observable_type", "unknown"),
        citation=meta.get("citation", ""),
        redshift_min=meta.get("redshift_min"),
        redshift_max=meta.get("redshift_max"),
        covariance_shape=meta.get("covariance_shape"),
    )


class DatasetDataResponse(BaseModel):
    """WO-42: Redshift and observable arrays for plotting."""

    redshift: list[float]
    observable: list[float]
    stat_unc: list[float]


@router.get("/datasets/{dataset_id}/data", response_model=DatasetDataResponse)
async def get_dataset_data(
    dataset_id: str,
    session: AsyncSession = Depends(get_db),
):
    """WO-42: Return redshift, observable, stat_unc for builtin datasets (Explore view).
    WO-67: Also supports simulation-derived datasets (Observation with ObservationData)."""
    from app.datasets import BUILTIN_DATASET_NAMES, load_dataset
    from sqlalchemy import select

    from app.models.observation import ObservationData

    if dataset_id in BUILTIN_DATASET_NAMES or dataset_id in ("pantheon", "synthetic"):
        ds = load_dataset(dataset_id)
        return DatasetDataResponse(
            redshift=[float(z) for z in ds.redshift],
            observable=[float(mu) for mu in ds.observable],
            stat_unc=[float(s) for s in ds.statistical_uncertainty],
        )

    # WO-67: Custom dataset from simulation registration
    import json

    result = await session.execute(
        select(ObservationData).where(ObservationData.observation_id == dataset_id).limit(1)
    )
    od = result.scalars().first()
    if od is None:
        raise ResourceNotFoundError(
            "Dataset data not found (builtin or registered simulation dataset)",
            detail={"dataset_id": dataset_id},
        )
    data = json.loads(od.values_json)
    return DatasetDataResponse(
        redshift=[float(z) for z in data["redshift"]],
        observable=[float(o) for o in data["observable"]],
        stat_unc=[float(s) for s in data["statistical_uncertainty"]],
    )


# ---- Observation CRUD (/{observation_id}) ----
@router.patch("/{observation_id}", response_model=ObservationRead)
async def update_observation(
    observation_id: str,
    data: ObservationUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update an observation by ID (partial update)."""
    repo = ObservationRepository(session)
    obs = await repo.update(observation_id, **data.model_dump(exclude_unset=True))
    if obs is None:
        raise ResourceNotFoundError("Observation not found", detail={"observation_id": observation_id})
    return obs


@router.get("/{observation_id}", response_model=ObservationRead)
async def get_observation(
    observation_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get an observation by ID."""
    repo = ObservationRepository(session)
    obs = await repo.get_by_id(observation_id)
    if obs is None:
        raise ResourceNotFoundError("Observation not found", detail={"observation_id": observation_id})
    return obs


@router.delete("/{observation_id}", status_code=204)
async def delete_observation(
    observation_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Delete an observation by ID."""
    repo = ObservationRepository(session)
    deleted = await repo.delete(observation_id)
    if not deleted:
        raise ResourceNotFoundError("Observation not found", detail={"observation_id": observation_id})


@router.post("/upload", response_model=ObservationRead)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str | None = Form(None),
    session: AsyncSession = Depends(get_db),
):
    """WO-29: Upload custom dataset (CSV). Parses and stores metadata."""
    import csv
    import json

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise ValidationError("Only CSV uploads supported", detail={"filename": file.filename})
    content = (await file.read()).decode("utf-8", errors="replace")
    reader = csv.DictReader(content.splitlines())
    rows = list(reader)
    if not rows:
        raise ValidationError("Empty or invalid CSV", detail={})
    # Infer columns: look for z/redshift, mb/observable, dmb/stat_unc
    cols = list(rows[0].keys())
    z_col = next((c for c in cols if c.lower() in ("z", "zcmb", "redshift")), cols[0])
    obs_col = next((c for c in cols if c.lower() in ("mb", "mu", "observable", "distance_modulus")), cols[1] if len(cols) > 1 else cols[0])
    stat_col = next((c for c in cols if c.lower() in ("dmb", "sigma", "stat_unc", "err")), None)
    z_vals = []
    obs_vals = []
    stat_vals = []
    for row in rows:
        try:
            z_vals.append(float(row[z_col]))
            obs_vals.append(float(row[obs_col]))
            stat_vals.append(float(row[stat_col]) if stat_col and row.get(stat_col) else 0.1)
        except (ValueError, KeyError):
            continue
    if not z_vals:
        raise ValidationError("No valid data rows in CSV", detail={})
    # Store as Observation with metadata
    meta = {
        "num_points": len(z_vals),
        "observable_type": "distance_modulus",
        "redshift_min": min(z_vals),
        "redshift_max": max(z_vals),
        "columns": {"z": z_col, "observable": obs_col, "stat_unc": stat_col},
    }
    repo = ObservationRepository(session)
    obs = await repo.create(
        name=name or file.filename or "Uploaded dataset",
        source="csv_upload",
        metadata_json=json.dumps(meta),
    )
    return obs
