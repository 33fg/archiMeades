"""WO-20: Provenance graph queries - theory lineage, simulation chains."""

from fastapi import APIRouter

from app.core.neo4j import (
    check_neo4j_available,
    find_simulations_from_theory,
    get_theory_lineage,
    neo4j_session,
    trace_provenance_chain,
)

router = APIRouter(prefix="/api/provenance", tags=["provenance"])


def _get_neo4j_status() -> tuple[bool, str]:
    """Return (available, error_message)."""
    try:
        from app.core.neo4j import get_driver

        driver = get_driver()
        driver.verify_connectivity()
        driver.close()
        return True, ""
    except Exception as e:
        return False, str(e)


def _require_neo4j():
    """Raise 503 if Neo4j unavailable."""
    from app.core.exceptions import AppException

    ok, err = _get_neo4j_status()
    if not ok:
        raise AppException(f"Neo4j unavailable: {err}" if err else "Neo4j unavailable", status_code=503)


@router.get("/status")
async def provenance_status():
    """Diagnostic: Neo4j connection status and error if unavailable."""
    ok, err = _get_neo4j_status()
    from app.core.config import settings

    return {
        "available": ok,
        "error": err if not ok else None,
        "uri": settings.neo4j_uri,
        "hint": "Ensure Neo4j is running (docker compose up -d neo4j) and port 7687 is exposed. Auth: neo4j/gravitational",
    }


@router.get("/theory/{theory_id}/simulations")
async def get_theory_simulations(theory_id: str):
    """Find all simulations derived from a theory."""
    _require_neo4j()
    with neo4j_session() as session:
        sims = find_simulations_from_theory(session, theory_id)
    return {"theory_id": theory_id, "simulations": sims}


@router.get("/theory/{theory_id}/lineage")
async def get_theory_lineage_endpoint(theory_id: str):
    """Get theory lineage: simulations and publications that reference it."""
    _require_neo4j()
    with neo4j_session() as session:
        lineage = get_theory_lineage(session, theory_id)
    return lineage


@router.get("/simulation/{simulation_id}/chain")
async def get_provenance_chain(simulation_id: str):
    """Trace full provenance chain for a simulation."""
    _require_neo4j()
    with neo4j_session() as session:
        chain = trace_provenance_chain(session, simulation_id)
    return chain


@router.get("/{result_type}/{result_id}")
async def get_provenance(result_type: str, result_id: str):
    """WO-47: Unified provenance endpoint. Routes by result_type (theory|simulation)."""
    if result_type == "theory":
        _require_neo4j()
        with neo4j_session() as session:
            return get_theory_lineage(session, result_id)
    if result_type == "simulation":
        _require_neo4j()
        with neo4j_session() as session:
            return trace_provenance_chain(session, result_id)
    from fastapi import HTTPException

    raise HTTPException(404, detail=f"Unknown result_type: {result_type}. Use 'theory' or 'simulation'.")
