"""WO-52: Physics Methods Library — layer above Physics & Numerics (WO-51).

Implements classical mechanics (Newtonian gravity), relativistic extensions (post-Newtonian),
and provides method catalog for simulation engines (WO-69), retardation (WO-24), etc.

Uses physics_numerics for: integration, roots, reduction.
"""

from app.physics_methods.classical import (
    kinetic_energy,
    newtonian_gravity_force,
    newtonian_potential_energy,
    newtonian_pair_forces,
    total_angular_momentum,
    total_energy,
    total_momentum,
)
from app.physics_methods.relativistic import post_newtonian_1pn_acceleration, regime_beta
from app.physics_methods.catalog import get_physics_method_catalog

__all__ = [
    "newtonian_gravity_force",
    "newtonian_pair_forces",
    "newtonian_potential_energy",
    "kinetic_energy",
    "total_energy",
    "total_momentum",
    "total_angular_momentum",
    "post_newtonian_1pn_acceleration",
    "regime_beta",
    "get_physics_method_catalog",
]
