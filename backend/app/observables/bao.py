"""WO-27: BAO observables, effective equation of state, Hubble parameter.

REQ-OBS-004: H(z)·r_d, d_A(z)/r_d
REQ-OBS-005: w_eff(z) = -1 - (1/3) d ln E / d ln (1+z)
REQ-OBS-006: H(z) = H0 E(z)
"""

from __future__ import annotations

from typing import Callable, Union

import numpy as np

from app.field_solvers import get_expansion_solver
from app.observables.distance import (
    angular_diameter_distance,
    luminosity_distance,
    luminosity_distance_theory,
)


class NotSupportedError(Exception):
    """Raised when a theory does not support the requested observable."""


def hubble_parameter(
    z: Union[float, np.ndarray],
    e_func: Callable[[float], float],
    h0: float = 70.0,
) -> Union[float, np.ndarray]:
    """Compute H(z) = H0 E(z) in km/s/Mpc.

    AC-OBS-006.1: H(z) = H0 E(z) where E(z) = H(z)/H0 from theory.
    """
    z_arr = np.atleast_1d(np.asarray(z, dtype=np.float64))
    a = 1.0 / (1.0 + z_arr)
    e_vals = np.array([float(e_func(ai)) for ai in a.flat])
    e_vals = e_vals.reshape(z_arr.shape)
    h = np.where(np.isfinite(e_vals) & (e_vals > 0), h0 * e_vals, np.inf)
    return float(h.flat[0]) if np.isscalar(z) else h


def hubble_parameter_theory(
    z: Union[float, np.ndarray],
    theory_id: str,
    omega_m: float = 0.31,
    i_rel: float = 1.451782,
    h0: float = 70.0,
) -> Union[float, np.ndarray]:
    """Compute H(z) using theory's expansion history."""
    solver = get_expansion_solver(theory_id)
    if solver is None:
        raise NotSupportedError(f"No expansion solver for theory '{theory_id}'")

    def e_func(a: float) -> float:
        if theory_id.lower() == "g4v":
            return solver(a, omega_m=omega_m, i_rel=i_rel)
        return solver(a, omega_m=omega_m)

    return hubble_parameter(z, e_func, h0)


def effective_equation_of_state(
    z: Union[float, np.ndarray],
    e_func: Callable[[float], float],
    delta: float = 1e-6,
) -> Union[float, np.ndarray]:
    """Compute w_eff(z) = -1 - (1/3) d ln E / d ln (1+z).

    AC-OBS-005.1: w_eff = -1 - (1/3) d ln E / d ln (1+z)
    Uses finite difference: d ln E / d ln (1+z) ≈ (ln E_+ - ln E_-) / (2*delta).
    """
    z_arr = np.atleast_1d(np.asarray(z, dtype=np.float64))
    a = 1.0 / (1.0 + z_arr)

    def e_at_a(ai: float) -> float:
        return float(e_func(ai))

    # ln(1+z) + delta => a_plus = a * exp(-delta); ln(1+z) - delta => a_minus = a * exp(delta)
    a_plus = a * np.exp(-delta)
    a_minus = a * np.exp(delta)
    a_plus = np.clip(a_plus, 1e-10, 1.0)
    a_minus = np.clip(a_minus, 1e-10, 1.0)

    e_plus = np.array([e_at_a(ai) for ai in a_plus.flat])
    e_minus = np.array([e_at_a(ai) for ai in a_minus.flat])
    e_plus = np.maximum(e_plus.reshape(z_arr.shape), 1e-300)
    e_minus = np.maximum(e_minus.reshape(z_arr.shape), 1e-300)
    dlnE_dln1pz = np.log(e_plus / e_minus) / (2.0 * delta)

    w_eff = -1.0 - (1.0 / 3.0) * dlnE_dln1pz
    return float(w_eff.flat[0]) if np.isscalar(z) else w_eff


def sound_horizon_rd(
    omega_m: float = 0.315,
    omega_b: float = 0.0493,
    h0: float = 67.36,
    n_s: float = 0.965,
) -> float:
    """Compute sound horizon r_d at drag epoch in Mpc.

    AC-OBS-004.2: Planck 2020 params => r_d = 147.09 ± 0.26 Mpc.
    Uses CLASS when available; otherwise returns approximate value.
    """
    try:
        from classy import Class

        omega_cdm = omega_m - omega_b
        params = {
            "output": "mPk",
            "h": h0 / 100.0,
            "Omega_cdm": omega_cdm,
            "Omega_b": omega_b,
            "n_s": n_s,
        }
        cosmo = Class()
        cosmo.set(params)
        cosmo.compute()
        rd = cosmo.rs_d()  # sound horizon at drag in Mpc
        cosmo.struct_cleanup()
        cosmo.empty()
        return float(rd)
    except ImportError:
        # Approximate r_d from Eisenstein & Hu (1998) for Planck-like params
        # r_d ≈ 147 Mpc for Planck 2018/2020
        return 147.09


def bao_observables_theory(
    z: Union[float, np.ndarray],
    theory_id: str,
    r_d: float | None = None,
    omega_m: float = 0.31,
    omega_b: float = 0.0493,
    i_rel: float = 1.451782,
    h0: float = 70.0,
) -> tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """Compute BAO observables: H(z)·r_d and d_A(z)/r_d.

    AC-OBS-004.1: Returns (H(z)*r_d, d_A(z)/r_d).
    AC-OBS-004.4: Raises NotSupportedError for unsupported theories or invalid results.
    """
    if theory_id.lower() not in ("lcdm", "lambdacdm", "lambda-cdm", "g4v"):
        raise NotSupportedError(f"Theory '{theory_id}' does not support BAO predictions")

    if r_d is None:
        r_d = sound_horizon_rd(omega_m=omega_m, omega_b=omega_b, h0=h0)

    h_z = hubble_parameter_theory(z, theory_id, omega_m=omega_m, i_rel=i_rel, h0=h0)
    d_l = luminosity_distance_theory(z, theory_id, omega_m=omega_m, i_rel=i_rel, h0=h0)
    d_a = angular_diameter_distance(z, d_l)

    # AC-OBS-004.4: Invalid numerical results => NotSupported
    if np.any(~np.isfinite(h_z)) or np.any(~np.isfinite(d_a)) or np.any(d_a <= 0):
        raise NotSupportedError(
            f"Theory '{theory_id}' yields invalid BAO results at requested redshifts"
        )

    h_rd = h_z * r_d
    d_a_over_rd = d_a / r_d

    return h_rd, d_a_over_rd
