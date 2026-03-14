"""WO-51: Tests for Physics & Numerics Library."""

import numpy as np
import pytest

from app.physics_numerics import (
    angular_diameter_distance,
    distance_modulus,
    get_method_catalog,
    luminosity_distance,
    solve_cubic,
)
from app.physics_numerics.distances import comoving_distance_integral
from app.field_solvers.g4v_cubic import solve_g4v_cubic


def _lcdm_e(a: float, omega_m: float = 0.31) -> float:
    return float(np.sqrt(omega_m / (a**3) + (1 - omega_m)))


class TestSolveCubic:
    """Root finding — Cardano cubic."""

    def test_g4v_coefficients_matches_g4v_cubic(self) -> None:
        """physics_numerics.solve_cubic with G4v coeffs matches solve_g4v_cubic."""
        a, omega_m, i_rel = 1.0, 0.31, 1.451782
        c0 = 1.5 * i_rel
        d = omega_m / (a**3)
        # G4v: 2*E^3 - C0*E^2 + d = 0  =>  a=2, b=-C0, c=0, d=d
        e_pn = solve_cubic(2.0, -c0, 0.0, d)
        e_g4v = solve_g4v_cubic(a, omega_m, i_rel)
        assert np.isclose(e_pn, e_g4v, rtol=1e-12)

    def test_scalar_and_array(self) -> None:
        """Scalar and array inputs."""
        e1 = solve_cubic(2.0, -2.18, 0.0, 0.31)
        assert np.isfinite(e1)
        # Two G4v-like cases (a=1, a=0.99) that both yield positive roots
        d1, d2 = 0.31, 0.31 / (0.99**3)
        e_arr = solve_cubic(
            np.array([2.0, 2.0]),
            np.array([-2.18, -2.18]),
            np.array([0.0, 0.0]),
            np.array([d1, d2]),
        )
        assert e_arr.shape == (2,)
        assert np.all(np.isfinite(e_arr))


class TestDistances:
    """Cosmological distances."""

    def test_luminosity_distance(self) -> None:
        """luminosity_distance matches observables."""
        from app.observables import luminosity_distance as obs_dl

        z = 0.5
        d_pn = luminosity_distance(z, _lcdm_e, h0=70)
        d_obs = obs_dl(z, _lcdm_e, h0=70)
        assert np.isclose(d_pn, d_obs, rtol=1e-12)

    def test_distance_modulus_dl_1000(self) -> None:
        """μ(1000) = 40."""
        assert abs(distance_modulus(1000.0) - 40.0) < 1e-10

    def test_angular_diameter_relation(self) -> None:
        """d_A = d_L/(1+z)²."""
        z = np.array([0.1, 0.5])
        d_l = luminosity_distance(z, _lcdm_e)
        d_a = angular_diameter_distance(z, d_l)
        np.testing.assert_allclose(d_a, d_l / ((1 + z) ** 2))


class TestCatalog:
    """Method catalog."""

    def test_catalog_non_empty(self) -> None:
        """Catalog returns methods."""
        catalog = get_method_catalog()
        assert len(catalog) >= 4
        ids = [m.id for m in catalog]
        assert "roots.cubic" in ids
        assert "distances.luminosity" in ids

    def test_implemented_vs_planned(self) -> None:
        """Some implemented, some planned."""
        catalog = get_method_catalog()
        implemented = [m for m in catalog if m.status == "implemented"]
        planned = [m for m in catalog if m.status == "planned"]
        assert len(implemented) >= 3
        assert len(planned) >= 1
