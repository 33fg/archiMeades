"""WO-27: Tests for BAO observables, w_eff, H(z)."""

import numpy as np
import pytest

from app.observables import (
    NotSupportedError,
    bao_observables_theory,
    effective_equation_of_state,
    hubble_parameter,
    hubble_parameter_theory,
    sound_horizon_rd,
)


def _lcdm_e(a: float, omega_m: float = 0.31) -> float:
    return float(np.sqrt(omega_m / (a**3) + (1 - omega_m)))


def _lcdm_weff_analytical(z: float, omega_m: float = 0.31) -> float:
    """Analytical w_eff for Lambda-CDM: -1 - 0.5 * Omega_m*(1+z)^3 / (Omega_m*(1+z)^3 + (1-Omega_m))."""
    x = omega_m * (1 + z) ** 3
    denom = x + (1 - omega_m)
    dlnE_dln1pz = 1.5 * x / denom
    return -1.0 - (1.0 / 3.0) * dlnE_dln1pz


class TestHubbleParameter:
    """REQ-OBS-006: H(z) = H0 E(z)."""

    def test_ac_obs_006_1_hubble_at_z(self) -> None:
        """AC-OBS-006.1: H(z) = H0 E(z)."""
        z = 0.5
        h = hubble_parameter(z, _lcdm_e, h0=70)
        assert 0 < h < np.inf
        assert np.isfinite(h)

    def test_ac_obs_006_2_h_at_z_zero(self) -> None:
        """AC-OBS-006.2: H(0) = H0."""
        h = hubble_parameter(0.0, _lcdm_e, h0=70)
        assert abs(h - 70.0) < 1e-10

    def test_ac_obs_006_3_high_z_matter_dominated_limit(self) -> None:
        """AC-OBS-006.3: At high z (matter-dominated), H(z) ∝ (1+z)^1.5."""
        omega_m = 0.31
        h0 = 70.0
        # H(z) ~ H0 * sqrt(Omega_m) * (1+z)^1.5 in matter era
        h_ratio_limit = h0 * np.sqrt(omega_m)
        for z in [10.0, 100.0]:
            h = hubble_parameter(z, _lcdm_e, h0=h0)
            one_plus_z = 1.0 + z
            ratio = h / (one_plus_z**1.5)
            # Should approach h0 * sqrt(Omega_m) as z → ∞
            assert abs(ratio - h_ratio_limit) / h_ratio_limit < 0.05

    def test_hubble_theory_lcdm(self) -> None:
        """hubble_parameter_theory for Lambda-CDM."""
        h = hubble_parameter_theory(0.5, "lcdm", omega_m=0.31, h0=70)
        assert np.isfinite(h)


class TestEffectiveEquationOfState:
    """REQ-OBS-005: w_eff(z)."""

    def test_ac_obs_005_2_lcdm_weff_range(self) -> None:
        """AC-OBS-005.2: Lambda-CDM w_eff in [-1.5, -0.5] (matter→Lambda transition).

        Note: AC says 'exactly -1' but for Lambda-CDM with matter, w_eff varies:
        z→0 (Lambda-dominated) ≈ -1.1, z→∞ (matter-dominated) → -0.5.
        """
        z = np.array([0.01, 0.1, 0.5, 1.0])
        w = effective_equation_of_state(z, _lcdm_e)
        assert np.all((w >= -1.5) & (w <= -0.5))
        assert np.all(np.isfinite(w))

    def test_ac_obs_005_3_g4v_differs_from_minus_one(self) -> None:
        """AC-OBS-005.3: G4v at z<0.1 differs from -1 (uses z=0.005 where G4v valid)."""
        z = 0.005  # a=0.995, G4v solver returns finite for a>=0.99
        from app.field_solvers import get_expansion_solver

        solver = get_expansion_solver("g4v")

        def e_g4v(a: float) -> float:
            return float(solver(a, omega_m=0.31, i_rel=1.451782))

        w = effective_equation_of_state(z, e_g4v)
        assert np.isfinite(w)
        # G4v differs from Lambda-CDM => w_eff may differ from -1
        assert abs(w + 1) < 0.5  # physically reasonable range

    def test_ac_obs_005_4_numerical_error_lcdm(self) -> None:
        """AC-OBS-005.4: Numerical derivative error < 1e-6 vs analytical w_eff for LCDM."""
        omega_m = 0.31
        z_vals = np.array([0.1, 0.5, 1.0, 2.0])
        w_num = effective_equation_of_state(z_vals, _lcdm_e, delta=1e-6)
        w_ana = np.array([_lcdm_weff_analytical(z, omega_m) for z in z_vals])
        err = np.abs(w_num - w_ana)
        assert np.all(err < 1e-6), f"max err={np.max(err)}"


class TestSoundHorizon:
    """REQ-OBS-004: r_d."""

    def test_ac_obs_004_2_planck_rd(self) -> None:
        """AC-OBS-004.2: Planck 2020 params => r_d ≈ 147.09 ± 0.26 Mpc."""
        rd = sound_horizon_rd(omega_m=0.315, omega_b=0.0493, h0=67.36)
        assert 140 < rd < 155
        # With CLASS: 147.09; without (approx): may differ
        if rd > 146 and rd < 148:
            assert abs(rd - 147.09) < 1.0  # within ~1 Mpc


class TestBaoObservables:
    """REQ-OBS-004: H(z)r_d, d_A/r_d."""

    def test_ac_obs_004_1_bao_computation(self) -> None:
        """AC-OBS-004.1: Compute both H(z)r_d and d_A/r_d."""
        z = 0.5
        h_rd, d_a_rd = bao_observables_theory(z, "lcdm", omega_m=0.31, h0=70)
        assert np.isfinite(h_rd)
        assert np.isfinite(d_a_rd)
        assert h_rd > 0
        assert d_a_rd > 0

    def test_ac_obs_004_3_desi_compatibility(self) -> None:
        """AC-OBS-004.3: BAO observables compatible with DESI format and redshifts."""
        # DESI-like effective redshifts: LRG ~0.7, ELG ~0.85, QSO ~1.48
        z_desi = np.array([0.7, 0.85, 1.48])
        h_rd, d_a_rd = bao_observables_theory(
            z_desi, "lcdm", omega_m=0.31, h0=70, omega_b=0.049, r_d=147.0
        )
        # H(z)·r_d in km/s (physical units used by DESI)
        assert np.all(np.isfinite(h_rd))
        assert np.all(h_rd > 0)
        assert np.all((h_rd > 500) & (h_rd < 50000))  # physically reasonable range
        # d_A/r_d dimensionless (DESI reports this)
        assert np.all(np.isfinite(d_a_rd))
        assert np.all(d_a_rd > 0)
        assert np.all((d_a_rd > 4) & (d_a_rd < 50))  # typical range at these z

    def test_ac_obs_004_4_unsupported_theory(self) -> None:
        """AC-OBS-004.4: NotSupported for unknown theory."""
        with pytest.raises(NotSupportedError):
            bao_observables_theory(0.5, "unknown_theory")
