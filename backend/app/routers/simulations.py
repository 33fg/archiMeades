"""Simulations API - list and manage GPU simulation runs.

WO-13: Job dispatch, status polling.
WO-67: Simulation Output Integration - register completed simulation as dataset.
"""

import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.models.observation import Observation, ObservationData
from app.repositories.observation import ObservationRepository
from app.repositories.simulation import SimulationOutputRepository, SimulationRepository
from app.repositories.theory import TheoryRepository
from app.services.s3 import get_object
from app.tasks.simulation import run_simulation_task

router = APIRouter(prefix="/api/simulations", tags=["simulations"])


class SimulationCreate(BaseModel):
    """Schema for creating a simulation."""

    theory_id: str
    observable_type: str = "distance_modulus"
    omega_m: float = 0.31
    h0: float = 70.0
    i_rel: float = 1.451782
    n_points: int = 50
    n_particles: int = 64
    n_steps: int = 100
    dt: float = 1e4


class SimulationUpdate(BaseModel):
    """Schema for updating a simulation (partial)."""

    status: str | None = None


class SimulationRead(BaseModel):
    """Schema for reading a simulation."""

    id: str
    theory_id: str
    params_json: str | None = None
    status: str
    progress_percent: float
    error_message: str | None
    started_at: str | None
    completed_at: str | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[SimulationRead])
