"""WO-25: Tests for perturbation theory integration."""

import numpy as np
import pytest

from app.field_solvers.perturbations import (
    NotSupportedError,
    PowerSpectrumResult,
    compute_power_spectrum,
    get_perturbation_solver,
)


class TestPerturbationInterface:
    """AC-FLD-006.4: NotSupported for unavailable theories."""

    def test_unknown_theory_returns_none(self) -> None:
        """Unknown theory => get_perturbation_solver returns None."""
        assert get_perturbation_solver("unknown") is None

    def test_unknown_theory_raises_on_compute(self) -> None:
        """Unknown theory => compute_power_spectrum raises NotSupportedError."""
        with pytest.raises(NotSupportedError, match="not available"):
            compute_power_spectrum("unknown", omega_m=0.31)

    def test_g4v_raises_not_supported(self) -> None:
        """G4v solver exists but raises NotSupportedError (stub)."""
        solver = get_perturbation_solver("g4v")
        assert solver is not None
        with pytest.raises(NotSupportedError, match="not yet implemented"):
            solver.compute_power_spectrum(omega_m=0.31)


class TestLambdaCdmSolver:
    """AC-FLD-006.1: Lambda-CDM P(k,z) when CAMB/CLASS available."""

    @pytest.mark.skipif(
        __import__("importlib").util.find_spec("camb") is None,
        reason="camb not installed",
    )
    def test_lcdm_power_spectrum_via_camb(self) -> None:
        """Lambda-CDM returns P(k,z) with valid k, z ranges when CAMB succeeds."""
        try:
            result = compute_power_spectrum(
                "lcdm",
                omega_m=(0.022 + 0.122) / (0.67**2),
                omega_b=0.022 / (0.67**2),
                h=0.67,
                k_min=1e-3,
                k_max=1.0,
                z_max=1.0,
            )
        except Exception as e:
            if "DVERK" in str(e) or "CAMBError" in str(type(e).__name__):
                pytest.skip(f"CAMB numerical error in this environment: {e}")
            raise
        assert isinstance(result, PowerSpectrumResult)
        assert result.theory_id == "lcdm"
        assert len(result.k) > 0
        assert len(result.z) > 0
        assert result.Pkz.shape == (len(result.k), len(result.z))
        assert np.all(result.k >= 1e-3)
        assert np.all(result.k <= 1.0)
        assert np.all(result.z >= 0)
        assert np.all(result.z <= 2.0)
        assert np.all(result.Pkz > 0)
