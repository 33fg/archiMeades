"""Publication model for research output."""

from sqlmodel import Field, SQLModel

from app.models.base import BaseTable


class Publication(BaseTable, table=True):
    """Published research output."""

    __tablename__ = "publications"

    title: str = Field(index=True)
    abstract: str | None = None
    doi: str | None = Field(default=None, unique=True, index=True)
    authors_json: str | None = None
    metadata_json: str | None = None
