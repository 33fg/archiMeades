#!/usr/bin/env python3
"""Quick check that NumPyro is installed and MCMC can run."""
import sys
try:
    import numpyro
    import jax
    print("OK: numpyro and jax installed", file=sys.stderr)
except ImportError as e:
    print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)
# Quick MCMC run
from app.mcmc.sampler import run_numpyro_mcmc
r = run_numpyro_mcmc("lcdm", "synthetic", {"omega_m": {"type": "uniform", "low": 0.3, "high": 0.35}, "h0": {"type": "uniform", "low": 69, "high": 71}}, num_samples=20, num_warmup=10, num_chains=1)
print("OK: MCMC ran", len(r["posterior_samples"]["omega_m"]), "samples")
