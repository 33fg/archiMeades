#!/usr/bin/env python3
"""Quick script to test MCMC endpoint and NumPyro availability."""
import sys
sys.path.insert(0, ".")

def test_numpyro_import():
    try:
        import numpyro
        import jax
        print("OK: numpyro and jax imported")
        return True
    except ImportError as e:
        print(f"FAIL: {e}")
        return False

def test_run_mcmc():
    try:
        from app.mcmc.sampler import run_numpyro_mcmc
        result = run_numpyro_mcmc(
            theory_id="lcdm",
            dataset_id="synthetic",
            prior_spec={
                "omega_m": {"type": "uniform", "low": 0.28, "high": 0.35},
                "h0": {"type": "uniform", "low": 68, "high": 72},
            },
            num_samples=30,
            num_warmup=15,
            num_chains=1,
        )
        assert "posterior_samples" in result
        assert "omega_m" in result["posterior_samples"]
        print("OK: run_numpyro_mcmc completed")
        print(f"  omega_m samples: {len(result['posterior_samples']['omega_m'])}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    ok1 = test_numpyro_import()
    ok2 = test_run_mcmc() if ok1 else False
    sys.exit(0 if (ok1 and ok2) else 1)
