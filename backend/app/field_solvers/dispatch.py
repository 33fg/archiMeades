"""WO-23: Solver dispatch for Theory Engine integration."""

from typing import Protocol

from app.field_solvers.g4v_cubic import solve_g4v_cubic
from app.field_solvers.lcdm_background import solve_lcdm_background


class ExpansionSolver(Protocol):
    """Protocol for expansion history solvers E(a)."""

    def __call__(self, a: float, **params: float) -> float:
        """Return E(a) = H(a)/H0 given scale factor and theory parameters."""
        ...


def get_expansion_solver(theory_id: str) -> ExpansionSolver | None:
    """Return expansion solver for theory, or None if unsupported.

    WO-23: Integration with Theory Engine for solver dispatch.
    """
    if theory_id in ("g4v", "G4v"):
        return _g4v_solver
    if theory_id in ("lcdm", "Lambda-CDM", "lambdacdm"):
        return _lcdm_solver
    return None


def _g4v_solver(a: float, omega_m: float, i_rel: float, **_: float) -> float:
    """G4v expansion rate E(a)."""
    return float(solve_g4v_cubic(a, omega_m, i_rel))


def _lcdm_solver(a: float, omega_m: float, **_: float) -> float:
    """Lambda-CDM expansion rate E(a)."""
    return float(solve_lcdm_background(a, omega_m))
