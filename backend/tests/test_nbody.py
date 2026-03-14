"""WO-69: Tests for N-body simulation engine."""

import numpy as np
import pytest

from app.simulations.nbody import (
    nbody_to_distance_modulus,
    run_nbody,
    run_nbody_simulation,
)


class TestRunNbody:
    """N-body integration."""

    def test_run_nbody_returns_correct_shapes(self) -> None:
        """run_nbody returns positions, velocities, masses with expected shapes."""
        n_p, n_s = 32, 20
        pos, vel, masses = run_nbody(n_particles=n_p, n_steps=n_s, seed=0)
        assert pos.shape == (n_s + 1, n_p, 3)
        assert vel.shape == (n_s + 1, n_p, 3)
        assert masses.shape == (n_p,)

    def test_run_nbody_deterministic_with_seed(self) -> None:
        """Same seed yields same trajectory."""
        a = run_nbody(n_particles=16, n_steps=5, seed=42)
        b = run_nbody(n_particles=16, n_steps=5, seed=42)
        np.testing.assert_array_almost_equal(a[0], b[0])
        np.testing.assert_array_almost_equal(a[1], b[1])

    def test_run_nbody_conserves_center_of_mass_velocity(self) -> None:
        """Center of mass velocity stays near zero (no external force)."""
        _, vel, masses = run_nbody(n_particles=16, n_steps=10, seed=1)
        v_com = np.average(vel, axis=1, weights=masses)
        np.testing.assert_allclose(v_com, 0, atol=1e-6)


class TestNbodyToDistanceModulus:
    """Conversion to ObservationalDataset format."""

    def test_output_has_required_keys(self) -> None:
        """nbody_to_distance_modulus returns WO-67 compatible dict."""
        pos, masses = np.random.randn(50, 3) * 1e17, np.ones(50) * 1e30
        out = nbody_to_distance_modulus(pos, masses, n_points=20, h0=70)
        assert "observable_type" in out
        assert out["observable_type"] == "distance_modulus"
        assert "redshift" in out
        assert "observable" in out
        assert "statistical_uncertainty" in out
        assert "systematic_covariance" in out

    def test_output_length_matches_n_points(self) -> None:
        """Output arrays have length n_points (or less if fewer particles)."""
        pos, masses = np.random.randn(30, 3) * 1e17, np.ones(30) * 1e30
        out = nbody_to_distance_modulus(pos, masses, n_points=50, h0=70)
        n = len(out["redshift"])
        assert n <= 50
        assert len(out["observable"]) == n
        assert len(out["statistical_uncertainty"]) == n


class TestRunNbodySimulation:
    """Full N-body simulation pipeline."""

    def test_run_nbody_simulation_returns_observational_dataset(self) -> None:
        """run_nbody_simulation returns WO-67 compatible dict."""
        out = run_nbody_simulation(
            theory_id="tid",
            theory_name="LCDM",
            n_particles=32,
            n_steps=20,
            n_points=25,
            h0=70,
            seed=0,
        )
        assert out["observable_type"] == "distance_modulus"
        assert out["theory_id"] == "tid"
        assert out["theory_name"] == "LCDM"
        assert len(out["redshift"]) > 0
        assert len(out["redshift"]) == len(out["observable"])
