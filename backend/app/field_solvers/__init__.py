"""WO-23/24: Field computation solvers - G4v cubic, Lambda-CDM, retardation integral."""

from app.field_solvers.dispatch import get_expansion_solver
from app.field_solvers.g4v_cubic import solve_g4v_cubic
from app.field_solvers.lcdm_background import solve_lcdm_background
from app.field_solvers.perturbations import (
    NotSupportedError,
    compute_power_spectrum,
    get_perturbation_solver,
)
from app.field_solvers.retardation import (
    SMOOTH_HUBBLE_I_REL,
    compute_retardation_discrete,
    compute_retardation_smooth_hubble,
)

__all__ = [
    "solve_g4v_cubic",
    "solve_lcdm_background",
    "get_expansion_solver",
    "compute_retardation_smooth_hubble",
    "compute_retardation_discrete",
    "SMOOTH_HUBBLE_I_REL",
    "NotSupportedError",
    "compute_power_spectrum",
    "get_perturbation_solver",
]

# Optional batch/GPU solvers (when JAX available)
try:
    from app.field_solvers.jax_solvers import (
        solve_g4v_cubic_batch,
        solve_lcdm_background_batch,
    )
    __all__ += ["solve_g4v_cubic_batch", "solve_lcdm_background_batch"]
except ImportError:
    pass
