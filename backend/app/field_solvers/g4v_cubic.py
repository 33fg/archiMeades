"""WO-23: G4v self-consistent cubic solver using Cardano's formula.

REQ-FLD-001: G4v Self-Consistent Cubic Solver
AC-FLD-001.1: Cubic 2*E^3 - C0*E^2 + Omega_m*a^{-3} = 0, C0 = 1.5*I_rel
AC-FLD-001.2: a=1, Omega_m=0.31, I_rel=1.451782 => E=0.912 (within 1e-6)
AC-FLD-004.1/004.2: Undefined/degenerate => Inf
AC-FLD-004.4: NaN/Inf inputs => Inf output

WO-51: Uses physics_numerics.roots for cubic solver (Layer 1).
"""

from __future__ import annotations

from typing import Union

import numpy as np

from app.physics_numerics.roots import solve_cubic

# Type for scalar or array inputs
ScalarOrArray = Union[float, np.ndarray]


def solve_g4v_cubic(
    a: ScalarOrArray,
    omega_m: ScalarOrArray,
    i_rel: ScalarOrArray,
) -> ScalarOrArray:
    """Solve G4v cubic for unique real positive root E(a).

    Equation: 2*E^3 - C0*E^2 + Omega_m*a^{-3} = 0
    where C0 = 1.5 * I_rel.

    Uses physics_numerics.roots.solve_cubic (WO-51 Layer 1).

    Args:
        a: Scale factor (0 < a <= 1)
        omega_m: Matter density parameter
        i_rel: Retardation parameter I_rel

    Returns:
        E: Hubble-normalized expansion rate H/H0
    """
    scalar_in = np.isscalar(a) and np.isscalar(omega_m) and np.isscalar(i_rel)
    c0 = 1.5 * np.asarray(i_rel, dtype=np.float64)
    a_arr = np.asarray(a, dtype=np.float64)
    d_coef = np.asarray(omega_m, dtype=np.float64) / (a_arr**3)
    a_coef = np.full_like(c0, 2.0)
    b_coef = -c0
    c_coef = np.zeros_like(c0)
    result = solve_cubic(a_coef, b_coef, c_coef, d_coef, prefer_positive=True)
    if scalar_in:
        return float(np.asarray(result).flat[0])
    return result
