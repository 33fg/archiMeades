"""Observation repository."""

from app.models.observation import Observation
from app.repositories.base import BaseRepository


class ObservationRepository(BaseRepository[Observation]):
    """Repository for Observation entities."""

    def __init__(self, session) -> None:
        super().__init__(session, Observation)
