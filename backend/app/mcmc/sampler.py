"""WO-34: NumPyro HMC-NUTS sampler execution.
Unified run_mcmc dispatches to numpyro or emcee based on sampler param.
"""

from __future__ import annotations

from typing import Any

from app.datasets import load_dataset
from app.mcmc.diagnostics import compute_convergence_diagnostics
from app.mcmc.model import build_sn_model


def run_mcmc(
    theory_id: str,
    dataset_id: str,
    prior_spec: dict[str, dict[str, Any]],
    *,
    sampler: str = "numpyro",
    num_samples: int = 1000,
    num_warmup: int = 500,
    num_chains: int = 1,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run MCMC with NumPyro or Emcee. Dispatches based on sampler param."""
    if sampler == "emcee":
        from app.mcmc.emcee_sampler import run_emcee_mcmc

        return run_emcee_mcmc(
            theory_id=theory_id,
            dataset_id=dataset_id,
            prior_spec=prior_spec,
            num_samples=num_samples,
            num_warmup=num_warmup,
            num_chains=num_chains,
            **kwargs,
        )
    return run_numpyro_mcmc(
        theory_id=theory_id,
        dataset_id=dataset_id,
        prior_spec=prior_spec,
        num_samples=num_samples,
        num_warmup=num_warmup,
        num_chains=num_chains,
        **kwargs,
    )


def run_numpyro_mcmc(
    theory_id: str,
    dataset_id: str,
    prior_spec: dict[str, dict[str, Any]],
    *,
    num_samples: int = 1000,
    num_warmup: int = 500,
    num_chains: int = 1,
    chain_method: str = "sequential",
) -> dict[str, Any]:
    """Run NumPyro HMC-NUTS sampling.

    AC-MCC-001.1: Execute NumPyro HMC-NUTS on JAX backend.
    AC-MCC-001.3: Inf likelihood rejected without terminating chain.

    Args:
        theory_id: lcdm or g4v
        dataset_id: synthetic, pantheon
        prior_spec: Prior specification per parameter
        num_samples: Target samples per chain
        num_warmup: Warmup steps per chain
        num_chains: Number of chains
        chain_method: sequential, parallel, or vectorized

    Returns:
        Dict with posterior_samples, summary (rhat, etc.)
    """
    import jax
    from numpyro.infer import MCMC, NUTS

    dataset = load_dataset(dataset_id)
    param_names, model = build_sn_model(dataset, theory_id, prior_spec)

    kernel = NUTS(model)
    mcmc = MCMC(kernel, num_warmup=num_warmup, num_samples=num_samples, num_chains=num_chains)
    rng_key = jax.random.PRNGKey(0)
    mcmc.run(rng_key)

    samples = mcmc.get_samples()
    posterior = {k: v.tolist() for k, v in samples.items()}

    # WO-35: Convergence diagnostics (R-hat, ESS, divergences)
    diagnostics = compute_convergence_diagnostics(mcmc)

    return {
        "posterior_samples": posterior,
        "param_names": param_names,
        "num_samples": num_samples,
        "num_warmup": num_warmup,
        "num_chains": num_chains,
        "diagnostics": diagnostics,
    }
