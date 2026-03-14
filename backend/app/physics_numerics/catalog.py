"""WO-51: Method catalog — REQ-PNL-003.

Provides catalog of available methods with formula, complexity, hardware target,
precision, and status. AC-PNL-001.2, AC-PNL-003.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Status = Literal["implemented", "planned"]


@dataclass
class MethodEntry:
    """Single method in the catalog."""

    id: str
    name: str
    formula: str
    complexity: str
    hardware_target: str
    precision: str
    status: Status
    module: str


def get_method_catalog() -> list[MethodEntry]:
    """Return catalog of physics & numerics methods."""
    return [
        MethodEntry(
            id="roots.cubic",
            name="Cubic root (Cardano)",
            formula="ax³ + bx² + cx + d = 0",
            complexity="O(1)",
            hardware_target="CPU, GPU (JAX planned)",
            precision="10⁻¹² (analytic)",
            status="implemented",
            module="physics_numerics.roots",
        ),
        MethodEntry(
            id="distances.luminosity",
            name="Luminosity distance",
            formula="d_L = (1+z) c/H₀ ∫ da/(a² E(a))",
            complexity="O(n) per redshift, adaptive quad",
            hardware_target="CPU (scipy.quad)",
            precision="10⁻⁶ relative",
            status="implemented",
            module="physics_numerics.distances",
        ),
        MethodEntry(
            id="distances.modulus",
            name="Distance modulus",
            formula="μ = 5 log₁₀(d_L/Mpc) + 25",
            complexity="O(1)",
            hardware_target="CPU",
            precision="exact",
            status="implemented",
            module="physics_numerics.distances",
        ),
        MethodEntry(
            id="integration.romberg",
            name="Romberg integration",
            formula="Adaptive Richardson extrapolation on trapezoidal rule",
            complexity="O(n log n)",
            hardware_target="CPU, GPU (planned)",
            precision="10⁻⁸ relative",
            status="implemented",
            module="physics_numerics.integration",
        ),
        MethodEntry(
            id="roots.newton",
            name="Newton-Raphson",
            formula="x_{n+1} = x_n - f(x_n)/f'(x_n)",
            complexity="O(k) iterations",
            hardware_target="CPU, GPU (JAX autodiff)",
            precision="10⁻¹²",
            status="planned",
            module="physics_numerics.roots",
        ),
        MethodEntry(
            id="reduction.parallel_sum",
            name="Parallel reduction",
            formula="Sum over N particles with tree/multipole",
            complexity="O(N) direct, O(N log N) tree",
            hardware_target="CPU, GPU (JAX)",
            precision="configurable",
            status="planned",
            module="physics_numerics.reduction",
        ),
        MethodEntry(
            id="force.direct_summation",
            name="Direct force summation (WO-54)",
            formula="F_i = Σⱼ G m_i m_j / r²",
            complexity="O(N²)",
            hardware_target="CPU (physics_methods)",
            precision="exact",
            status="implemented",
            module="physics_numerics.force_acceleration",
        ),
        MethodEntry(
            id="accuracy.kahan_sum",
            name="Kahan compensated summation (WO-55)",
            formula="Compensated accumulator for Σ x_i",
            complexity="O(N)",
            hardware_target="CPU",
            precision="O(ε) vs O(Nε)",
            status="implemented",
            module="physics_numerics.accuracy",
        ),
        MethodEntry(
            id="accuracy.richardson",
            name="Richardson extrapolation (WO-55)",
            formula="Extrapolate f(h)→f(0) from mesh refinement",
            complexity="O(k²) for k levels",
            hardware_target="CPU",
            precision="error estimate",
            status="implemented",
            module="physics_numerics.accuracy",
        ),
        MethodEntry(
            id="gr.christoffel",
            name="Christoffel symbols (WO-56)",
            formula="Γ^α_βγ = (1/2) g^αδ (∂_β g_γδ + ...)",
            complexity="O(dim³)",
            hardware_target="CPU",
            precision="finite diff",
            status="implemented",
            module="physics_numerics.gr_numerics",
        ),
        MethodEntry(
            id="gr.geodesic",
            name="Geodesic acceleration (WO-56)",
            formula="a^α = -Γ^α_βγ u^β u^γ",
            complexity="O(dim³)",
            hardware_target="CPU",
            precision="exact from Γ",
            status="implemented",
            module="physics_numerics.gr_numerics",
        ),
        MethodEntry(
            id="observables.bao",
            name="BAO observables",
            formula="H(z)·r_d, d_A(z)/r_d",
            complexity="O(n) per redshift",
            hardware_target="CPU",
            precision="10⁻⁶",
            status="implemented",
            module="app.observables.bao",
        ),
        MethodEntry(
            id="observables.hubble",
            name="Hubble parameter",
            formula="H(z) = H0 E(z)",
            complexity="O(1)",
            hardware_target="CPU",
            precision="exact",
            status="implemented",
            module="app.observables.bao",
        ),
        MethodEntry(
            id="observables.weff",
            name="Effective equation of state",
            formula="w_eff = -1 - (1/3) d ln E / d ln (1+z)",
            complexity="O(1) with finite diff",
            hardware_target="CPU",
            precision="10⁻⁶",
            status="implemented",
            module="app.observables.bao",
        ),
        MethodEntry(
            id="likelihood.chi2",
            name="Chi-squared likelihood",
            formula="χ² = Δμᵀ C⁻¹ Δμ",
            complexity="O(n²) for n data points",
            hardware_target="CPU",
            precision="exact",
            status="implemented",
            module="app.likelihood.chi_squared",
        ),
    ]
