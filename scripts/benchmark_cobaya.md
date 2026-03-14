# Cobaya Benchmarking Guide

Use [Cobaya](https://cobaya.readthedocs.io/) (or CosmoMC) to validate our ΛCDM likelihood and MCMC pipeline against the standard cosmology toolchain.

## Prerequisites

```bash
pip install cobaya camb
```

Or with conda:
```bash
conda install -c conda-forge cobaya camb
```

## Quick ΛCDM + Pantheon Comparison

1. **Run our platform** (NumPyro or Emcee):
   - Theory: Lambda-CDM
   - Dataset: Pantheon
   - Priors: omega_m ∈ [0.2, 0.5], h0 ∈ [65, 75]
   - Note best-fit χ² and posterior means

2. **Run Cobaya** with equivalent setup:

```yaml
# cobaya_pantheon.yaml
theory:
  camb: {}

params:
  omega_cdm: {min: 0.05, max: 0.5}
  H0: {min: 60, max: 80}

likelihood:
  Pantheon: {}

sampler:
  mcmc:
    Rminus1_stop: 0.01
    max_tries: 1000
```

```bash
cobaya-run cobaya_pantheon.yaml
```

3. **Compare**:
   - Best-fit χ² should agree within ~1 (numerical differences)
   - Posterior means (omega_m, H0) should overlap within 1σ

## Mapping Our Params to Cobaya

| Our param | Cobaya param |
|-----------|--------------|
| omega_m   | omega_cdm + omega_b (or Omegam) |
| h0        | H0 |

For flat ΛCDM, omega_m = omega_cdm + omega_b. Cobaya's Pantheon likelihood uses the full CMB+SN setup; for SN-only comparison, use the Pantheon likelihood with fixed omega_b.

## Full Planck + Pantheon

For a full comparison including CMB:

```yaml
theory:
  camb: {}

params:
  omega_cdm: {min: 0.05, max: 0.5}
  omega_b: 0.022  # or sample
  H0: {min: 60, max: 80}

likelihood:
  planck_2018_highl_plik.TTTEEE: {}
  planck_2018_lowl.EE: {}
  Pantheon: {}

sampler:
  mcmc:
    Rminus1_stop: 0.01
```

## Output

Cobaya writes to `chains/` and `output/`. Use GetDist to plot:

```python
from getdist import MCSamples
samples = MCSamples(root="chains/run_name")
samples.plot_2d(['omega_cdm', 'H0'])
```

Our platform exports GetDist-compatible `chains.txt` and `paramnames.txt` from the MCMC API for direct comparison.