async def list_simulations(
    limit: int = 100,
    offset: int = 0,
    status: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    """List simulations with optional status filter."""
    repo = SimulationRepository(session)
    filters = {"status": status} if status else {}
    sims = await repo.list(limit=limit, offset=offset, order_by="-created_at", **filters)
    return list(sims)


@router.post("", response_model=SimulationRead)
async def create_simulation(
    data: SimulationCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new simulation and enqueue Celery task for GPU execution."""
    from app.services.provenance_sync import sync_simulation, sync_theory

    theory_repo = TheoryRepository(session)
    theory = await theory_repo.get_by_id(data.theory_id)
    if theory is None:
        raise ValidationError("Theory not found", detail={"theory_id": data.theory_id})
    params = {
        "observable_type": data.observable_type,
        "omega_m": data.omega_m,
        "h0": data.h0,
        "i_rel": data.i_rel,
        "n_points": data.n_points,
        "n_particles": data.n_particles,
        "n_steps": data.n_steps,
        "dt": data.dt,
    }
    repo = SimulationRepository(session)
    sim = await repo.create(theory_id=data.theory_id, params_json=json.dumps(params))
    sync_theory(theory.id, identifier=getattr(theory, "identifier", None))
    sync_simulation(sim.id, sim.theory_id, status=sim.status)
    run_simulation_task.delay(sim.id)
    return sim


@router.get("/nbody-preview")
async def get_nbody_preview(
    n_particles: int = 48,
    n_steps: int = 50,
    n_points: int = 30,
):
    """Run a quick N-body simulation and return particle_positions for visualization.

    Use when simulation output is unavailable (e.g. S3 not configured).
    """
    from app.simulations.nbody import run_nbody_simulation

    data = run_nbody_simulation(
        theory_id="preview",
        theory_name="Preview",
        n_particles=min(max(n_particles, 16), 128),
        n_steps=min(max(n_steps, 20), 100),
        n_points=min(max(n_points, 10), 50),
    )
    return {
        "observational_dataset": {
            "particle_positions": data.get("particle_positions", []),
            "n_particles": data.get("n_particles"),
            "n_steps": data.get("n_steps"),
        },
    }


@router.get("/{simulation_id}/output-data")
async def get_simulation_output_data(
    simulation_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get simulation output JSON (for N-body visualization, etc.)."""
    sim_repo = SimulationRepository(session)
    sim = await sim_repo.get_by_id(simulation_id)
    if sim is None:
        raise ResourceNotFoundError("Simulation not found", detail={"simulation_id": simulation_id})
    if sim.status != "completed":
        raise ValidationError(
            "Simulation must be completed to fetch output",
            detail={"status": sim.status},
        )
    out_repo = SimulationOutputRepository(session)
    outputs = await out_repo.list(simulation_id=simulation_id, limit=1)
    if not outputs:
        raise ValidationError(
            "Simulation has no outputs",
            detail={"simulation_id": simulation_id},
        )
    output = outputs[0]
    try:
        body = get_object(output.s3_key)
    except Exception as e:
        raise ResourceNotFoundError(
            f"Could not fetch simulation output: {e!s}",
            detail={"s3_key": output.s3_key},
        ) from e
    return json.loads(body.decode("utf-8"))


@router.get("/{simulation_id}/status")
async def get_simulation_status(
    simulation_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Lightweight status and progress for polling."""
    repo = SimulationRepository(session)
    sim = await repo.get_by_id(simulation_id)
    if sim is None:
        raise ResourceNotFoundError("Simulation not found", detail={"simulation_id": simulation_id})
    return {
        "id": sim.id,
        "status": sim.status,
        "progress_percent": sim.progress_percent,
        "error_message": sim.error_message,
    }


@router.get("/{simulation_id}", response_model=SimulationRead)
async def get_simulation(
    simulation_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get a simulation by ID."""
    repo = SimulationRepository(session)
    sim = await repo.get_by_id(simulation_id)
    if sim is None:
        raise ResourceNotFoundError("Simulation not found", detail={"simulation_id": simulation_id})
    return sim


@router.patch("/{simulation_id}", response_model=SimulationRead)
async def update_simulation(
    simulation_id: str,
    data: SimulationUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update a simulation by ID (e.g. cancel)."""
    repo = SimulationRepository(session)
    sim = await repo.update(simulation_id, **data.model_dump(exclude_unset=True))
    if sim is None:
        raise ResourceNotFoundError("Simulation not found", detail={"simulation_id": simulation_id})
    return sim


@router.delete("/{simulation_id}", status_code=204)
async def delete_simulation(
    simulation_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Delete a simulation by ID."""
    repo = SimulationRepository(session)
    deleted = await repo.delete(simulation_id)
    if not deleted:
        raise ResourceNotFoundError("Simulation not found", detail={"simulation_id": simulation_id})


class RegisterAsDatasetResponse(BaseModel):
    """WO-67: Response when registering simulation output as dataset."""

    dataset_id: str
    name: str
    num_points: int
    observable_type: str


@router.post("/{simulation_id}/register-as-dataset", response_model=RegisterAsDatasetResponse)
async def register_simulation_as_dataset(
    simulation_id: str,
    session: AsyncSession = Depends(get_db),
):
    """WO-67: Register completed simulation output as an observational dataset.

    Fetches output from S3, extracts ObservationalDataset-compatible data,
    creates Observation + ObservationData for use in Explore/Scan/MCMC.
    """
    sim_repo = SimulationRepository(session)
    sim = await sim_repo.get_by_id(simulation_id)
    if sim is None:
        raise ResourceNotFoundError("Simulation not found", detail={"simulation_id": simulation_id})
    if sim.status != "completed":
        raise ValidationError(
            "Simulation must be completed to register as dataset",
            detail={"status": sim.status},
        )

    out_repo = SimulationOutputRepository(session)
    outputs = await out_repo.list(simulation_id=simulation_id, limit=1)
    if not outputs:
        raise ValidationError(
            "Simulation has no outputs",
            detail={"simulation_id": simulation_id},
        )
    output = outputs[0]

    try:
        body = get_object(output.s3_key)
    except Exception as e:
        raise ResourceNotFoundError(
            f"Could not fetch simulation output: {e!s}",
            detail={"s3_key": output.s3_key},
        ) from e

    data = json.loads(body.decode("utf-8"))
    obs_data = data.get("observational_dataset")
    if not obs_data:
        raise ValidationError(
            "Simulation output does not contain observational_dataset (WO-69 format)",
            detail={},
        )

    # Check if already registered
    obs_repo = ObservationRepository(session)
    existing = await session.execute(
        select(Observation).where(Observation.source == f"simulation:{simulation_id}")
    )
    obs = existing.scalars().first()
    if obs:
        meta = json.loads(obs.metadata_json or "{}") if obs.metadata_json else {}
        return RegisterAsDatasetResponse(
            dataset_id=obs.id,
            name=obs.name,
            num_points=meta.get("num_points", 0),
            observable_type=meta.get("observable_type", "distance_modulus"),
        )

    # Create Observation with metadata
    name = obs_data.get("name", f"Simulated ({obs_data.get('theory_name', 'Unknown')})")
    meta = {
        "num_points": len(obs_data.get("redshift", [])),
        "observable_type": obs_data.get("observable_type", "distance_modulus"),
        "citation": obs_data.get("citation", ""),
        "simulation_id": simulation_id,
        "redshift_min": min(obs_data["redshift"]) if obs_data.get("redshift") else None,
        "redshift_max": max(obs_data["redshift"]) if obs_data.get("redshift") else None,
        "covariance_shape": (
            [len(obs_data["redshift"]), len(obs_data["redshift"])]
            if obs_data.get("redshift") and obs_data.get("systematic_covariance")
            else None
        ),
    }
    obs = await obs_repo.create(
        name=name,
        source=f"simulation:{simulation_id}",
        metadata_json=json.dumps(meta),
    )

    # Create ObservationData with full dataset for load_dataset / get_dataset_data
    values = {
        "redshift": obs_data["redshift"],
        "observable": obs_data["observable"],
        "statistical_uncertainty": obs_data["statistical_uncertainty"],
        "systematic_covariance": obs_data["systematic_covariance"],
        "observable_type": obs_data.get("observable_type", "distance_modulus"),
        "name": name,
        "citation": obs_data.get("citation", ""),
    }
    od = ObservationData(
        observation_id=obs.id,
        values_json=json.dumps(values),
    )
    session.add(od)
    await session.flush()
    await session.refresh(obs)

    return RegisterAsDatasetResponse(
        dataset_id=obs.id,
        name=obs.name,
        num_points=meta["num_points"],
        observable_type=meta["observable_type"],
    )
