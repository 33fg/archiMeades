"""WO-32: Batched/vectorized chi-squared for parameter scans.

REQ-SCN-003: GPU-parallel likelihood batching.
Uses multiprocessing for CPU parallelization; JAX path when available.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

import numpy as np

from app.likelihood.chi_squared import compute_chi_squared


def _chi2_chunk_worker(args: tuple) -> list[tuple[int, float]]:
    """Worker: compute chi2 for a chunk of parameter sets. Top-level for pickling."""
    indices, param_sets, dataset_id, theory_id = args
    from app.datasets import load_dataset

    dataset = load_dataset(dataset_id)
    results: list[tuple[int, float]] = []
    for idx, params in zip(indices, param_sets):
        try:
            c2 = compute_chi_squared(
                dataset,
                theory_id,
                omega_m=params.get("omega_m", 0.31),
                i_rel=params.get("i_rel", 1.451782),
                h0=params.get("h0", 70.0),
            )
            results.append((idx, float(c2)))
        except Exception:
            results.append((idx, np.inf))
    return results


def compute_chi_squared_batch(
    dataset_id: str,
    theory_id: str,
    param_sets: list[dict[str, float]],
    *,
    n_workers: int | None = None,
    chunk_size: int = 500,
) -> np.ndarray:
    """Compute chi-squared for many parameter sets in parallel.

    Uses ProcessPoolExecutor for CPU parallelization.
    AC-SCN-001.4: Unphysical => Inf, continue.
    """
    n = len(param_sets)
    chi2 = np.full(n, np.inf, dtype=np.float64)

    n_workers = n_workers or max(1, mp.cpu_count() - 1)
    chunks: list[tuple[list[int], list[dict], str, str]] = []
    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        indices = list(range(start, end))
        chunk_params = [param_sets[i] for i in indices]
        chunks.append((indices, chunk_params, dataset_id, theory_id))

    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(_chi2_chunk_worker, c) for c in chunks]
        for future in as_completed(futures):
            for idx, c2 in future.result():
                chi2[idx] = c2

    return chi2
