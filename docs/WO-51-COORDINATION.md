# WO-51: Physics & Numerics Library — Coordination and Implementation Plan

**Status:** Draft  
**Last Updated:** 2026-03-12  
**Related:** WO-23, WO-24, WO-26, WO-52

---

## Executive Summary

WO-51 (Physics & Numerics Library Foundation) is the **critical foundation** that Field Computation, Observable Prediction, Theory Engine, and Physics Methods depend on. WO-23, WO-24, and WO-26 were implemented ahead of WO-51 and contain logic that belongs in the shared library. This document defines the coordination strategy and implementation plan.

---

## Dependency Graph

```
WO-51 (Physics & Numerics Library)  ← START HERE
    │
    ├── WO-52 (Physics Methods)     ← Uses WO-51 for numerics
    │
    ├── WO-23 (G4v Cubic, LCDM)     ← Migrate to use WO-51
    ├── WO-24 (Retardation)         ← Migrate to use WO-51
    └── WO-26 (Distance Observables)← Migrate to use WO-51
```

---

## WO-51 Scope (from Work Order)

| Module | Description | Current Location |
|--------|-------------|------------------|
| Numerical integration | Adaptive quadrature, Romberg on GPU | `scipy.integrate.quad` in WO-26; no Romberg |
| Root finding | Cardano (cubics), Newton-Raphson | `field_solvers/g4v_cubic.py` (WO-23) |
| Cosmological distances | d_L, d_A, μ, comoving | `observables/distance.py` (WO-26) |
| Parallel reduction | Retardation integrals | `field_solvers/retardation*.py` (WO-24) |
| Cross-backend validation | CPU, Mac GPU, DGX Spark | Not implemented |
| Method catalog | API, formula, precision, status | Not implemented |
| Result caching | Keyed by function + params | Not implemented |

---

## Implementation Strategy: Extract from Prototype

**Approach:** WO-23, WO-24, WO-26 serve as the **working prototype**. WO-51 extracts and generalizes their logic into a shared library.

### Phase 1: Create Library Structure (WO-51)

1. **Create `backend/app/physics_numerics/`**
   - `__init__.py` — unified API
   - `integration.py` — adaptive quadrature, Romberg (add GPU path later)
   - `roots.py` — Cardano cubic, Newton-Raphson
   - `distances.py` — cosmological distances (extract from observables)
   - `reduction.py` — parallel reduction (extract from retardation)
   - `catalog.py` — method catalog (AC-PNL-001.2, AC-PNL-003.1)
   - `validation.py` — cross-backend validation framework

2. **Add method catalog** (REQ-PNL-003)
   - Each method: formula, complexity, hardware target, precision, status
   - Clear indication: implemented vs planned

3. **Add build vs. library strategy** (REQ-PNL-004)
   - Document: custom vs. NVIDIA libs vs. battle-tested libs

### Phase 2: Extract and Migrate

| Source (WO-23/24/26) | Target (WO-51) | Migration |
|---------------------|----------------|-----------|
| `g4v_cubic.py` | `physics_numerics/roots.py` | Extract Cardano + trig cubic; keep G4v-specific coefficients in WO-23 |
| `lcdm_background.py` | `physics_numerics/roots.py` or keep in field_solvers | LCDM E(a) is analytic; may stay in field_solvers |
| `observables/distance.py` | `physics_numerics/distances.py` | Move core logic; observables layer calls physics_numerics |
| `retardation.py` | `physics_numerics/reduction.py` | Extract parallel sum; keep Liénard-Wiechert physics in field_solvers |
| `retardation_jax.py` | `physics_numerics/reduction.py` | Merge JAX path into reduction module |
| `jax_solvers.py` | `physics_numerics/` | Integrate into roots + integration with vmap |

### Phase 3: Update Consumers

- **WO-23** (`field_solvers/dispatch.py`, `g4v_cubic.py`): Call `physics_numerics.roots.solve_cubic_cardano()` instead of local implementation
- **WO-24** (`retardation.py`): Call `physics_numerics.reduction.parallel_sum()` for reduction
- **WO-26** (`observables/distance.py`): Call `physics_numerics.distances.luminosity_distance()` for integration
- **WO-52**: Use WO-51 for all numerics from day one

---

## WO-23, WO-24, WO-26 Implementation Plan Updates

### WO-23: G4v Cubic and Lambda-CDM Background Solvers

**Add to implementation plan:**
- **Dependency:** WO-51 (Physics & Numerics Library)
- **Migration:** Replace local Cardano implementation with `physics_numerics.roots.solve_cubic_cardano()`
- **Retain:** G4v cubic coefficients (2*E³ - C0*E² + Ωm*a⁻³), LCDM E(a) formula, dispatch logic, theory-specific glue

