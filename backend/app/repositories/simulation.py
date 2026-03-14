"""Simulation, ParameterSet, and SimulationOutput repositories."""

from typing import Any

from sqlalchemy.orm import selectinload

from app.models.simulation import Simulation, SimulationOutput
from app.repositories.base import BaseRepository


class SimulationRepository(BaseRepository[Simulation]):
    """Repository for Simulation entities with eager loading support."""

    def __init__(self, session) -> None:
        super().__init__(session, Simulation)

    async def get_by_id_with_theory(self, id: str) -> Simulation | None:
        """Get simulation by ID with theory eagerly loaded (avoids N+1)."""
        return await self.get_by_id(id, options=(selectinload(Simulation.theory),))

    async def list_with_theory(
        self, *, limit: int = 100, offset: int = 0, **filters: Any
    ) -> list[Simulation]:
        """List simulations with theory eagerly loaded."""
        result = await self.list(
            limit=limit,
            offset=offset,
            options=(selectinload(Simulation.theory),),
            **filters,
        )
        return list(result)

    async def list_by_status(self, status: str, *, limit: int = 100) -> list[Simulation]:
        """List simulations by status."""
        result = await self.list(status=status, limit=limit)
        return list(result)


class SimulationOutputRepository(BaseRepository[SimulationOutput]):
    """Repository for SimulationOutput entities."""

    def __init__(self, session) -> None:
        super().__init__(session, SimulationOutput)
