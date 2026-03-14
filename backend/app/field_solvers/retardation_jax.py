"""WO-24: JAX/GPU vectorized retardation integral for 10^6 sources.

AC-FLD-003.3: 10^6 sources in under 1 second on DGX.
"""

from __future__ import annotations

import numpy as np

from app.field_solvers.retardation import KAPPA_MIN


def compute_retardation_discrete_jax(masses, v_over_c):
    """Compute I_rel on GPU via JAX. Falls back to NumPy if JAX unavailable."""
    try:
        import jax.numpy as jnp

        masses_j = jnp.asarray(masses)
        v_over_c_j = jnp.asarray(v_over_c)
        M_tot = jnp.sum(masses_j)
        kappa = jnp.maximum(1.0 - v_over_c_j, KAPPA_MIN)
        weights = masses_j / M_tot
        contrib = weights / (kappa**2)
        return float(jnp.sum(contrib))
    except ImportError:
        from app.field_solvers.retardation import compute_retardation_discrete
        return compute_retardation_discrete(
            np.asarray(masses),
            np.asarray(v_over_c),
        )
