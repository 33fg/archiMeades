"""WO-52: Physics Methods Library — API for UI access."""

from fastapi import APIRouter

from app.physics_methods import get_physics_method_catalog

router = APIRouter(prefix="/api/physics-methods", tags=["physics-methods"])


@router.get("/catalog")
def get_catalog():
    """Return physics methods catalog: formula, regime, status (WO-52)."""
    catalog = get_physics_method_catalog()
    return [
        {
            "id": m.id,
            "name": m.name,
            "formula": m.formula,
            "regime": m.regime,
            "status": m.status,
            "module": m.module,
        }
        for m in catalog
    ]
