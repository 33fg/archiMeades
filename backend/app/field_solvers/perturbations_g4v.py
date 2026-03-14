"""WO-25: G4v perturbation solver (modified growth around cubic background).

AC-FLD-006.2: G4v perturbations around self-consistent cubic background.
Stub: raises NotSupportedError until modified growth equations implemented.
"""

from __future__ import annotations

from app.field_solvers.perturbations import NotSupportedError, PowerSpectrumResult


class G4vPerturbationSolver:
    """G4v power spectrum via modified growth equations. Stub implementation."""

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
        """AC-FLD-006.2: G4v perturbations - not yet implemented."""
        raise NotSupportedError(
            "G4v perturbation solutions (modified growth around cubic background) "
            "are not yet implemented. Use Lambda-CDM for power spectrum computation."
        )
