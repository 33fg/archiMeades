"""WO-20: Sync PostgreSQL records to Neo4j for provenance tracking."""

import structlog

from app.core.neo4j import (
    neo4j_session,
    upsert_observation,
    upsert_publication,
    upsert_simulation,
    upsert_theory,
)

log = structlog.get_logger()


def _safe_sync(fn, *args, **kwargs) -> None:
    """Run sync in Neo4j, log and swallow errors (don't block API)."""
    try:
        with neo4j_session() as session:
            fn(session, *args, **kwargs)
    except Exception as e:
        log.warning("Provenance sync failed", error=str(e), fn=fn.__name__)


def sync_theory(theory_id: str, identifier: str | None = None, version: str | None = None) -> None:
    """Sync a theory to Neo4j."""
    _safe_sync(upsert_theory, theory_id, identifier, version)


def sync_simulation(
    sim_id: str,
    theory_id: str,
    status: str | None = None,
    duration_sec: float | None = None,
) -> None:
    """Sync a simulation to Neo4j."""
    _safe_sync(upsert_simulation, sim_id, theory_id, status, duration_sec)


def sync_observation(
    obs_id: str,
    checksum: str | None = None,
    num_points: int | None = None,
) -> None:
    """Sync an observation to Neo4j."""
    _safe_sync(upsert_observation, obs_id, checksum, num_points)


def sync_publication(
    pub_id: str,
    doi: str | None = None,
    title: str | None = None,
) -> None:
    """Sync a publication to Neo4j."""
    _safe_sync(upsert_publication, pub_id, doi, title)
