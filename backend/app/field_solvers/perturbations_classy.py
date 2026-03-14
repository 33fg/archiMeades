"""WO-25: CLASS perturbation solver for Lambda-CDM P(k,z).

Requires: pip install classy
"""

from __future__ import annotations

import numpy as np

from app.field_solvers.perturbations import PowerSpectrumResult


class ClassyPerturbationSolver:
    """Lambda-CDM power spectrum via CLASS."""

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
        """AC-FLD-006.1: P(k,z) via CLASS for 1e-4 < k < 10 Mpc^-1, 0 < z < 10."""
        from classy import Class

        omega_cdm = omega_m - omega_b
        params = {
            "output": "mPk",
            "P_k_max_1/Mpc": k_max * 1.1,
            "z_pk": "0," + str(z_max),
            "h": h,
            "Omega_cdm": omega_cdm,
            "Omega_b": omega_b,
            "n_s": n_s,
        }
        if sigma8 is not None:
            params["sigma8"] = sigma8

        cosmo = Class()
        cosmo.set(params)
        cosmo.compute()

        k = np.logspace(np.log10(k_min), np.log10(k_max), 64)
        z_vals = np.array([0.0, 0.5, 1.0, 2.0, 5.0, z_max])
        z_vals = z_vals[z_vals <= z_max]

        Pkz = np.zeros((len(k), len(z_vals)))
        for j, z in enumerate(z_vals):
            for i, ki in enumerate(k):
                Pkz[i, j] = cosmo.pk(ki, z)

        cosmo.struct_cleanup()
        cosmo.empty()

        return PowerSpectrumResult(k=k, z=z_vals, Pkz=Pkz, theory_id="lcdm")
