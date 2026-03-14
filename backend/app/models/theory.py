"""Theory model - gravitational theory definitions."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseTable

if TYPE_CHECKING:
    from app.models.simulation import Simulation


class Theory(BaseTable, table=True):
    """Gravitational theory definition."""

    __tablename__ = "theories"

    name: str = Field(index=True)
    description: str | None = None
    equation_spec: str | None = None  # JSON or DSL for theory equations
    author_id: str | None = Field(default=None, foreign_key="users.id")
    # WO-21: Theory registration and validation
    identifier: str | None = Field(default=None, index=True, unique=True)  # programmatic name
    version: str | None = None
    code: str | None = None  # theory implementation code
    validation_passed: bool | None = None
    validation_report: str | None = None  # JSON string with test results

    simulations: list["Simulation"] = Relationship(back_populates="theory")
