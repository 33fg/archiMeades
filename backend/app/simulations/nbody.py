"""WO-69: N-body simulation engine.

Uses physics_numerics.force_acceleration (direct_summation) and physics_methods (Newtonian).
Leapfrog integration. Outputs ObservationalDataset-compatible distance_modulus for WO-67.
Uses astropy.constants.G when available.
"""

from __future__ import annotations

import numpy as np

from app.physics_numerics.force_acceleration import direct_summation_forces

try:
    from astropy.constants import G
    G_SI = float(G.si.value)
except ImportError:
    G_SI = 6.67430e-11  # m³/(kg·s²), CODATA 2018


def _leapfrog_step(
    masses: np.ndarray,
    positions: np.ndarray,
    velocities: np.ndarray,
    dt: float,
    G: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Leapfrog (velocity Verlet) step: drift-kick-drift."""
    # Kick: v += a * dt/2
    F = direct_summation_forces(masses, positions, G)
    # Softening: avoid div by zero
    acc = np.zeros_like(positions)
    for i in range(len(masses)):
        if masses[i] > 0:
            acc[i] = F[i] / masses[i]
    velocities = velocities + acc * (dt / 2)

    # Drift: x += v * dt
    positions = positions + velocities * dt

    # Kick: v += a * dt/2
    F = direct_summation_forces(masses, positions, G)
    acc = np.zeros_like(positions)
    for i in range(len(masses)):
        if masses[i] > 0:
            acc[i] = F[i] / masses[i]
    velocities = velocities + acc * (dt / 2)

    return positions, velocities


def run_nbody(
    n_particles: int = 64,
    n_steps: int = 100,
    dt: float = 1e4,  # seconds (SI)
    box_size: float = 1e18,  # m, initial box
    seed: int | None = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Run N-body simulation with leapfrog integration.

    Initial conditions: random positions in box, random velocities.
    Uses direct_summation_forces (O(N²)).
    Velocities scaled so motion is visible over n_steps (~10–20% of box).

    Returns:
        positions: (n_steps+1, n_particles, 3)
        velocities: (n_steps+1, n_particles, 3)
        masses: (n_particles,)
    """
    rng = np.random.default_rng(seed)
    masses = np.ones(n_particles) * 1e30  # kg (e.g. galaxy-scale)
    positions = rng.uniform(-box_size / 2, box_size / 2, (n_particles, 3))
    # Velocities scaled for visible motion: v*dt*n_steps ~ 0.15*box
    v_scale = 0.15 * box_size / (dt * max(1, n_steps))
    velocities = rng.uniform(-v_scale, v_scale, (n_particles, 3))  # m/s

    # Center and subtract bulk velocity
    com = np.average(positions, axis=0, weights=masses)
    positions = positions - com
    v_com = np.average(velocities, axis=0, weights=masses)
    velocities = velocities - v_com

    pos_hist = [positions.copy()]
    vel_hist = [velocities.copy()]

    for _ in range(n_steps):
        positions, velocities = _leapfrog_step(masses, positions, velocities, dt, G_SI)
        pos_hist.append(positions.copy())
        vel_hist.append(velocities.copy())

    return np.array(pos_hist), np.array(vel_hist), masses


def nbody_to_distance_modulus(
    positions: np.ndarray,
    masses: np.ndarray,
    n_points: int = 50,
    h0: float = 70.0,
) -> dict:
    """Convert N-body final snapshot to ObservationalDataset-compatible distance_modulus.

    Uses radial distances from origin as proxy for comoving distance.
    Maps to redshift via d_c ~ c/H0 * z (low-z), then d_L = (1+z) d_c, μ = 5*log10(d_L/Mpc)+25.

    Args:
        positions: (n_particles, 3) final positions in m
        masses: (n_particles,)
        n_points: number of output points (subsample if needed)
        h0: Hubble constant for distance scaling

    Returns:
        Dict with redshift, observable, statistical_uncertainty, systematic_covariance.
    """
    # Radial distances in m
    r = np.linalg.norm(positions, axis=1)
    r = np.maximum(r, 1e16)  # avoid zeros

    # Subsample to n_points
    if len(r) > n_points:
        idx = np.linspace(0, len(r) - 1, n_points, dtype=int)
        r = r[idx]

    # Scale: r (m) -> comoving distance (Mpc)
    # d_c = r / (3.086e22)  # 1 Mpc = 3.086e22 m
    c_km_s = 299792.458
    d_h = c_km_s / h0  # Hubble distance in Mpc
    # Low-z: z ~ d_c / d_H  =>  d_c = z * d_H
    # We use r as proxy: d_c (Mpc) = r_m / (3.086e22) * scale
    mpc_per_m = 1.0 / 3.086e22
    d_c_mpc = r * mpc_per_m * 1e3  # scale up for reasonable z range
    z = d_c_mpc / d_h
    z = np.clip(z, 0.01, 2.5)

    # d_L = (1+z) * d_c for flat universe
    d_l = (1 + z) * d_c_mpc
    d_l = np.maximum(d_l, 0.1)
    mu = 5 * np.log10(d_l) + 25

    n = len(z)
    stat_unc = np.full(n, 0.15)
    cov = np.eye(n) * 0.02**2

    return {
        "observable_type": "distance_modulus",
        "name": "N-body simulated (distance modulus)",
        "citation": "Derived from N-body particle positions via radial distance mapping",
        "redshift": z.tolist(),
        "observable": mu.tolist(),
        "statistical_uncertainty": stat_unc.tolist(),
        "systematic_covariance": cov.tolist(),
    }


def run_nbody_simulation(
    theory_id: str,
    theory_name: str,
    n_particles: int = 64,
    n_steps: int = 100,
    dt: float = 1e4,
    n_points: int = 50,
    h0: float = 70.0,
    seed: int | None = 42,
    include_positions: bool = True,
    max_frames: int = 21,
) -> dict:
    """Run N-body and return ObservationalDataset-compatible dict for WO-67.

    Uses run_nbody + nbody_to_distance_modulus.
    When include_positions=True, adds particle_positions for visualization:
    list of frames, each frame is list of [x,y,z] per particle (m, SI).
    Subsampled to max_frames to keep payload size reasonable.
    """
    pos_hist, _, masses = run_nbody(
        n_particles=n_particles,
        n_steps=n_steps,
        dt=dt,
        seed=seed,
    )
    final_pos = pos_hist[-1]
    base = nbody_to_distance_modulus(final_pos, masses, n_points=n_points, h0=h0)
    base["theory_id"] = theory_id
    base["theory_name"] = theory_name
    base["name"] = f"N-body simulated ({theory_name})"
    base["citation"] = f"N-body simulation output for {theory_name}"
    base["h0"] = h0
    base["n_particles"] = n_particles
    base["n_steps"] = n_steps

    if include_positions:
        n_frames = pos_hist.shape[0]
        step = max(1, (n_frames - 1) // max(1, max_frames - 1))
        indices = list(range(0, n_frames, step))
        if indices[-1] != n_frames - 1:
            indices.append(n_frames - 1)
        frames = []
        for i in indices:
            frame = pos_hist[i].tolist()
            frames.append(frame)
        base["particle_positions"] = frames
        base["position_scale_m"] = 1.0

    return base
