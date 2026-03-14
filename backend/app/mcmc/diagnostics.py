"""WO-35: Multi-chain convergence diagnostics - R-hat, ESS, divergences."""

from __future__ import annotations

from typing import Any


def compute_convergence_diagnostics(mcmc: Any) -> dict[str, Any]:
    """Compute R-hat, ESS, and divergence metrics from NumPyro MCMC.

    WO-35: Gelman-Rubin R-hat, effective sample size (ESS), divergence reporting.
    AC-MCC-001.2: R-hat < 1.1 indicates convergence.

    Args:
        mcmc: NumPyro MCMC object after run()

    Returns:
        Dict with rhat, ess_bulk, ess_tail, divergences, n_divergences,
        divergence_rate, warning (if >1% divergences or R-hat > 1.1)
    """
    result: dict[str, Any] = {
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

        idata = az.from_numpyro(mcmc)
        num_chains = idata.posterior.dims.get("chain", 1)

        # R-hat requires ≥2 chains; ESS works for any chain count
        if num_chains >= 2:
            rhat = az.rhat(idata)
            for vn in rhat.data_vars:
                val = float(rhat[vn].values)
                result["rhat"][vn] = val

        ess_bulk = az.ess(idata, method="bulk")
        ess_tail = az.ess(idata, method="tail")
        for vn in (ess_bulk.data_vars or []):
            result["ess_bulk"][vn] = int(ess_bulk[vn].values)
        for vn in (ess_tail.data_vars or []):
            result["ess_tail"][vn] = int(ess_tail[vn].values)

        # Divergences from NumPyro extra fields
        try:
            extra = mcmc.get_extra_fields()
            if "diverging" in extra:
                div_arr = extra["diverging"]
                n_div = int(div_arr.sum())
                total = div_arr.size
                result["n_divergences"] = n_div
                result["divergence_rate"] = n_div / total if total > 0 else 0.0
                if n_div > 0:
                    result["divergences"] = div_arr.tolist()
                # Warning if >1% divergences
                if result["divergence_rate"] > 0.01:
                    result["warning"] = (
                        f"High divergence rate: {result['divergence_rate']:.1%} "
                        f"({n_div}/{total}). Consider reducing step size or reparameterizing."
                    )
        except Exception:
            pass

        # Warning if R-hat > 1.1 for any param
        if result["rhat"]:
            max_rhat = max(result["rhat"].values()) if result["rhat"] else 1.0
            if max_rhat > 1.1 and not result["warning"]:
                result["warning"] = (
                    f"R-hat > 1.1 for some parameters (max={max_rhat:.3f}). "
                    "Chains may not have converged. Consider extending the run."
                )

    except ImportError:
        pass  # ArviZ optional

    return result
