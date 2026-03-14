"""WO-52: Tests for Physics Methods Library."""

import numpy as np
import pytest

from app.physics_methods import (
    newtonian_gravity_force,
    newtonian_potential_energy,
    newtonian_pair_forces,
    kinetic_energy,
    total_momentum,
    total_angular_momentum,
    post_newtonian_1pn_acceleration,
    regime_beta,
)
from app.physics_methods.classical import total_energy


def test_newtonian_gravity_force_attractive():
    """AC-PM-001.1: Force points toward other mass."""
    F = newtonian_gravity_force(1e30, 1e30, np.array([1e11, 0, 0]))
    assert F[0] < 0  # attractive
    assert np.allclose(np.linalg.norm(F), 6.6743e8, rtol=0.01)


def test_newtonian_potential_energy():
    """AC-PM-001.2: U = -G m1 m2 / r."""
    U = newtonian_potential_energy(1, 1, 1.0)
    assert U < 0
    assert np.isclose(U, -6.67430e-11, rtol=0.01)


def test_kinetic_energy():
    """AC-PM-001.2: T = (1/2) m v²."""
    T = kinetic_energy(2.0, np.array([3.0, 4.0, 0.0]))
    assert np.isclose(T, 25.0)  # 0.5 * 2 * (9+16)


def test_total_momentum_conservation():
    """AC-PM-002.2: p = Σ m v."""
    m = np.array([1.0, 2.0])
    v = np.array([[1.0, 0, 0], [-0.5, 0, 0]])
    p = total_momentum(m, v)
    assert np.isclose(p[0], 0.0)  # equal and opposite


def test_regime_beta():
    """Regime detection from velocity (v in m/s, c≈3e8)."""
    assert regime_beta(np.array([0, 0, 0])) == "newtonian"
    # v=3e6 m/s => beta=0.01 => newtonian
    assert regime_beta(np.array([3e6, 0, 0])) == "newtonian"
    # v=1e8 m/s => beta≈0.33 => post_newtonian
    # v=5e7 m/s => beta≈0.17
    assert regime_beta(np.array([5e7, 0, 0])) == "post_newtonian"
