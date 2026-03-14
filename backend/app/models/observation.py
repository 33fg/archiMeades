"""Observation and observational data models."""

from sqlmodel import Field, SQLModel

from app.models.base import BaseTable


class Observation(BaseTable, table=True):
    """Observation dataset (e.g., lensing survey)."""

    __tablename__ = "observations"

    name: str = Field(index=True)
    description: str | None = None
    source: str | None = None  # e.g., HST, JWST, Gaia
    metadata_json: str | None = None


class ObservationData(BaseTable, table=True):
    """Individual data points within an observation."""

    __tablename__ = "observation_data"

    observation_id: str = Field(foreign_key="observations.id")
    s3_key: str | None = Field(default=None, index=True)
    values_json: str = Field()  # JSON-encoded data values
