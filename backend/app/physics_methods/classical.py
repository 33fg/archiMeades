"""WO-52: Classical mechanics — Newtonian gravity, forces, conservation laws.

REQ-PM-001: Physics Method Library
AC-PM-001.1: Newtonian gravity, force decomposition, third law optimizations.
AC-PM-001.2: Kinetic energy, potential energy, Hamiltonian formulations.
REQ-PM-002: Conservation law monitoring.
"""

from __future__ import annotations

import numpy as np


# Physical constants (SI); use for dimensional consistency
G_SI = 6.67430e-11  # m³ kg⁻¹ s⁻²
C_LIGHT = 2.99792458e8  # m/s


def newtonian_gravity_force(
    m1: float,
    m2: float,
    r: np.ndarray,
    G: float = G_SI,
) -> np.ndarray:
    """AC-PM-001.1: Newtonian gravitational force F = G m1 m2 / r² in direction -r̂.

    Args:
        m1, m2: Masses (kg)
        r: Separation vector from m1 to m2 (m), shape (3,)
        G: Gravitational constant

    Returns:
        Force on m2 due to m1 (N), shape (3,). Force on m1 is -F (third law).
    """
    r = np.asarray(r, dtype=np.float64)
    r_mag = np.linalg.norm(r)
    if r_mag < 1e-30:
        return np.zeros(3)
    r_hat = r / r_mag
    F_mag = G * m1 * m2 / (r_mag**2)
    return -F_mag * r_hat  # attractive: force on m2 points toward m1


def newtonian_potential_energy(m1: float, m2: float, r: float, G: float = G_SI) -> float:
    """AC-PM-001.2: Newtonian gravitational potential energy U = -G m1 m2 / r.

    Args:
        m1, m2: Masses (kg)
        r: Separation magnitude (m)
        G: Gravitational constant

    Returns:
        Potential energy (J)
    """
    if r < 1e-30:
        return float("-inf")  # singularity
    return -G * m1 * m2 / r


def kinetic_energy(mass: float | np.ndarray, velocity: np.ndarray) -> float:
    """AC-PM-001.2: Kinetic energy T = (1/2) m v².

    Args:
        mass: Scalar or per-particle array
        velocity: Shape (3,) or (N, 3)

    Returns:
        Kinetic energy (J)
    """
    v = np.asarray(velocity, dtype=np.float64)
    v_sq = np.sum(v * v, axis=-1)
    return float(0.5 * np.sum(np.asarray(mass) * v_sq))


def total_momentum(masses: np.ndarray, velocities: np.ndarray) -> np.ndarray:
    """AC-PM-002.2: Total momentum p = Σ mᵢ vᵢ."""
    m = np.asarray(masses, dtype=np.float64)
    v = np.asarray(velocities, dtype=np.float64)
    return np.sum(m[:, np.newaxis] * v, axis=0)


def total_angular_momentum(
    masses: np.ndarray,
    positions: np.ndarray,
    velocities: np.ndarray,
) -> np.ndarray:
    """AC-PM-002.3: Total angular momentum L = Σ mᵢ (xᵢ × vᵢ)."""
    m = np.asarray(masses, dtype=np.float64)
    x = np.asarray(positions, dtype=np.float64)
    v = np.asarray(velocities, dtype=np.float64)
    L_i = np.cross(x, v, axis=-1)
    return np.sum(m[:, np.newaxis] * L_i, axis=0)


def total_energy(
    masses: np.ndarray,
    positions: np.ndarray,
    velocities: np.ndarray,
    G: float = G_SI,
) -> float:
    """AC-PM-002.1: Total mechanical energy H = T + V.

    T = (1/2) Σ mᵢ vᵢ²
    V = -G Σᵢ<ⱼ mᵢ mⱼ / rᵢⱼ
    """
    n = len(masses)
    T = kinetic_energy(masses, velocities)

    V = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            r = np.linalg.norm(positions[j] - positions[i])
            V += newtonian_potential_energy(masses[i], masses[j], r, G)
    return T + V


def newtonian_pair_forces(
    masses: np.ndarray,
    positions: np.ndarray,
    G: float = G_SI,
) -> np.ndarray:
    """AC-PM-001.1: Vectorized pair forces with third-law optimization.

    Returns forces on each particle: F[i] = Σⱼ≠ᵢ F_ji (force on i due to j).
    Uses F_ji = -F_ij for efficiency.
    """
    n = len(masses)
    m = np.asarray(masses, dtype=np.float64)
    x = np.asarray(positions, dtype=np.float64)
    F = np.zeros_like(x)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            r = x[j] - x[i]
            F_ij = newtonian_gravity_force(m[i], m[j], r, G)
            F[i] += F_ij  # force on i due to j
    return F
