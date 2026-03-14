"""User model - mapped from Cognito identity."""

from sqlmodel import Field, SQLModel

from app.models.base import BaseTable


class User(BaseTable, table=True):
    """User record synced from Cognito on first authentication."""

    __tablename__ = "users"

    email: str = Field(index=True)
    cognito_sub: str = Field(unique=True, index=True)  # Cognito user ID (sub claim)
    name: str | None = None
    role: str = Field(default="researcher", index=True)  # researcher | admin | viewer
