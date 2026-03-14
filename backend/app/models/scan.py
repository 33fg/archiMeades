"""WO-31: Parameter scan model."""

from sqlmodel import Field, Column, JSON

from app.models.base import BaseTable


class ParameterScan(BaseTable, table=True):
    """Parameter scan configuration and result metadata."""

    __tablename__ = "parameter_scans"

    theory_id: str = Field(index=True)
    dataset_id: str = Field(index=True)
    # axes: list of {name, min, max, n, scale}
    axes_config: list[dict] = Field(sa_column=Column(JSON), default_factory=list)
    # Fixed params (omega_m, h0, i_rel when not scanned)
    fixed_params: dict = Field(sa_column=Column(JSON), default_factory=dict)
    status: str = Field(default="pending", index=True)  # pending, running, completed, failed
    total_points: int = Field(default=0)
    # Result: chi2 values as flat array (or 1D/2D/3D shape stored separately)
    result_shape: list[int] = Field(sa_column=Column(JSON), default_factory=list)
    result_ref: str | None = None  # S3 key or inline for small results
    error_message: str | None = None
    job_id: str | None = Field(default=None, index=True)  # Celery job ID when async
