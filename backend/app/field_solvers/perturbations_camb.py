"""WO-25: CAMB perturbation solver for Lambda-CDM P(k,z).

Requires: pip install camb
"""

from __future__ import annotations

import numpy as np

import camb

from app.field_solvers.perturbations import PowerSpectrumResult


class CambPerturbationSolver:
    """Lambda-CDM power spectrum via CAMB."""

    def compute_power_spectrum(
        self,
        omega_m: float,
        omega_b: float = 0.049,
        h: float = 0.67,
        n_s: float = 0.965,
        sigma8: float | None = None,
        k_min: float = 1e-4,
        k_max: float = 10.0,
        z_max: float = 10.0,
    ) -> PowerSpectrumResult:
        """AC-FLD-006.1: P(k,z) via CAMB for 1e-4 < k < 10 Mpc^-1, 0 < z < 10."""
        pars = camb.CAMBparams()
        ombh2 = omega_b * h**2
        omch2 = (omega_m - omega_b) * h**2
        pars.set_cosmology(H0=h * 100, ombh2=ombh2, omch2=omch2)
        pars.InitPower.set_params(ns=n_s)
        z_vals = np.array([0.0, 0.5, 1.0, min(z_max, 2.0)])
        pars.set_matter_power(redshifts=z_vals.tolist(), kmax=min(k_max, 2.0))
        if sigma8 is not None:
            pars.set_sigma8(sigma8)

        results = camb.get_results(pars)
        PK = results.get_matter_power_interpolator(nonlinear=False, hubble_units=False, k_hunit=False)

        k = np.logspace(np.log10(k_min), np.log10(k_max), 64)
        Pkz = np.array([[PK.P(z, ki) for ki in k] for z in z_vals]).T  # shape (nk, nz)

        return PowerSpectrumResult(k=k, z=z_vals, Pkz=Pkz, theory_id="lcdm")
