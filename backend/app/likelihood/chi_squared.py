"""WO-30: Chi-squared computation χ² = Δμᵀ C⁻¹ Δμ.

REQ-LIK-001: Full covariance chi-squared.
AC-LIK-001.1: χ² = Δμᵀ C⁻¹ Δμ where Δμ = μ_obs - μ_theory.
AC-LIK-001.3: NaN/Inf in theory prediction => return Inf.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from app.datasets.observational_dataset import ObservationalDataset
from app.observables import distance_modulus, luminosity_distance_theory
from app.observables.bao import NotSupportedError


def _get_theory_predictions(
    dataset: ObservationalDataset,
    theory_id: str,
    omega_m: float = 0.31,
    i_rel: float = 1.451782,
    h0: float = 70.0,
) -> np.ndarray:
    """Compute theory distance moduli at dataset redshifts."""
    if dataset.observable_type != "distance_modulus":
        raise ValueError(
            f"Observable type '{dataset.observable_type}' not supported; "
            "expected 'distance_modulus'"
        )
    z = dataset.redshift
    d_l = luminosity_distance_theory(z, theory_id, omega_m=omega_m, i_rel=i_rel, h0=h0)
    mu_theory = distance_modulus(d_l)
    return np.asarray(mu_theory, dtype=np.float64).flatten()


def compute_chi_squared(
    dataset: ObservationalDataset,
    theory_id: str,
    *,
    omega_m: float = 0.31,
    i_rel: float = 1.451782,
    h0: float = 70.0,
    **_: Any,
) -> float:
    """Compute χ² = Δμᵀ C⁻¹ Δμ for theory vs dataset.

    AC-LIK-001.1: χ² = Δμᵀ C⁻¹ Δμ where Δμ = μ_obs - μ_theory, C = total covariance.
    AC-LIK-001.3: Returns Inf when theory prediction contains NaN/Inf.

    Args:
        dataset: ObservationalDataset with distance_modulus observable
        theory_id: Theory identifier (lcdm, g4v)
        omega_m, i_rel, h0: Theory parameters

    Returns:
        Chi-squared value, or Inf for unphysical parameters.
    """
    try:
        mu_theory = _get_theory_predictions(
            dataset, theory_id, omega_m=omega_m, i_rel=i_rel, h0=h0
        )
    except (NotSupportedError, ValueError):
        return np.inf

    if not np.all(np.isfinite(mu_theory)):
        return np.inf

    mu_obs = np.asarray(dataset.observable, dtype=np.float64).flatten()
    delta_mu = mu_obs - mu_theory

    if len(delta_mu) != dataset.num_points:
        return np.inf

    cov_inv = dataset.cov_inv
    # χ² = Δμᵀ C⁻¹ Δμ
    chi2 = float(np.dot(delta_mu, np.dot(cov_inv, delta_mu)))
    return np.inf if not np.isfinite(chi2) or chi2 < 0 else chi2
