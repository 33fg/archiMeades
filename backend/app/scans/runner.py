"""WO-31: Scan runner - evaluate likelihood at each grid point.

AC-SCN-001.1/001.2/001.3: 1D, 2D, 3D grids.
AC-SCN-001.4: Unphysical => Inf, continue without exception.
WO-32: Uses batched parallel evaluation when grid is large.
"""

from __future__ import annotations

import numpy as np

from app.datasets import load_dataset
from app.grid import generate_grid
from app.likelihood import compute_chi_squared
from app.likelihood.chi_squared_batch import compute_chi_squared_batch

_PARALLEL_THRESHOLD = 64  # Use batch/parallel when grid has >= this many points


def run_scan(
    theory_id: str,
    dataset_id: str,
    axes_config: list[dict],
    fixed_params: dict | None = None,
) -> tuple[np.ndarray, list[int]]:
    """Run parameter scan, return chi2 array and shape.

    Args:
        theory_id: Theory identifier
        dataset_id: Dataset name (synthetic, pantheon)
        axes_config: List of {name, min, max, n, scale} per axis
        fixed_params: Params not being scanned (omega_m, h0, i_rel)

    Returns:
        (chi2_values, shape) - chi2 as flat array, shape for reshape
    """
    fixed = fixed_params or {}

    axes = [
        (
            a["name"],
            float(a["min"]),
            float(a["max"]),
            int(a["n"]),
            a.get("scale", "linear"),
        )
        for a in axes_config
    ]

    param_names, flat_arrays, shape = generate_grid(axes)
    n_points = len(flat_arrays[0]) if flat_arrays else 0

    param_sets: list[dict[str, float]] = []
    for i in range(n_points):
        params = dict(fixed)
        for j, name in enumerate(param_names):
            params[name] = float(flat_arrays[j][i])
        param_sets.append(params)

    if n_points >= _PARALLEL_THRESHOLD:
        chi2 = compute_chi_squared_batch(
            dataset_id, theory_id, param_sets,
            chunk_size=min(500, max(1, n_points // 8)),
        )
    else:
        dataset = load_dataset(dataset_id)
        chi2 = np.full(n_points, np.inf, dtype=np.float64)
        for i, params in enumerate(param_sets):
            try:
                c2 = compute_chi_squared(
                    dataset,
                    theory_id,
                    omega_m=params.get("omega_m", 0.31),
                    i_rel=params.get("i_rel", 1.451782),
                    h0=params.get("h0", 70.0),
                )
                chi2[i] = c2
            except Exception:
                chi2[i] = np.inf  # AC-SCN-001.4: continue

    return chi2, [int(x) for x in shape]
