"""WO-55: Accuracy enhancement and verification — Kahan summation, Richardson extrapolation.

REQ-NM-003: AC-NM-003.1 Kahan, AC-NM-003.2 Richardson/convergence.
"""

from __future__ import annotations

import numpy as np


def kahan_sum(arr: np.ndarray, axis: int | None = None) -> np.ndarray | float:
    """AC-NM-003.1: Kahan compensated summation to reduce floating-point error.

    Returns sum with O(ε) instead of O(N·ε) error for N terms.
    """
    arr = np.asarray(arr, dtype=np.float64)
    if axis is None:
        total = 0.0
        carry = 0.0
        for x in arr.flat:
            y = x - carry
            t = total + y
            carry = (t - total) - y
            total = t
        return total
    return np.apply_along_axis(kahan_sum, axis, arr)


def richardson_extrapolate(
    values: list[float],
    h_ratios: list[float] | None = None,
    order: int = 2,
) -> tuple[float, float]:
    """AC-NM-003.2: Richardson extrapolation for discretization error estimation.

    Given f(h₁), f(h₂), ... with h_i = h₀ / r^i, extrapolates to h→0 limit.
    Returns (extrapolated_value, estimated_error).
    """
    if len(values) < 2:
        return values[0] if values else (0.0, 0.0)
    r = 2.0 if h_ratios is None else (h_ratios[1] / h_ratios[0] if len(h_ratios) > 1 else 2.0)
    v = np.array(values, dtype=np.float64)
    # R[0,j] = f(h_j); R[i,j] = (r^order * R[i-1,j+1] - R[i-1,j]) / (r^order - 1)
    n = len(v)
    R = np.zeros((n, n))
    R[0, :n] = v
    for i in range(1, n):
        for j in range(n - i):
            fac = r ** (order * i)
            R[i, j] = (fac * R[i - 1, j + 1] - R[i - 1, j]) / (fac - 1)
    best = R[n - 1, 0]
    err = abs(best - R[n - 2, 0]) if n > 1 else 0.0
    return float(best), float(err)
