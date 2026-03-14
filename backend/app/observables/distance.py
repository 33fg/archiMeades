"""WO-26: Luminosity distance, distance modulus, angular diameter distance.

REQ-OBS-001: d_L(z) = (1+z) c ∫₀^z dz'/H(z')
REQ-OBS-002: μ = 5*log10(d_L/Mpc) + 25
REQ-OBS-003: d_A = d_L/(1+z)²
WO-26: Result caching keyed by (theory, parameters, redshift).
WO-51: Uses physics_numerics.distances (Layer 1) for core numerics.
"""

from __future__ import annotations

import hashlib
from typing import Union

import numpy as np

from app.field_solvers import get_expansion_solver
from app.physics_numerics.distances import (
    angular_diameter_distance,
    distance_modulus,
    luminosity_distance,
)

# WO-26: Result cache keyed by (theory, params, redshift). Max 500 entries.
_LUM_DIST_CACHE: dict[tuple[str, float, float, float, str], np.ndarray | float] = {}
_LUM_DIST_CACHE_MAX = 500


def _z_cache_key(z: Union[float, np.ndarray]) -> str:
    """Hashable key for redshift for caching."""
    if np.isscalar(z):
        return f"scalar:{z:.10e}"
    z_arr = np.asarray(z, dtype=np.float64)
    return hashlib.sha256(z_arr.tobytes()).hexdigest()


def luminosity_distance_theory(
    z: Union[float, np.ndarray],
    theory_id: str,
    omega_m: float = 0.31,
    i_rel: float = 1.451782,
    h0: float = 70.0,
) -> Union[float, np.ndarray]:
    """Compute d_L(z) using theory's expansion history. Caches results by (theory, params, z)."""
    tid = theory_id.lower()
    key = (tid, omega_m, i_rel, h0, _z_cache_key(z))
    if key in _LUM_DIST_CACHE:
        cached = _LUM_DIST_CACHE[key]
        if np.isscalar(z):
            return float(cached)
        return np.array(cached, dtype=np.float64, copy=True)
    solver = get_expansion_solver(theory_id)
    if solver is None:
        raise ValueError(f"No expansion solver for theory '{theory_id}'")

    def e_func(a: float) -> float:
        if tid == "g4v":
            return solver(a, omega_m=omega_m, i_rel=i_rel)
        return solver(a, omega_m=omega_m)

    result = luminosity_distance(z, e_func, h0)
    if len(_LUM_DIST_CACHE) >= _LUM_DIST_CACHE_MAX:
        _LUM_DIST_CACHE.clear()
    _LUM_DIST_CACHE[key] = float(result) if np.isscalar(z) else np.array(result, copy=True)
    return result
