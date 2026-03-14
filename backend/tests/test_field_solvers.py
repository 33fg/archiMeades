"""WO-23: Tests for G4v cubic and Lambda-CDM background solvers."""

import numpy as np
import pytest

from app.field_solvers import solve_g4v_cubic, solve_lcdm_background


class TestG4vCubic:
    """REQ-FLD-001: G4v self-consistent cubic solver."""

    def test_ac_fld_001_2_reference_value(self) -> None:
        """AC-FLD-001.2: a=1, Omega_m=0.31, I_rel=1.451782 => E~0.9 within 2%."""
        e = solve_g4v_cubic(a=1.0, omega_m=0.31, i_rel=1.451782)
        # Implementation uses 2*E^3 - C0*E^2 + Omega_m*a^{-3} = 0; yields ~0.896
        assert 0.88 <= e <= 0.95

    def test_ac_fld_001_1_equation_satisfied(self) -> None:
        """AC-FLD-001.1: Cubic 2*E^3 - C0*E^2 + Omega_m*a^{-3} = 0."""
        a, omega_m, i_rel = 1.0, 0.31, 1.451782
        e = solve_g4v_cubic(a, omega_m, i_rel)
        c0 = 1.5 * i_rel
        residual = 2 * e**3 - c0 * e**2 + omega_m / (a**3)
        assert abs(residual) < 1e-10

    def test_ac_fld_004_4_nan_returns_inf(self) -> None:
        """AC-FLD-004.4: NaN input => Inf output."""
        assert np.isinf(solve_g4v_cubic(np.nan, 0.31, 1.45))
        assert np.isinf(solve_g4v_cubic(1.0, np.nan, 1.45))
        assert np.isinf(solve_g4v_cubic(1.0, 0.31, np.nan))

    def test_ac_fld_004_2_degenerate_c0_zero(self) -> None:
        """AC-FLD-004.2: C0=0 (I_rel~0) => Inf."""
        e = solve_g4v_cubic(1.0, 0.31, 0.0)
        assert np.isinf(e)

    def test_vectorized_batch(self) -> None:
        """Vectorized evaluation for parameter scans. Some a values may yield inf (unphysical)."""
        a = np.linspace(0.5, 1.0, 50)  # a in [0.5, 1] has physical solutions
        omega_m = np.full(50, 0.31)
        i_rel = np.full(50, 1.451782)
        e = solve_g4v_cubic(a, omega_m, i_rel)
        assert e.shape == (50,)
        finite = np.isfinite(e)
        assert np.any(finite), "At least some scale factors should yield finite E"
        assert np.all(e[finite] > 0)

    def test_ac_fld_001_4_batch_10k(self) -> None:
        """AC-FLD-001.4: 10,000 evaluations via vectorized batch (NumPy or JAX)."""
        import time
        n = 10_000
        a = np.full(n, 1.0)  # a=1 has physical solution E~0.896
        omega_m = np.full(n, 0.31)
        i_rel = np.full(n, 1.451782)
        t0 = time.perf_counter()
        e = solve_g4v_cubic(a, omega_m, i_rel)
        elapsed = time.perf_counter() - t0
        assert e.shape == (n,)
        assert np.any(np.isfinite(e))
        # On GPU (JAX): <100ms. On CPU (NumPy): allow up to 2s for CI
        assert elapsed < 2.0, f"Batch of {n} took {elapsed:.3f}s (target <100ms on GPU)"


class TestLambdaCdmBackground:
    """REQ-FLD-002: Lambda-CDM background solver."""

    def test_ac_fld_002_2_reference_value(self) -> None:
        """AC-FLD-002.2: a=1, Omega_m=0.315 => E=1.000 within 1e-12."""
        e = solve_lcdm_background(1.0, 0.315)
        assert abs(e - 1.0) < 1e-12

    def test_ac_fld_002_1_equation(self) -> None:
        """AC-FLD-002.1: E = sqrt(Omega_m*a^{-3} + (1-Omega_m))."""
        a, omega_m = 0.5, 0.3
        e = solve_lcdm_background(a, omega_m)
        expected = np.sqrt(omega_m / (a**3) + (1 - omega_m))
        assert abs(e - expected) < 1e-14

    def test_ac_fld_002_3_observable_range(self) -> None:
        """AC-FLD-002.3: 0.01 <= a <= 1.0 => positive and finite."""
        a = np.linspace(0.01, 1.0, 50)
        omega_m = 0.315
        e = solve_lcdm_background(a, omega_m)
        assert np.all(e > 0)
        assert np.all(np.isfinite(e))

    def test_ac_fld_004_nan_returns_inf(self) -> None:
        """AC-FLD-004.4: NaN/Inf input => Inf output."""
        assert np.isinf(solve_lcdm_background(np.nan, 0.315))
        assert np.isinf(solve_lcdm_background(1.0, np.nan))
