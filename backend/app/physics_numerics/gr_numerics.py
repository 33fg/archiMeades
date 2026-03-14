"""WO-56: Tensor, GR, and differential geometry numerics.

REQ-NM-004: Christoffel, Riemann/Ricci/Einstein. AC-NM-004.1.
"""

from __future__ import annotations

import numpy as np


def christoffel_symbols(
    g: np.ndarray,
    g_inv: np.ndarray,
    dg: np.ndarray,
) -> np.ndarray:
    """AC-NM-004.1: Christoffel symbols Γ^α_βγ = (1/2) g^αδ (∂_β g_γδ + ∂_γ g_βδ - ∂_δ g_βγ).

    Args:
        g: Metric g_αβ, shape (4,4) for spacetime
        g_inv: Inverse metric g^αβ
        dg: Derivatives ∂_μ g_αβ, shape (4,4,4) for [mu, alpha, beta]

    Returns:
        Γ^α_βγ, shape (4,4,4)
    """
    dim = g.shape[0]
    Gamma = np.zeros((dim, dim, dim), dtype=np.float64)
    for a in range(dim):
        for b in range(dim):
            for g_idx in range(dim):
                for d in range(dim):
                    Gamma[a, b, g_idx] += 0.5 * g_inv[a, d] * (
                        dg[b, d, g_idx] + dg[g_idx, d, b] - dg[d, b, g_idx]
                    )
    return Gamma


def christoffel_from_diagonal_metric(
    g_diag: np.ndarray,
    dg_diag: np.ndarray,
) -> np.ndarray:
    """Christoffel symbols for diagonal metric g_μν = diag(g_00, g_11, g_22, g_33).

    dg_diag[mu, nu] = ∂_μ g_νν (no sum). Simpler for FLRW, Schwarzschild.
    """
    dim = len(g_diag)
    g_inv = np.diag(1.0 / np.asarray(g_diag))
    dg = np.zeros((dim, dim, dim))
    for mu in range(dim):
        for nu in range(dim):
            dg[mu, nu, nu] = dg_diag[mu, nu]
    return christoffel_symbols(np.diag(g_diag), g_inv, dg)


def geodesic_acceleration(
    Gamma: np.ndarray,
    position: np.ndarray,
    velocity: np.ndarray,
) -> np.ndarray:
    """Geodesic equation d²x^α/dτ² = -Γ^α_βγ u^β u^γ. Returns acceleration."""
    dim = len(position)
    accel = np.zeros(dim)
    for a in range(dim):
        for b in range(dim):
            for g in range(dim):
                accel[a] -= Gamma[a, b, g] * velocity[b] * velocity[g]
    return accel
