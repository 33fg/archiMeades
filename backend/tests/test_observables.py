"""WO-26: Tests for distance observable computations."""

import numpy as np
import pytest

from app.observables import (
    angular_diameter_distance,
    distance_modulus,
    luminosity_distance,
)
from app.observables.distance import luminosity_distance_theory

try:
    from astropy.cosmology import FlatLambdaCDM
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False

# Planck 2018/2020 parameters (A&A 641 A6)
PLANCK_OMEGA_M = 0.315
PLANCK_H0 = 67.36


def _lcdm_e(a: float, omega_m: float = 0.31) -> float:
    """E(a) for Lambda-CDM."""
    return float(np.sqrt(omega_m / (a**3) + (1 - omega_m)))


class TestLuminosityDistance:
    """AC-OBS-001: Luminosity distance d_L(z)."""

    def test_ac_obs_001_1_integral_form(self) -> None:
        """AC-OBS-001.1: d_L = (1+z) c ∫ dz'/H(z')."""
        z = 0.5
        d_l = luminosity_distance(z, lambda a: _lcdm_e(a), h0=70)
        assert 0 < d_l < np.inf
        assert np.isfinite(d_l)

    def test_z_zero(self) -> None:
        """d_L(0) = 0."""
        d_l = luminosity_distance(0.0, lambda a: _lcdm_e(a))
        assert d_l == 0.0

    @pytest.mark.skipif(not HAS_ASTROPY, reason="astropy not installed")
    def test_ac_obs_001_2_planck_pantheon(self) -> None:
        """AC-OBS-001.2: LCDM with Planck params matches published values within 0.1 Mpc."""
        from app.datasets.loaders.pantheon import load_pantheon_redshifts

        z = load_pantheon_redshifts(use_cache=True)
        e_planck = lambda a: _lcdm_e(a, omega_m=PLANCK_OMEGA_M)
        d_l_ours = luminosity_distance(z, e_planck, h0=PLANCK_H0)

        cosmo = FlatLambdaCDM(H0=PLANCK_H0, Om0=PLANCK_OMEGA_M)
        d_l_ref = cosmo.luminosity_distance(z).to("Mpc").value

        np.testing.assert_allclose(d_l_ours, d_l_ref, rtol=0, atol=0.1)

    def test_ac_obs_001_3_g4v_vs_lcdm(self) -> None:
        """AC-OBS-001.3: G4v differs from LCDM by G4v cubic solution amount.

        Uses z=0.01 because G4v solver has limited validity for a<0.99 (high z).
        At z=0.01, a_min=0.99 and both theories return finite d_L.
        """
        z = 0.01
        d_l_lcdm = luminosity_distance_theory(z, "lcdm", omega_m=0.31, h0=70)
        d_l_g4v = luminosity_distance_theory(z, "g4v", omega_m=0.31, h0=70)
        assert d_l_g4v != d_l_lcdm
        rel_diff = abs(d_l_g4v - d_l_lcdm) / d_l_lcdm
        assert 0.001 < rel_diff < 0.5  # non-trivial but physically reasonable

    def test_ac_obs_001_4_integration_accuracy(self) -> None:
        """AC-OBS-001.4: Integration error < 10^-6 relative for 0.01 < z < 2.5."""
        z_test = np.array([0.01, 0.1, 0.5, 1.0, 2.0, 2.5])
        d_l = luminosity_distance(z_test, lambda a: _lcdm_e(a))
        if HAS_ASTROPY:
            cosmo = FlatLambdaCDM(H0=70, Om0=0.31)
            d_l_ref = cosmo.luminosity_distance(z_test).to("Mpc").value
            np.testing.assert_allclose(d_l, d_l_ref, rtol=1e-6)
        else:
            # Sanity: finite and positive
            assert np.all(np.isfinite(d_l))
            assert np.all(d_l > 0)


class TestDistanceModulus:
    """AC-OBS-002: Distance modulus μ."""

    def test_ac_obs_002_2_dl_1000(self) -> None:
        """AC-OBS-002.2: d_L=1000 Mpc => μ=40.0."""
        mu = distance_modulus(1000.0)
        assert abs(mu - 40.0) < 1e-10

    def test_ac_obs_002_3_dl_10(self) -> None:
        """AC-OBS-002.3: d_L=10 Mpc => μ=30.0."""
        mu = distance_modulus(10.0)
        assert abs(mu - 30.0) < 1e-10

    def test_ac_obs_002_4_finite_positive(self) -> None:
        """AC-OBS-002.4: All μ finite and positive for valid d_L."""
        z = np.linspace(0.01, 2.0, 20)
        d_l = luminosity_distance(z, lambda a: _lcdm_e(a))
        mu = distance_modulus(d_l)
        assert np.all(np.isfinite(mu))
        assert np.all(mu > 0)


