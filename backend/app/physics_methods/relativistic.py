"""WO-52: Relativistic extensions — post-Newtonian corrections, regime detection.

REQ-PM-003: Relativistic Extensions
AC-PM-003.1: Post-Newtonian corrections when v ~ c.
"""

from __future__ import annotations

import numpy as np


def post_newtonian_1pn_acceleration(
    m: float,
    r: np.ndarray,
    v: np.ndarray,
    G: float = 6.67430e-11,
    c: float = 2.99792458e8,
) -> np.ndarray:
    """AC-PM-003.1: 1PN correction to Newtonian acceleration for a test particle.

    Simplified 1PN: a_1PN ≈ a_N * (1 + (v/c)² + 2 G M / (r c²) + ...)
    Returns additional 1PN term for use as: a_total = a_N + a_1PN

    Args:
        m: Central mass (kg)
        r: Position vector from center (m)
        v: Velocity vector (m/s)
        G, c: Constants

    Returns:
        1PN correction to acceleration (m/s²), shape (3,)
    """
    r = np.asarray(r, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    r_mag = np.linalg.norm(r)
    if r_mag < 1e-30:
        return np.zeros(3)
    v_sq = np.dot(v, v)
    beta_sq = v_sq / (c * c)
    phi = G * m / r_mag  # Newtonian potential
    # 1PN correction factor (simplified)
    factor = beta_sq + 2 * phi / (c * c)
    a_N_mag = G * m / (r_mag * r_mag)
    r_hat = r / r_mag
    a_1PN = -a_N_mag * r_hat * factor * 0.5  # order-of-magnitude 1PN term
    return a_1PN


def regime_beta(v: np.ndarray, c: float = 2.99792458e8) -> str:
    """Physics regime from velocity: Newtonian, post-Newtonian, or relativistic."""
    v_mag = np.linalg.norm(np.asarray(v))
    beta = v_mag / c
    if beta < 0.01:
        return "newtonian"
    if beta < 0.3:
        return "post_newtonian"
    return "relativistic"
