"""WO-25: Perturbation theory integration for power spectra.

REQ-FLD-006: Perturbation Theory for Power Spectra
AC-FLD-006.1: Lambda-CDM via CLASS/CAMB, P(k,z) for 1e-4 < k < 10 Mpc^-1, 0 < z < 10
AC-FLD-006.2: G4v perturbations around cubic background (modified growth)
AC-FLD-006.4: NotSupported for theories without perturbation solutions
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class NotSupportedError(Exception):
    """AC-FLD-006.4: Raised when perturbation solutions unavailable for a theory."""

    pass


@dataclass
class PowerSpectrumResult:
    """Matter power spectrum P(k,z) result."""

    k: np.ndarray  # wavenumbers [Mpc^-1]
    z: np.ndarray  # redshifts
    Pkz: np.ndarray  # P(k,z) [Mpc^3]
    theory_id: str


class PerturbationSolver(Protocol):
    """Protocol for perturbation theory solvers."""

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
        """Compute P(k,z). Raises NotSupportedError if unavailable."""
        ...


def get_perturbation_solver(theory_id: str) -> PerturbationSolver | None:
    """Return perturbation solver for theory, or None if unsupported.

    AC-FLD-006.4: Returns None (or solver that raises NotSupported) for unsupported theories.
    """
    if theory_id in ("lcdm", "Lambda-CDM", "lambdacdm"):
        return _get_lcdm_solver()
    if theory_id in ("g4v", "G4v"):
        return _get_g4v_solver()
    return None


def _get_lcdm_solver() -> PerturbationSolver | None:
    """Return Lambda-CDM solver (CAMB or CLASS) if available."""
    try:
        from app.field_solvers.perturbations_camb import CambPerturbationSolver
        return CambPerturbationSolver()
    except ImportError:
        pass
    try:
        from app.field_solvers.perturbations_classy import ClassyPerturbationSolver
        return ClassyPerturbationSolver()
    except ImportError:
        pass
    return None


def _get_g4v_solver() -> PerturbationSolver | None:
    """Return G4v solver (modified growth around cubic background)."""
    try:
        from app.field_solvers.perturbations_g4v import G4vPerturbationSolver
        return G4vPerturbationSolver()
    except ImportError:
        pass
    return None


def compute_power_spectrum(
    theory_id: str,
    omega_m: float,
    omega_b: float = 0.049,
    h: float = 0.67,
    n_s: float = 0.965,
    sigma8: float | None = None,
    k_min: float = 1e-4,
    k_max: float = 10.0,
    z_max: float = 10.0,
) -> PowerSpectrumResult:
    """Compute P(k,z) for theory. Raises NotSupportedError if unavailable."""
    solver = get_perturbation_solver(theory_id)
    if solver is None:
        raise NotSupportedError(f"Perturbation solutions not available for theory '{theory_id}'")
    return solver.compute_power_spectrum(
        omega_m=omega_m,
        omega_b=omega_b,
        h=h,
        n_s=n_s,
        sigma8=sigma8,
        k_min=k_min,
        k_max=k_max,
        z_max=z_max,
    )
