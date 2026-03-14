"""WO-42: Observable prediction API for Theory Exploration Mode.

POST /api/observables/distance_modulus - theory predictions for distance modulus at given redshifts.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.observables import distance_modulus, luminosity_distance_theory

router = APIRouter(prefix="/api/observables", tags=["observables"])


class DistanceModulusRequest(BaseModel):
    """Request for distance modulus predictions."""

    theory_id: str
    redshifts: list[float]
    omega_m: float = 0.31
    i_rel: float = 1.451782
    h0: float = 70.0


@router.post("/distance_modulus")
def predict_distance_modulus(body: DistanceModulusRequest) -> dict:
    """Compute distance modulus μ(z) for theory at given redshifts.

    WO-42: Used by Explore page for theory curve overlay.
    AC-IRE-003.1: Distance modulus plot with theory prediction.
    """
    if body.theory_id.lower() not in ("lcdm", "lambdacdm", "lambda-cdm", "g4v"):
        raise HTTPException(422, f"Theory '{body.theory_id}' not supported for distance modulus")
    if len(body.redshifts) > 10_000:
        raise HTTPException(422, "Max 10,000 redshifts per request")
    if not body.redshifts:
        return {"distance_modulus": [], "redshifts": []}

    import numpy as np

    z = np.array(body.redshifts, dtype=np.float64)
    try:
        d_l = luminosity_distance_theory(
            z,
            body.theory_id,
            omega_m=body.omega_m,
            i_rel=body.i_rel,
            h0=body.h0,
        )
        mu = distance_modulus(d_l)
        # Convert inf/nan to null for JSON
        mu_list = [float(x) if np.isfinite(x) else None for x in np.atleast_1d(mu).flat]
    except Exception as e:
        raise HTTPException(500, str(e)) from e
    return {"redshifts": body.redshifts, "distance_modulus": mu_list}
