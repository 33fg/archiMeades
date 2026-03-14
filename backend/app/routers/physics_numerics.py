"""WO-51: Physics & Numerics Library — API for UI access.

GET /api/physics-numerics/catalog — method catalog (AC-PNL-001.2).
"""

from fastapi import APIRouter

from app.physics_numerics import get_method_catalog

router = APIRouter(prefix="/api/physics-numerics", tags=["physics-numerics"])


@router.get("/catalog")
def get_catalog():
    """Return method catalog: formula, complexity, hardware target, precision, status."""
    catalog = get_method_catalog()
    return [
        {
            "id": m.id,
            "name": m.name,
            "formula": m.formula,
            "complexity": m.complexity,
            "hardware_target": m.hardware_target,
            "precision": m.precision,
            "status": m.status,
            "module": m.module,
        }
        for m in catalog
    ]
