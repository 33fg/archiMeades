"""WO-24: Tests for retardation integral engine."""

import numpy as np
import pytest

from app.field_solvers.retardation import (
    KAPPA_MIN,
    SMOOTH_HUBBLE_I_REL,
    compute_retardation_discrete,
    compute_retardation_smooth_hubble,
)


class TestSmoothHubble:
    """AC-FLD-003.1: Smooth Hubble flow I_rel."""

    def test_analytic_value(self) -> None:
        """AC-FLD-003.1: Smooth Hubble flow returns 1.451782 within 10^-6."""
        i_rel = compute_retardation_smooth_hubble()
        assert abs(i_rel - 1.451782) / 1.451782 < 1e-6


class TestDiscreteRetardation:
    """AC-FLD-003.2: Discrete Liénard-Wiechert sum."""

    def test_single_particle_at_rest(self) -> None:
        """Single particle at rest: kappa=1, I_rel = 1."""
        masses = np.array([1.0])
        v_over_c = np.array([0.0])
        i_rel = compute_retardation_discrete(masses, v_over_c)
        assert abs(i_rel - 1.0) < 1e-10

    def test_two_equal_particles(self) -> None:
        """Two equal particles at rest: I_rel = 1."""
        masses = np.array([0.5, 0.5])
        v_over_c = np.array([0.0, 0.0])
        i_rel = compute_retardation_discrete(masses, v_over_c)
        assert abs(i_rel - 1.0) < 1e-10

    def test_velocity_increases_contribution(self) -> None:
        """Particle with v/c=0.5: kappa=0.5, contrib = 1/0.25 = 4."""
        masses = np.array([1.0])
        v_over_c = np.array([0.5])
        i_rel = compute_retardation_discrete(masses, v_over_c)
        assert abs(i_rel - 4.0) < 1e-10

    def test_mixed_velocities(self) -> None:
        """I_rel = 0.5*1 + 0.5*4 = 2.5 for two particles."""
        masses = np.array([0.5, 0.5])
        v_over_c = np.array([0.0, 0.5])
        i_rel = compute_retardation_discrete(masses, v_over_c)
        expected = 0.5 * (1 / 1**2) + 0.5 * (1 / 0.5**2)  # 0.5 + 2 = 2.5
        assert abs(i_rel - expected) < 1e-10

    def test_kappa_regularization(self) -> None:
        """AC-FLD-004.3: v→c (kappa→0) regularized, no overflow."""
        masses = np.array([1.0])
        v_over_c = np.array([1.0 - 1e-15])  # v very close to c
        i_rel = compute_retardation_discrete(masses, v_over_c)
        assert np.isfinite(i_rel)
        assert i_rel > 0
        # Max contrib = 1/KAPPA_MIN^2
        assert i_rel <= 1.0 / (KAPPA_MIN**2) + 1

    def test_nan_returns_inf(self) -> None:
        """AC-FLD-004.4: NaN input => Inf output."""
        assert np.isinf(compute_retardation_discrete(np.array([np.nan]), np.array([0.0])))
        assert np.isinf(compute_retardation_discrete(np.array([1.0]), np.array([np.nan])))

    def test_zero_total_mass_returns_inf(self) -> None:
        """Zero total mass => Inf."""
        masses = np.array([0.0, 0.0])
        v_over_c = np.array([0.0, 0.0])
        assert np.isinf(compute_retardation_discrete(masses, v_over_c))

    def test_large_particle_count(self) -> None:
        """AC-FLD-003.3: 10^6 sources completes (timing relaxed for CPU)."""
        import time
        n = 10**6
        masses = np.ones(n) / n  # M_tot = 1
        v_over_c = np.full(n, 0.1)  # kappa = 0.9
        t0 = time.perf_counter()
        i_rel = compute_retardation_discrete(masses, v_over_c)
        elapsed = time.perf_counter() - t0
        expected = n * (1/n) * (1 / 0.9**2)  # = 1/0.81
        assert abs(i_rel - expected) < 1e-6
        assert elapsed < 5.0, f"10^6 sources took {elapsed:.2f}s (target <1s on GPU)"
