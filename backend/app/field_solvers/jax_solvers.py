"""WO-23: JAX/GPU vectorized field solvers for parameter scans.

AC-FLD-001.4: 10,000 evaluations in under 100ms on DGX (vectorized GPU).
"""

from __future__ import annotations

import numpy as np


def _solve_g4v_cubic_jax(a, omega_m, i_rel):
    """JAX implementation of G4v cubic solver. All args must be JAX arrays."""
    import jax.numpy as jnp

    c0 = 1.5 * i_rel
    d_coef = omega_m / (a**3)
    a_coef = jnp.full_like(c0, 2.0)
    b_coef = -c0
    c_coef = jnp.zeros_like(c0)

    p = (3 * a_coef * c_coef - b_coef**2) / (3 * a_coef**2)
    q = (2 * b_coef**3 - 9 * a_coef * b_coef * c_coef + 27 * a_coef**2 * d_coef) / (
        27 * a_coef**3
    )
    delta = (q / 2) ** 2 + (p / 3) ** 3

    sqrt_delta = jnp.sqrt(jnp.maximum(delta, 0.0))
    y_cardano = jnp.cbrt(-q / 2 + sqrt_delta) + jnp.cbrt(-q / 2 - sqrt_delta)

    p_safe = jnp.where(jnp.abs(p) < 1e-15, -1e-15, p)
    arg = jnp.clip(3 * q / (2 * p_safe) * jnp.sqrt(-3 / p_safe), -1.0, 1.0)
    base = jnp.arccos(arg) / 3
    y0 = 2 * jnp.sqrt(-p_safe / 3) * jnp.cos(base)
    y1 = 2 * jnp.sqrt(-p_safe / 3) * jnp.cos(base - 2 * jnp.pi / 3)
    y2 = 2 * jnp.sqrt(-p_safe / 3) * jnp.cos(base - 4 * jnp.pi / 3)
    y_trig = jnp.maximum(jnp.maximum(y0, y1), y2)

    y = jnp.where(delta >= 0, y_cardano, y_trig)
    x = y - b_coef / (3 * a_coef)

    bad = jnp.isnan(a) | jnp.isnan(omega_m) | jnp.isnan(i_rel)
    bad = bad | jnp.isinf(a) | jnp.isinf(omega_m) | jnp.isinf(i_rel)
    degenerate = jnp.abs(c0) < 1e-15
    result = jnp.where(bad | degenerate, jnp.inf, x)
    result = jnp.where(result < 0, jnp.inf, result)
    return result


def _solve_lcdm_background_jax(a, omega_m):
    """JAX implementation of Lambda-CDM background solver."""
    import jax.numpy as jnp

    radicand = omega_m / (a**3) + (1.0 - omega_m)
    result = jnp.where(radicand >= 0, jnp.sqrt(radicand), jnp.inf)
    bad = jnp.isnan(a) | jnp.isnan(omega_m) | jnp.isinf(a) | jnp.isinf(omega_m)
    return jnp.where(bad, jnp.inf, result)


def solve_g4v_cubic_batch(a, omega_m, i_rel):
    """Vectorized G4v cubic solver. Uses JAX when available for GPU acceleration."""
    try:
        import jax.numpy as jnp

        a_j = jnp.asarray(a)
        omega_m_j = jnp.asarray(omega_m)
        i_rel_j = jnp.asarray(i_rel)
        return _solve_g4v_cubic_jax(a_j, omega_m_j, i_rel_j)
    except ImportError:
        from app.field_solvers.g4v_cubic import solve_g4v_cubic
        return np.asarray(solve_g4v_cubic(a, omega_m, i_rel))


def solve_lcdm_background_batch(a, omega_m):
    """Vectorized Lambda-CDM background solver. Uses JAX when available."""
    try:
        import jax.numpy as jnp

        a_j = jnp.asarray(a)
        omega_m_j = jnp.asarray(omega_m)
        return _solve_lcdm_background_jax(a_j, omega_m_j)
    except ImportError:
        from app.field_solvers.lcdm_background import solve_lcdm_background
        return np.asarray(solve_lcdm_background(a, omega_m))
