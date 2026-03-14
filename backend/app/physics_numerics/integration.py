"""WO-51/WO-53: Numerical integration — adaptive quadrature, Romberg.

WO-51: Foundation.
WO-53: Integration Methods — Romberg (Richardson extrapolation on trapezoidal rule).
"""

from __future__ import annotations

from typing import Callable, Union

import numpy as np


def romberg(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-8,
    max_steps: int = 20,
) -> tuple[float, float]:
    """WO-53: Romberg integration — Richardson extrapolation on trapezoidal rule.

    R[k,m] = (4^m R[k,m-1] - R[k-1,m-1]) / (4^m - 1)
    Converges O(h^{2m}) with step refinement.

    Args:
        f: Integrand (scalar function)
        a, b: Integration limits
        tol: Relative tolerance for convergence
        max_steps: Maximum Romberg steps

    Returns:
        (integral, estimated_error)
    """
    # R[0,0] = (b-a)/2 * (f(a) + f(b))
    h = b - a
    r = [[0.5 * h * (f(a) + f(b))]]
    best = r[0][0]

    for k in range(1, max_steps):
        h *= 0.5
        # Trapezoidal with 2^k subintervals
        x = np.linspace(a + h, b - h, 2 ** (k - 1))
        trap = h * (f(a) + 2 * np.sum(np.vectorize(f)(x)) + f(b))
        r.append([trap])

        # Richardson extrapolation
        for m in range(1, k + 1):
            fac = 4**m
            val = (fac * r[k][m - 1] - r[k - 1][m - 1]) / (fac - 1)
            r[k].append(val)

        best = r[k][k]
        err = abs(best - r[k - 1][k - 1]) if k > 0 else abs(best)
        if err < tol * (abs(best) + 1e-30):
            break

    return float(best), float(err)


def adaptive_quadrature(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-8,
) -> float:
    """Wrapper using Romberg for adaptive quadrature. Compatible with scipy.quad usage."""
    result, _ = romberg(f, a, b, tol=tol)
    return result
