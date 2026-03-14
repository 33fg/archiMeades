"""WO-34: JAX-compatible luminosity distance for NumPyro MCMC.

Uses trapezoidal integration over fixed grid. Required for differentiable
likelihood in HMC-NUTS.
"""

from __future__ import annotations

# c in km/s for Hubble distance c/H0 in Mpc
C_KM_S = 299792.458

_N_QUAD = 64  # quadrature points


def _d_l_scalar_jax(z, omega_m, i_rel, h0, theory_id: str):
    """Compute d_L(z) for scalar z using trapezoidal integration. JAX-differentiable."""
    import jax.numpy as jnp
    from app.field_solvers.jax_solvers import (
        solve_g4v_cubic_batch,
        solve_lcdm_background_batch,
    )

    a_min = 1.0 / (1.0 + z)
    if theory_id.lower() == "g4v":
        a_grid = jnp.linspace(a_min, 1.0, _N_QUAD)
        e_vals = solve_g4v_cubic_batch(a_grid, omega_m, i_rel)
    else:
        a_grid = jnp.linspace(a_min, 1.0, _N_QUAD)
        e_vals = solve_lcdm_background_batch(a_grid, omega_m)

    # integrand 1/(a^2 E(a)); avoid div by zero
    integrand = jnp.where(e_vals > 0, 1.0 / (a_grid**2 * e_vals), jnp.inf)
    integrand = jnp.where(jnp.isfinite(integrand), integrand, jnp.inf)
    # trapezoidal rule
    dx = (1.0 - a_min) / (_N_QUAD - 1)
    integral = dx * (0.5 * integrand[0] + jnp.sum(integrand[1:-1]) + 0.5 * integrand[-1])
    d_h = C_KM_S / h0
    d_c = d_h * integral
    d_l = (1.0 + z) * d_c
    return jnp.where(jnp.isfinite(d_l) & (d_l > 0), d_l, jnp.inf)


def luminosity_distance_jax(z, omega_m, i_rel, h0, theory_id: str):
    """JAX-compatible luminosity distance. Vectorized over z."""
    import jax.numpy as jnp
    from jax import vmap

    z_arr = jnp.atleast_1d(z)
    fn = lambda zi: _d_l_scalar_jax(zi, omega_m, i_rel, h0, theory_id)
    out = vmap(fn)(z_arr)
    return jnp.squeeze(out) if jnp.ndim(z) == 0 else out
