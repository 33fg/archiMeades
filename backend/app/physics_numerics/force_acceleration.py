"""WO-54: Force calculation acceleration — direct summation, Barnes-Hut (planned).

REQ-NM-002: AC-NM-002.1 N < 10³ direct summation.
"""

from __future__ import annotations

import numpy as np

from app.physics_methods.classical import newtonian_pair_forces


def direct_summation_forces(
    masses: np.ndarray,
    positions: np.ndarray,
    G: float = 6.67430e-11,
) -> np.ndarray:
    """AC-NM-002.1: Direct O(N²) force summation for N < 10³.

    Uses physics_methods.newtonian_pair_forces. GPU vectorization planned.
    """
    return newtonian_pair_forces(masses, positions, G)


def select_force_method(n_particles: int, accuracy_priority: bool = False) -> str:
    """Select force method by N: direct (<10³), Barnes-Hut (10³–10⁶), FMM (>10⁶)."""
    if n_particles < 1000:
        return "direct"
    if accuracy_priority or n_particles > 1e6:
        return "fmm"  # planned
    return "barnes_hut"  # planned
