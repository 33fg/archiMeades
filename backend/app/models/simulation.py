"""Simulation and job models."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseTable

if TYPE_CHECKING:
    from app.models.theory import Theory


class SimulationStatus(str, Enum):
    """Simulation job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ParameterSet(BaseTable, table=True):
    """Parameter set for a simulation run."""

    __tablename__ = "parameter_sets"

    parameters_json: str = Field()  # JSON-encoded parameter values
    simulation_id: str | None = Field(default=None, foreign_key="simulations.id")


class Simulation(BaseTable, table=True):
    """Simulation job record - tracks execution state and metadata."""

    __tablename__ = "simulations"

    theory_id: str = Field(foreign_key="theories.id")
    params_json: str | None = None  # {observable_type, omega_m, h0, i_rel, n_points}
    status: str = Field(default=SimulationStatus.PENDING.value, index=True)
    progress_percent: float = Field(default=0.0)
    error_message: str | None = None
    created_by_id: str | None = Field(default=None, foreign_key="users.id")
    started_at: str | None = None  # ISO timestamp
    completed_at: str | None = None  # ISO timestamp

    theory: "Theory" = Relationship(back_populates="simulations")


class SimulationOutput(BaseTable, table=True):
    """Output artifacts from a completed simulation."""

    __tablename__ = "simulation_outputs"

    simulation_id: str = Field(foreign_key="simulations.id")
    s3_key: str = Field(index=True)
    file_size: int = Field(default=0)
    checksum: str | None = None
    content_type: str | None = None
