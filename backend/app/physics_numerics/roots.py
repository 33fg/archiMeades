"""WO-51: Root finding — Cardano cubic, Newton-Raphson (planned).

Extracted from WO-23 g4v_cubic. Generic cubic solver for ax³ + bx² + cx + d = 0.
Returns unique real positive root, or inf if none/unphysical.
"""

from __future__ import annotations

from typing import Union

import numpy as np

ScalarOrArray = Union[float, np.ndarray]


def solve_cubic(
    a_coef: ScalarOrArray,
    b_coef: ScalarOrArray,
    c_coef: ScalarOrArray,
    d_coef: ScalarOrArray,
    *,
    prefer_positive: bool = True,
) -> ScalarOrArray:
    """Solve cubic ax³ + bx² + cx + d = 0 for real root(s).

    Uses Cardano's formula (Delta >= 0) or trigonometric (Delta < 0, casus irreducibilis).
    When prefer_positive=True, returns the unique real positive root, or inf if none.

    Args:
        a_coef, b_coef, c_coef, d_coef: Cubic coefficients
        prefer_positive: If True, return positive root; negative/unphysical => inf

    Returns:
        Root(s), or inf for NaN/Inf inputs, degenerate (a=0), or no positive root.
    """
    scalar = (
        np.isscalar(a_coef)
        and np.isscalar(b_coef)
        and np.isscalar(c_coef)
        and np.isscalar(d_coef)
    )
    a_arr = np.atleast_1d(np.asarray(a_coef, dtype=np.float64))
    b_arr = np.atleast_1d(np.asarray(b_coef, dtype=np.float64))
    c_arr = np.atleast_1d(np.asarray(c_coef, dtype=np.float64))
    d_arr = np.atleast_1d(np.asarray(d_coef, dtype=np.float64))

    bad = (
        np.isnan(a_arr) | np.isnan(b_arr) | np.isnan(c_arr) | np.isnan(d_arr)
        | np.isinf(a_arr) | np.isinf(b_arr) | np.isinf(c_arr) | np.isinf(d_arr)
    )
    out = np.full_like(a_arr, np.inf, dtype=np.float64)
    if np.all(bad):
        return float(out.flat[0]) if scalar else out

    shape = np.broadcast_shapes(a_arr.shape, b_arr.shape, c_arr.shape, d_arr.shape)
    a_arr = np.broadcast_to(a_arr, shape).copy()
    b_arr = np.broadcast_to(b_arr, shape).copy()
    c_arr = np.broadcast_to(c_arr, shape).copy()
    d_arr = np.broadcast_to(d_arr, shape).copy()

    out = np.full(shape, np.inf, dtype=np.float64)
    valid = ~bad

    degenerate = np.abs(a_arr) < 1e-15
    valid = valid & ~degenerate
    if not np.any(valid):
        return float(out.flat[0]) if scalar else out

    # Depressed cubic: x = y - b/(3a), y³ + p*y + q = 0
    p = (3 * a_arr * c_arr - b_arr**2) / (3 * a_arr**2)
    q = (
        2 * b_arr**3
        - 9 * a_arr * b_arr * c_arr
        + 27 * a_arr**2 * d_arr
    ) / (27 * a_arr**3)

    delta = (q / 2) ** 2 + (p / 3) ** 3

    sqrt_delta = np.sqrt(np.maximum(delta, 0.0))
    y_cardano = np.cbrt(-q / 2 + sqrt_delta) + np.cbrt(-q / 2 - sqrt_delta)

    p_safe = np.where(np.abs(p) < 1e-15, -1e-15, p)
    arg = np.clip(3 * q / (2 * p_safe) * np.sqrt(-3 / p_safe), -1, 1)
    base = np.arccos(arg) / 3
    y0 = 2 * np.sqrt(-p_safe / 3) * np.cos(base)
    y1 = 2 * np.sqrt(-p_safe / 3) * np.cos(base - 2 * np.pi / 3)
    y2 = 2 * np.sqrt(-p_safe / 3) * np.cos(base - 4 * np.pi / 3)
    y_trig = np.maximum(np.maximum(y0, y1), y2)

    y = np.where(delta >= 0, y_cardano, y_trig)
    x = y - b_arr / (3 * a_arr)

    result = np.where(valid, x, out)
    if prefer_positive:
        result = np.where(result < 0, np.inf, result)

    return float(result.flat[0]) if scalar else result
