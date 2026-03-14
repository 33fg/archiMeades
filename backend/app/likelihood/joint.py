"""WO-30: Joint likelihood across multiple datasets.

REQ-LIK-004: Multi-dataset joint likelihood.
AC-LIK-004.1: Joint χ² = sum of individual χ².
AC-LIK-004.3: Inf from any dataset => return Inf without evaluating rest.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from app.datasets.observational_dataset import ObservationalDataset
from app.likelihood.chi_squared import compute_chi_squared


def compute_joint_chi_squared(
    datasets: list[ObservationalDataset],
    theory_id: str,
    *,
    omega_m: float = 0.31,
    i_rel: float = 1.451782,
    h0: float = 70.0,
    **kwargs: Any,
) -> float:
    """Compute joint χ² = Σ χ²_i for multiple datasets.

    AC-LIK-004.1: Returns sum of individual chi-squared values.
    AC-LIK-004.3: Stops and returns Inf if any dataset yields Inf.
    """
    total = 0.0
    for ds in datasets:
        chi2 = compute_chi_squared(
            ds, theory_id, omega_m=omega_m, i_rel=i_rel, h0=h0, **kwargs
        )
        if not np.isfinite(chi2):
            return np.inf
        total += chi2
    return total
