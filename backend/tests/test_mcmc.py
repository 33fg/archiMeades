"""WO-34: Tests for NumPyro MCMC integration."""

import pytest

# Skip all tests if JAX/NumPyro not available
jax_available = False
try:
    import jax
    import numpyro
    jax_available = True
except ImportError:
    pass

pytestmark = pytest.mark.skipif(not jax_available, reason="JAX and NumPyro required")


class TestNumPyroMCMC:
    """AC-MCC-001: NumPyro HMC-NUTS sampling."""

    def test_run_mcmc_lcdm_synthetic(self) -> None:
        """AC-MCC-001.1: Execute HMC-NUTS for LCDM against synthetic dataset."""
        from app.mcmc.sampler import run_numpyro_mcmc

        result = run_numpyro_mcmc(
            theory_id="lcdm",
            dataset_id="synthetic",
            prior_spec={
                "omega_m": {"type": "uniform", "low": 0.2, "high": 0.5},
                "h0": {"type": "uniform", "low": 65, "high": 75},
            },
            num_samples=50,
            num_warmup=30,
            num_chains=1,
        )
        assert "posterior_samples" in result
        assert "omega_m" in result["posterior_samples"]
        assert "h0" in result["posterior_samples"]
        omega_m = result["posterior_samples"]["omega_m"]
        h0 = result["posterior_samples"]["h0"]
        assert len(omega_m) == 50
        assert len(h0) == 50
        flat_om = omega_m if isinstance(omega_m[0], (int, float)) else [x for row in omega_m for x in row]
        flat_h0 = h0 if isinstance(h0[0], (int, float)) else [x for row in h0 for x in row]
        assert all(0.2 <= x <= 0.5 for x in flat_om)
        assert all(65 <= x <= 75 for x in flat_h0)

    def test_diagnostics_returned(self) -> None:
        """WO-35: Diagnostics (rhat, ess, divergences) returned when arviz available."""
        from app.mcmc.sampler import run_numpyro_mcmc

        result = run_numpyro_mcmc(
            theory_id="lcdm",
            dataset_id="synthetic",
            prior_spec={
                "omega_m": {"type": "uniform", "low": 0.28, "high": 0.35},
                "h0": {"type": "uniform", "low": 68, "high": 72},
            },
            num_samples=40,
            num_warmup=20,
            num_chains=2,  # R-hat requires >= 2 chains
        )
        assert "diagnostics" in result
        diag = result["diagnostics"]
        assert "rhat" in diag
        assert "ess_bulk" in diag
        assert "n_divergences" in diag
        # With 2 chains, should have rhat if arviz installed
        try:
            import arviz
            arviz  # use to trigger ImportError if not present
            assert "omega_m" in diag.get("rhat", {}) or "h0" in diag.get("rhat", {})
        except ImportError:
            pass


# Emcee tests - skip if emcee not available
emcee_available = False
try:
    import emcee  # noqa: F401
    emcee_available = True
except ImportError:
    pass


@pytest.mark.skipif(not emcee_available, reason="emcee not installed")
class TestEmceeMCMC:
    """Emcee gradient-free sampler integration."""

    def test_run_emcee_lcdm_synthetic(self) -> None:
        """Emcee produces valid posterior for LCDM vs synthetic."""
        from app.mcmc.emcee_sampler import run_emcee_mcmc

        result = run_emcee_mcmc(
            theory_id="lcdm",
            dataset_id="synthetic",
            prior_spec={
                "omega_m": {"type": "uniform", "low": 0.2, "high": 0.5},
                "h0": {"type": "uniform", "low": 65, "high": 75},
            },
            num_samples=50,
            num_warmup=20,
            num_chains=2,
        )
        assert "posterior_samples" in result
        assert "omega_m" in result["posterior_samples"]
        assert "h0" in result["posterior_samples"]
        n = len(result["posterior_samples"]["omega_m"])
        assert n > 0
        assert all(0.2 <= x <= 0.5 for x in result["posterior_samples"]["omega_m"])
        assert all(65 <= x <= 75 for x in result["posterior_samples"]["h0"])

    def test_run_mcmc_dispatcher_emcee(self) -> None:
        """run_mcmc(sampler='emcee') routes to Emcee."""
        from app.mcmc.sampler import run_mcmc

        result = run_mcmc(
            theory_id="lcdm",
            dataset_id="synthetic",
            prior_spec={
                "omega_m": {"type": "uniform", "low": 0.28, "high": 0.35},
                "h0": {"type": "uniform", "low": 68, "high": 72},
            },
            num_samples=30,
            num_warmup=15,
            num_chains=2,
            sampler="emcee",
        )
        assert "posterior_samples" in result
        assert "param_names" in result
        assert "omega_m" in result["posterior_samples"]
