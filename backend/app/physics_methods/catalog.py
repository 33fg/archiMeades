"""WO-52: Physics methods catalog — REQ-PM-001."""

from dataclasses import dataclass
from typing import Literal

Status = Literal["implemented", "planned"]


@dataclass
class PhysicsMethodEntry:
    """Single physics method in the catalog."""

    id: str
    name: str
    formula: str
    regime: str  # newtonian, post_newtonian, relativistic
    status: Status
    module: str


def get_physics_method_catalog() -> list[PhysicsMethodEntry]:
    """Return catalog of physics methods (WO-52)."""
    return [
        PhysicsMethodEntry(
            id="classical.newtonian_force",
            name="Newtonian gravitational force",
            formula="F = G m₁ m₂ / r²",
            regime="newtonian",
            status="implemented",
            module="physics_methods.classical",
        ),
        PhysicsMethodEntry(
            id="classical.potential_energy",
            name="Newtonian potential energy",
            formula="U = -G m₁ m₂ / r",
            regime="newtonian",
            status="implemented",
            module="physics_methods.classical",
        ),
        PhysicsMethodEntry(
            id="classical.kinetic_energy",
            name="Kinetic energy",
            formula="T = (1/2) m v²",
            regime="newtonian",
            status="implemented",
            module="physics_methods.classical",
        ),
        PhysicsMethodEntry(
            id="classical.total_momentum",
            name="Total momentum",
            formula="p = Σ mᵢ vᵢ",
            regime="newtonian",
            status="implemented",
            module="physics_methods.classical",
        ),
        PhysicsMethodEntry(
            id="classical.angular_momentum",
            name="Total angular momentum",
            formula="L = Σ mᵢ (xᵢ × vᵢ)",
            regime="newtonian",
            status="implemented",
            module="physics_methods.classical",
        ),
        PhysicsMethodEntry(
            id="relativistic.1pn_acceleration",
            name="Post-Newtonian 1PN acceleration",
            formula="a_1PN correction for v ~ c",
            regime="post_newtonian",
            status="implemented",
            module="physics_methods.relativistic",
        ),
        PhysicsMethodEntry(
            id="relativistic.geodesic",
            name="Geodesic equation integration",
            formula="d²xᵅ/dτ² + Γᵅᵦᵧ uᵦ uᵧ = 0",
            regime="relativistic",
            status="planned",
            module="physics_methods.relativistic",
        ),
    ]
