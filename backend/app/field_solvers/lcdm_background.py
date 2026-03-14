"""WO-23: Lambda-CDM background expansion solver.

REQ-FLD-002: Lambda-CDM Background Solver
AC-FLD-002.1: E(a) = sqrt(Omega_m*a^{-3} + (1-Omega_m))
AC-FLD-002.2: a=1, Omega_m=0.315 => E=1.000 (within 1e-12)
AC-FLD-002.3: 0.01 <= a <= 1.0 => positive and finite
AC-FLD-004.1/004.4: Undefined/NaN/Inf => Inf
"""

from __future__ import annotations

from typing import Union

import numpy as np

ScalarOrArray = Union[float, np.ndarray]


def solve_lcdm_background(a: ScalarOrArray, omega_m: ScalarOrArray) -> ScalarOrArray:
    """Compute Lambda-CDM Hubble-normalized expansion rate E(a) = H(a)/H0.

    E(a) = sqrt(Omega_m * a^{-3} + (1 - Omega_m))

    Args:
        a: Scale factor (0 < a <= 1)
        omega_m: Matter density parameter

    Returns:
        E: Hubble-normalized expansion rate
    """
    scalar_input = np.isscalar(a) and np.isscalar(omega_m)
    a_arr = np.atleast_1d(np.asarray(a, dtype=np.float64))
    omega_m_arr = np.atleast_1d(np.asarray(omega_m, dtype=np.float64))

    # AC-FLD-004.4: NaN/Inf => Inf
    bad = np.isnan(a_arr) | np.isnan(omega_m_arr) | np.isinf(a_arr) | np.isinf(omega_m_arr)
    out = np.full_like(a_arr, np.inf, dtype=np.float64)
    if np.all(bad):
        return float(out.flat[0]) if scalar_input else out

    shape = np.broadcast_shapes(a_arr.shape, omega_m_arr.shape)
    a_arr = np.broadcast_to(a_arr, shape).copy()
    omega_m_arr = np.broadcast_to(omega_m_arr, shape).copy()

    # AC-FLD-002.1: E = sqrt(Omega_m * a^{-3} + (1 - Omega_m))
    omega_lambda = 1.0 - omega_m_arr
    radicand = omega_m_arr / (a_arr**3) + omega_lambda

    # AC-FLD-004.1: Negative radicand (unphysical) => Inf
    result = np.where(radicand >= 0, np.sqrt(radicand), np.inf)
    result = np.where(~bad, result, out)

    if scalar_input:
        return float(result.flat[0])
    return result
