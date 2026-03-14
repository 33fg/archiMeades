"""WO-34: NumPyro model construction from theory + likelihood."""

from __future__ import annotations

from typing import Any

import numpy as np

from app.datasets.observational_dataset import ObservationalDataset


def build_sn_model(
    dataset: ObservationalDataset,
    theory_id: str,
    prior_spec: dict[str, dict[str, Any]],
) -> tuple[list[str], Any]:
    """Build NumPyro model for SNe distance modulus likelihood.

    Args:
        dataset: ObservationalDataset with distance_modulus observable
        theory_id: lcdm or g4v
        prior_spec: Dict of param -> {type, low, high} or {type, mean, std}
            type: uniform, normal, log_normal
            uniform: low, high
            normal: mean, std
            log_normal: mean, std (in log space)

    Returns:
        (param_names, model_fn) for numpyro.infer.MCMC
    """
    from app.observables.distance_jax import luminosity_distance_jax

    import jax.numpy as jnp
    import numpyro
    import numpyro.distributions as dist

    if dataset.observable_type != "distance_modulus":
        raise ValueError(
            f"Observable type '{dataset.observable_type}' not supported; "
            "expected 'distance_modulus'"
        )

    z = jnp.array(dataset.redshift, dtype=jnp.float32)
    mu_obs = jnp.array(dataset.observable, dtype=jnp.float32)
    cov_inv = jnp.array(dataset.cov_inv, dtype=jnp.float32)

    # Determine params from prior_spec (guard against None)
    prior_spec = prior_spec or {}
    param_names = sorted(prior_spec.keys())

    def model() -> None:
        params = {}
        for name in param_names:
            spec = prior_spec[name]
            t = spec.get("type", "uniform")
            if t == "uniform":
                low = float(spec["low"])
                high = float(spec["high"])
                params[name] = numpyro.sample(name, dist.Uniform(low, high))
            elif t == "normal":
                mean = float(spec.get("mean", spec.get("mu", 0)))
                std = float(spec.get("std", spec.get("sigma", 1)))
                params[name] = numpyro.sample(name, dist.Normal(mean, std))
            elif t == "log_normal":
                mean = float(spec.get("mean", spec.get("mu", 0)))
                std = float(spec.get("std", spec.get("sigma", 1)))
                params[name] = numpyro.sample(name, dist.LogNormal(mean, std))
            else:
                raise ValueError(f"Unknown prior type: {t}")

        omega_m = params.get("omega_m", 0.31)
        h0 = params.get("h0", 70.0)
        i_rel = params.get("i_rel", 1.451782)

        d_l = luminosity_distance_jax(z, omega_m, i_rel, h0, theory_id)
        mu_theory = 5.0 * jnp.log10(jnp.maximum(d_l, 1e-10)) + 25.0

        delta = mu_obs - mu_theory
        # χ² = Δμᵀ C⁻¹ Δμ; -0.5 * χ² is log-likelihood (Gaussian)
        chi2 = jnp.dot(delta, jnp.dot(cov_inv, delta))
        # AC-MCC-001.3: Inf likelihood => reject step (NumPyro handles via -inf log_prob)
        log_lik = jnp.where(jnp.isfinite(chi2), -0.5 * chi2, -jnp.inf)
        numpyro.factor("likelihood", log_lik)

    return param_names, model
