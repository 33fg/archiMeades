"""WO-51: Physics & Numerics Library — unified API.

Provides reusable numerical methods for gravitational theory evaluation:
- Root finding (Cardano cubic, Newton-Raphson)
- Cosmological distances (d_L, d_A, μ)
- Numerical integration (adaptive quadrature)
- Parallel reduction (retardation integrals)

UI access: via REST APIs that call this library. See docs/WO-51-COORDINATION.md.
"""

from app.physics_numerics.roots import solve_cubic
from app.physics_numerics.integration import romberg, adaptive_quadrature
from app.physics_numerics.accuracy import kahan_sum, richardson_extrapolate
from app.physics_numerics.force_acceleration import direct_summation_forces, select_force_method
from app.physics_numerics.gr_numerics import christoffel_symbols, geodesic_acceleration
from app.physics_numerics.distances import (
    angular_diameter_distance,
    comoving_distance_integral,
    distance_modulus,
    luminosity_distance,
)
from app.physics_numerics.catalog import get_method_catalog

__all__ = [
    "solve_cubic",
    "romberg",
    "adaptive_quadrature",
    "kahan_sum",
    "richardson_extrapolate",
    "direct_summation_forces",
    "select_force_method",
    "christoffel_symbols",
    "geodesic_acceleration",
    "luminosity_distance",
    "comoving_distance_integral",
    "distance_modulus",
    "angular_diameter_distance",
    "get_method_catalog",
]
