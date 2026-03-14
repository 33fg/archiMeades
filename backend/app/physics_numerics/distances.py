"""WO-51: Cosmological distance calculations.

Core numerics: d_L(z), d_A, μ, comoving integral.
Extracted from WO-26 observables/distance.py.
Theory-specific E(a) is provided by callers (field_solvers).
Uses astropy.constants for c (speed of light).
"""

from __future__ import annotations

from typing import Callable, Union

import numpy as np
from scipy import integrate

try:
    from astropy.constants import c
    C_KM_S = float(c.to("km/s").value)
except ImportError:
    C_KM_S = 299792.458  # fallback if astropy not installed


def _integrand(a: float, e_func: Callable[[float], float]) -> float:
    """Integrand 1/(a² E(a)) for comoving distance."""
    e = e_func(a)
    if e <= 0 or not np.isfinite(e):
        return np.inf
    return 1.0 / (a * a * e)


def comoving_distance_integral(
    z: Union[float, np.ndarray],
    e_func: Callable[[float], float],
    h0: float = 70.0,
) -> Union[float, np.ndarray]:
    """Compute comoving distance d_c(z) = c/H0 ∫_{1/(1+z)}^1 da/(a² E(a)) in Mpc."""
    scalar = np.isscalar(z)
    z_arr = np.atleast_1d(np.asarray(z, dtype=np.float64))
    d_h = C_KM_S / h0

    def integrand(a: float) -> float:
        return _integrand(a, e_func)

    result = np.empty_like(z_arr)
    for i, zi in enumerate(z_arr.flat):
        if zi < 0 or np.isnan(zi) or np.isinf(zi):
            result.flat[i] = np.inf
            continue
        if zi == 0:
            result.flat[i] = 0.0
            continue
        a_min = 1.0 / (1.0 + zi)
        try:
            integral, _ = integrate.quad(integrand, a_min, 1.0, limit=200)
            result.flat[i] = d_h * integral
        except (ValueError, integrate.IntegrationWarning):
            result.flat[i] = np.inf

    return float(result.flat[0]) if scalar else result


def luminosity_distance(
    z: Union[float, np.ndarray],
    e_func: Callable[[float], float],
    h0: float = 70.0,
) -> Union[float, np.ndarray]:
    """Compute luminosity distance d_L(z) = (1+z) * d_c(z) in Mpc."""
    d_c = comoving_distance_integral(z, e_func, h0)
    z_arr = np.atleast_1d(np.asarray(z, dtype=np.float64))
    scalar = np.isscalar(z)
    d_c_arr = np.atleast_1d(np.asarray(d_c, dtype=np.float64))
    d_l = (1.0 + z_arr) * d_c_arr
    return float(d_l.flat[0]) if scalar else d_l


def distance_modulus(d_l_mpc: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Compute distance modulus μ = 5*log10(d_L/Mpc) + 25."""
    d = np.asarray(d_l_mpc, dtype=np.float64)
    scalar = d.ndim == 0
    d = np.atleast_1d(d)
    mu = np.where(d > 0, 5.0 * np.log10(d) + 25.0, np.inf)
    mu = np.where(np.isfinite(d), mu, np.inf)
    return float(mu.flat[0]) if scalar else mu


def angular_diameter_distance(
    z: Union[float, np.ndarray],
    d_l_mpc: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """Compute angular diameter distance d_A = d_L/(1+z)²."""
    z_arr = np.asarray(z, dtype=np.float64)
    d_arr = np.asarray(d_l_mpc, dtype=np.float64)
    scalar = np.isscalar(z) and np.isscalar(d_l_mpc)
    z_arr = np.atleast_1d(z_arr)
    d_arr = np.atleast_1d(d_arr)
    d_a = d_arr / ((1.0 + z_arr) ** 2)
    return float(d_a.flat[0]) if scalar else d_a
