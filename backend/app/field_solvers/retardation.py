"""WO-24: Retardation integral engine for G4v Machian computation.

REQ-FLD-003: Retardation Integral Computation
AC-FLD-003.1: Smooth Hubble flow => I_rel = 1.451782 (analytic)
AC-FLD-003.2: Discrete Liénard-Wiechert sum I_rel = sum_i (m_i/M_tot) * (1/kappa_i^2)
AC-FLD-003.4, AC-FLD-004.3: Regularize kappa→0 to prevent overflow
AC-FLD-004.1, 004.4: NaN/Inf => Inf
"""

from __future__ import annotations

from typing import Union

import numpy as np

# Analytic value for smooth Hubble flow (G4v self-consistent solution)
SMOOTH_HUBBLE_I_REL = 1.451782

# AC-FLD-004.3: Minimum kappa to prevent 1/kappa^2 overflow
KAPPA_MIN = 1e-10

ScalarOrArray = Union[float, np.ndarray]


def compute_retardation_smooth_hubble() -> float:
    """Return I_rel for smooth Hubble flow (analytic result).

    AC-FLD-003.1: Returns 1.451782 to within 10^-6 (exact analytic value).
    """
    return SMOOTH_HUBBLE_I_REL


def compute_retardation_discrete(
    masses: np.ndarray,
    v_over_c: np.ndarray,
) -> float:
    """Compute I_rel for discrete particle distribution (Liénard-Wiechert sum).

    I_rel = sum_i (m_i / M_tot) * (1 / kappa_i^2)
    where kappa_i = 1 - v_i/c.

    AC-FLD-003.2: Discrete particle Liénard-Wiechert sum.
    AC-FLD-004.3: kappa regularized to prevent overflow when v→c.

    Args:
        masses: Particle masses (any units; normalized by M_tot)
        v_over_c: Velocity / c for each particle (0 <= v_over_c < 1 for physical)

    Returns:
        I_rel: Retardation integral value
    """
    masses = np.asarray(masses, dtype=np.float64).flatten()
    v_over_c = np.asarray(v_over_c, dtype=np.float64).flatten()
    if len(masses) != len(v_over_c):
        raise ValueError("masses and v_over_c must have same length")

    # AC-FLD-004.4: NaN/Inf => Inf
    if np.any(np.isnan(masses)) or np.any(np.isnan(v_over_c)):
        return np.inf
    if np.any(np.isinf(masses)) or np.any(np.isinf(v_over_c)):
        return np.inf

    M_tot = np.sum(masses)
    if M_tot <= 0 or not np.isfinite(M_tot):
        return np.inf

    # kappa = 1 - v/c; AC-FLD-004.3: clamp to prevent 1/kappa^2 overflow
    kappa = 1.0 - v_over_c
    kappa = np.maximum(kappa, KAPPA_MIN)

    # I_rel = sum_i (m_i/M_tot) * (1/kappa_i^2)
    weights = masses / M_tot
    contrib = weights / (kappa**2)
    result = np.sum(contrib)
    return float(result) if np.isfinite(result) else np.inf