### WO-24: Retardation Integral Engine

**Add to implementation plan:**
- **Dependency:** WO-51
- **Migration:** Use `physics_numerics.reduction.parallel_sum()` for Liénard-Wiechert summation
- **Retain:** Retardation physics (κ regularization, discrete sum formula), smooth Hubble integral

### WO-26: Distance Observable Computations

**Add to implementation plan:**
- **Dependency:** WO-51
- **Migration:** Use `physics_numerics.distances.luminosity_distance()` (or equivalent)
- **Retain:** Observable layer (distance_modulus, angular_diameter_distance, theory integration via dispatch)

---

## WO-52 Alignment

WO-52 (Physics Methods) depends on WO-51. Ensure:
- G4v field equations use `physics_numerics.roots` for cubic solver
- Newtonian gravity, geodesics, etc. use `physics_numerics.integration` where needed
- No duplicate implementations — all numerics flow through WO-51

---

## File Layout (Proposed)

```
backend/app/
├── physics_numerics/          # WO-51 — NEW
│   ├── __init__.py
│   ├── integration.py        # quad, Romberg, JAX odeint
│   ├── roots.py              # Cardano, Newton-Raphson
│   ├── distances.py          # d_L, d_A, μ, comoving
│   ├── reduction.py          # parallel sum, retardation reduction
│   ├── catalog.py            # method catalog
│   └── validation.py         # cross-backend validation
│
├── field_solvers/            # WO-23, WO-24 — RETAIN, call physics_numerics
│   ├── g4v_cubic.py          # G4v coefficients → roots.solve_cubic
│   ├── lcdm_background.py
│   ├── retardation.py        # Physics → reduction.parallel_sum
│   ├── retardation_jax.py
│   └── dispatch.py
│
└── observables/              # WO-26 — RETAIN, call physics_numerics
    └── distance.py           # Theory glue → distances.luminosity_distance
```

---

## UI and API Access

**The Physics & Numerics Library has no direct UI access** — it is a stateless backend computation library (WO-51 scope: "Out of Scope: UI components or REST APIs").

**UI access flows through REST APIs** that call the library:

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────────┐
│  Frontend (UI)   │────▶│  REST API endpoints  │────▶│  physics_numerics /     │
│  React, pages   │     │  /api/observables/*  │     │  field_solvers /         │
│                 │◀────│  /api/field-solvers  │◀────│  observables             │
└─────────────────┘     └──────────────────────┘     └─────────────────────────┘
```

**Planned API surface for UI:**

| Capability | API (to add) | UI use case |
|------------|--------------|-------------|
| Luminosity distance | `POST /api/observables/distance` | Cosmology calculator, theory comparison |
| Distance modulus | (same or derived) | Supernova fit results, μ vs z plots |
| Expansion history E(a) | `POST /api/field-solvers/expand` | Theory comparison, H(z) plots |
| Retardation integral | `POST /api/field-solvers/retardation` | G4v parameter exploration |
| Method catalog | `GET /api/physics-numerics/catalog` | Developer tools, method status |

**Existing vs. planned:** WO-29 (Dataset Management) added Observations UI and upload APIs. Observable prediction APIs (distance, likelihood) are not yet exposed. A future work order (e.g. "Observable Prediction API and UI") would add these endpoints and UI components (cosmology calculator, fit results, etc.).

---

## Implementation Status (2026-03-13)

**Completed dependency chain:** WO-51 → WO-52 → WO-53 → WO-54 → WO-55 → WO-56 → WO-69

| WO  | Module | Status |
|-----|--------|--------|
| 51  | physics_numerics (roots, distances, integration) | ✅ Implemented |
| 52  | physics_methods (classical, relativistic) | ✅ Implemented |
| 53  | Romberg integration | ✅ Implemented |
| 54  | force_acceleration (direct summation) | ✅ Implemented |
| 55  | accuracy (Kahan, Richardson) | ✅ Implemented |
| 56  | gr_numerics (Christoffel, geodesic) | ✅ Implemented |
| 69  | Simulation Engine | ✅ Uses Library |
| 67  | Register-as-dataset | ✅ Implemented |
| 68  | Compute dispatch | ✅ Implemented |

## Next Steps (Future)

1. **Barnes-Hut / FMM** — WO-54: O(N log N) tree methods for N > 10³
2. **Cross-backend validation** — WO-51: CPU vs Mac GPU vs DGX Spark
3. **Newton-Raphson** — physics_numerics.roots (planned)

---

## References

- WO-51: Build Physics & Numerics Library Foundation
- WO-52: Implement Physics Methods Library
- WO-23: Implement G4v Cubic and Lambda-CDM Background Solvers
- WO-24: Implement Retardation Integral Engine with GPU Acceleration
- WO-26: Implement Distance Observable Computations
