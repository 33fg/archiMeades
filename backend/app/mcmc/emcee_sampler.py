"""Emcee sampler - gradient-free ensemble MCMC.

Alternative to NumPyro for non-differentiable likelihoods and cross-checks.
Uses same compute_chi_squared and prior_spec as NumPyro path.
"""

from __future__ import annotations

import numpy as np
from typing import Any

from app.datasets import load_dataset
from app.likelihood import compute_chi_squared


def _log_prior(params: np.ndarray, param_names: list[str], prior_spec: dict[str, dict[str, Any]]) -> float:
    """Log prior for parameters. Returns -np.inf if outside bounds."""
    log_p = 0.0
    for i, name in enumerate(param_names):
        spec = prior_spec.get(name, {})
        t = spec.get("type", "uniform")
        val = float(params[i])
        if t == "uniform":
            low = float(spec["low"])
            high = float(spec["high"])
            if val < low or val > high:
                return -np.inf
            log_p += -np.log(high - low)
        elif t == "normal":
            mean = float(spec.get("mean", spec.get("mu", 0)))
            std = float(spec.get("std", spec.get("sigma", 1)))
            if std <= 0:
                return -np.inf
            log_p += -0.5 * ((val - mean) / std) ** 2 - np.log(std * np.sqrt(2 * np.pi))
        elif t == "log_normal":
            mean = float(spec.get("mean", spec.get("mu", 0)))
            std = float(spec.get("std", spec.get("sigma", 1)))
            if val <= 0 or std <= 0:
                return -np.inf
            log_p += (
                -0.5 * ((np.log(val) - mean) / std) ** 2
                - np.log(val * std * np.sqrt(2 * np.pi))
            )
    return log_p


def run_emcee_mcmc(
    theory_id: str,
    dataset_id: str,
    prior_spec: dict[str, dict[str, Any]],
    *,
    num_samples: int = 1000,
    num_warmup: int = 500,
    num_chains: int = 2,
    nwalkers: int | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Run Emcee affine-invariant ensemble MCMC.

    Gradient-free; uses compute_chi_squared (not JAX). Good for cross-checks
    and non-differentiable likelihoods.

    Args:
        theory_id: lcdm or g4v
        dataset_id: synthetic, pantheon
        prior_spec: Prior specification per parameter
        num_samples: Target samples per chain (after warmup)
        num_warmup: Warmup/discard steps
        num_chains: Number of independent chains (run sequentially)
        nwalkers: Walkers per chain (default: 2*ndim)
        seed: Random seed

    Returns:
        Dict with posterior_samples, param_names, diagnostics (same format as NumPyro).
    """
    try:
        import emcee
    except ImportError as e:
        raise ImportError(
            "emcee is required for Emcee sampler. Install with: uv sync '.[emcee]'"
        ) from e

    dataset = load_dataset(dataset_id)
    if dataset.observable_type != "distance_modulus":
        raise ValueError(
            f"Observable type '{dataset.observable_type}' not supported; "
            "expected 'distance_modulus'"
        )

    prior_spec = prior_spec or {}
    param_names = sorted(prior_spec.keys())
    ndim = len(param_names)
    if ndim == 0:
        raise ValueError("prior_spec must define at least one parameter")

    nw = nwalkers or max(4, 2 * ndim)

    def log_prob(params: np.ndarray) -> float:
        lp = _log_prior(params, param_names, prior_spec)
        if not np.isfinite(lp):
            return -np.inf
        kwargs = dict(zip(param_names, params))
        chi2 = compute_chi_squared(dataset, theory_id, **kwargs)
        if not np.isfinite(chi2) or chi2 < 0:
            return -np.inf
        return lp - 0.5 * chi2

    # Initial positions from prior
    rng = np.random.default_rng(seed)
    p0_list = []
    for _ in range(nw):
        p = []
        for name in param_names:
            spec = prior_spec[name]
            t = spec.get("type", "uniform")
            if t == "uniform":
                low, high = float(spec["low"]), float(spec["high"])
                p.append(rng.uniform(low, high))
            elif t == "normal":
                mean, std = float(spec.get("mean", 0)), float(spec.get("std", 1))
                p.append(rng.normal(mean, std))
            else:
                low = prior_spec[name].get("low", 0.1)
                high = prior_spec[name].get("high", 1.0)
                p.append(rng.uniform(low, high))
        p0_list.append(p)
    p0 = np.array(p0_list)

    sampler = emcee.EnsembleSampler(nw, ndim, log_prob)
    sampler.random_state = np.random.RandomState(seed)

    # Warmup
    state = sampler.run_mcmc(p0, num_warmup, progress=False)
    sampler.reset()

    # Production run
    sampler.run_mcmc(state, num_samples, progress=False)

    # Shape: (nwalkers, nsteps, ndim) -> flatten to (nwalkers * nsteps, ndim)
    chain = sampler.get_chain()

    posterior = {}
    for j, name in enumerate(param_names):
        posterior[name] = chain[:, :, j].flatten().tolist()

    # Diagnostics via ArviZ (same format as NumPyro)
    diagnostics: dict[str, Any] = {
        "rhat": {},
        "ess_bulk": {},
        "ess_tail": {},
        "divergences": None,
        "n_divergences": 0,
        "divergence_rate": 0.0,
        "warning": None,
    }
    try:
        import arviz as az

        idata = az.from_emcee(sampler, var_names=param_names)
        if nw >= 2:
            rhat = az.rhat(idata)
            for vn in rhat.data_vars:
                val = float(rhat[vn].values)
                diagnostics["rhat"][vn] = val
        ess_bulk = az.ess(idata, method="bulk")
        ess_tail = az.ess(idata, method="tail")
        for vn in ess_bulk.data_vars:
            diagnostics["ess_bulk"][vn] = int(ess_bulk[vn].values)
        for vn in ess_tail.data_vars:
            diagnostics["ess_tail"][vn] = int(ess_tail[vn].values)
    except Exception:
        pass

    return {
        "posterior_samples": posterior,
        "param_names": param_names,
        "num_samples": num_samples,
        "num_warmup": num_warmup,
        "num_chains": nw,
        "diagnostics": diagnostics,
    }
