"""Theory repository."""

from sqlalchemy import select

from app.models.theory import Theory
from app.repositories.base import BaseRepository


class TheoryRepository(BaseRepository[Theory]):
    """Repository for Theory entities."""

    def __init__(self, session) -> None:
        super().__init__(session, Theory)

    async def get_by_identifier(self, identifier: str) -> Theory | None:
        """Get theory by identifier or name (for legacy theories without identifier)."""
        result = await self.session.execute(
            select(Theory).where(
                (Theory.identifier == identifier) | (Theory.name == identifier)
            )
        )
        return result.scalar_one_or_none()