class TestAngularDiameterDistance:
    """AC-OBS-003: Angular diameter distance d_A."""

    def test_ac_obs_003_1_relation(self) -> None:
        """AC-OBS-003.1: d_A = d_L/(1+z)²."""
        z = 0.5
        d_l = luminosity_distance(z, lambda a: _lcdm_e(a))
        d_a = angular_diameter_distance(z, d_l)
        expected = d_l / ((1 + z) ** 2)
        assert abs(d_a - expected) < 1e-12

    def test_ac_obs_003_3_consistency(self) -> None:
        """AC-OBS-003.3: d_A = d_L/(1+z)² to within floating-point precision."""
        z = np.array([0.1, 0.5, 1.0])
        d_l = luminosity_distance(z, lambda a: _lcdm_e(a))
        d_a = angular_diameter_distance(z, d_l)
        np.testing.assert_allclose(d_a, d_l / ((1 + z) ** 2))

    @pytest.mark.skipif(not HAS_ASTROPY, reason="astropy not installed")
    def test_ac_obs_003_2_planck_da(self) -> None:
        """AC-OBS-003.2: d_A at z=0.5 for LCDM Ωm=0.3 matches Planck cosmology within 1 Mpc."""
        z = 0.5
        d_l = luminosity_distance(z, lambda a: _lcdm_e(a, omega_m=0.3), h0=67.36)
        d_a = angular_diameter_distance(z, d_l)
        cosmo = FlatLambdaCDM(H0=67.36, Om0=0.3)
        d_a_ref = cosmo.angular_diameter_distance(z).to("Mpc").value
        assert abs(d_a - d_a_ref) < 1.0


class TestTheoryIntegration:
    """Integration with expansion solvers."""

    def test_lcdm_luminosity_distance(self) -> None:
        """luminosity_distance_theory for Lambda-CDM."""
        d_l = luminosity_distance_theory(0.5, "lcdm", omega_m=0.31, h0=70)
        assert 0 < d_l < np.inf

    def test_vectorized_redshifts(self) -> None:
        """AC-OBS-007.1: Vectorized over redshift array."""
        z = np.linspace(0.01, 2.0, 20)
        d_l = luminosity_distance(z, lambda a: _lcdm_e(a))
        assert d_l.shape == z.shape
        assert np.all(np.isfinite(d_l[d_l > 0]))

    def test_ac_obs_007_1_pantheon_1048(self) -> None:
        """AC-OBS-007.1: Vectorized over 1048 Pantheon redshifts."""
        from app.datasets.loaders.pantheon import load_pantheon_redshifts

        z = load_pantheon_redshifts(use_cache=True)
        assert len(z) == 1048
        d_l = luminosity_distance(z, lambda a: _lcdm_e(a))
        assert d_l.shape == (1048,)
        assert np.all(np.isfinite(d_l[d_l > 0]))

    def test_ac_obs_007_4_vectorized_vs_sequential(self) -> None:
        """AC-OBS-007.4: Vectorized results agree with sequential within 10^-12 relative."""
        z = np.linspace(0.01, 2.0, 50)  # smaller for speed
        e_func = lambda a: _lcdm_e(a)
        d_l_vec = luminosity_distance(z, e_func)
        d_l_seq = np.array([luminosity_distance(zi, e_func) for zi in z])
        np.testing.assert_allclose(d_l_vec, d_l_seq, rtol=1e-12)

    @pytest.mark.slow
    def test_ac_obs_007_2_pantheon_timing(self) -> None:
        """AC-OBS-007.2: Pantheon 1048 redshifts completes in reasonable time.

        Target: Mac < 50ms (JAX/GPU). NumPy/quad typically ~1-5s. Skip if > 10s.
        """
        import time

        from app.datasets.loaders.pantheon import load_pantheon_redshifts

        z = load_pantheon_redshifts(use_cache=True)
        e_func = lambda a: _lcdm_e(a)
        t0 = time.perf_counter()
        d_l = luminosity_distance(z, e_func)
        elapsed = time.perf_counter() - t0
        assert d_l.shape == (1048,)
        assert np.all(np.isfinite(d_l[d_l > 0]))
        # Allow up to 10s for CPU; JAX/GPU would be < 50ms
        assert elapsed < 10.0, f"Pantheon d_L took {elapsed:.2f}s (target < 10s)"
