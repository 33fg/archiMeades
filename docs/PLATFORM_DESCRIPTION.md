# ArchiMeades: Platform Description for Experiments and Publications

> **Purpose**: This document provides a formal, publication-ready description of the ArchiMeades platform for use in Methods sections, supplementary materials, and reproducibility statements.

---

## 1. Overview

**ArchiMeades** (named after Carver Mead) is an integrated research platform for gravitational physics that encompasses both **software** and **hardware**. It enables researchers to define gravitational theories, run GPU-accelerated simulations, compare predictions with observational data, perform Bayesian inference (MCMC), and export results for publication. The platform—the full stack of application software, orchestration, and dedicated DGX compute—supports the complete workflow from theory definition through simulation, inference, and publication-ready artifacts.

### 1.1 Key Differentiator: Integrated Software + Hardware

ArchiMeades is not software-only: it is the **unified platform** of application, orchestration, and dedicated DGX cluster. A central feature is its **dedicated NVIDIA DGX GPU cluster** (16 nodes, scalable to 64), which provides high-throughput compute for gravitational physics experiments. This distinguishes ArchiMeades from typical single-machine or cloud-pay-per-use setups:

- **Dedicated GPU capacity**: DGX nodes (16, scalable to 64), each with NVIDIA GPUs, interconnected via InfiniBand and orchestrated via a heartbeat-based discovery system. The cluster reports availability and node count to the platform; compute-intensive jobs (MCMC, parameter scans, expansion simulations) are automatically routed to the DGX when estimated cost exceeds 10¹¹ FLOPS.
- **Intelligent job routing**: Jobs are routed by computational cost—lighter workloads (e.g., quick parameter exploration) run on local Mac GPU or CPU; heavy workloads (large MCMC runs, dense parameter scans) are dispatched to the DGX cluster via a dedicated Celery queue.
- **Capacity-aware behavior**: When the cluster is at capacity, the platform applies rate-limit fallback and surfaces queue depth to users. Jobs persist before execution and can be recovered if interrupted.
- **Performance targets**: JAX-based field solvers target 10,000 evaluations in under 100 ms on DGX (vectorized GPU); retardation integrals target 10⁶ sources in under 1 second.

The DGX cluster enables experiments that would be impractical on single workstations—e.g., high-chain-count MCMC, fine-grained parameter scans, and validation across many theory configurations—while keeping the same theory engine, datasets, and publication export workflow.

### 1.2 AI Integration

ArchiMeades leverages AI in unique ways to accelerate gravitational physics research. A contextual AI assistant provides workflow-aware guidance and suggestions, surfacing relevant help based on the current task (exploration, simulation, inference, or publication). Intelligent job routing uses cost estimation to automatically dispatch compute-intensive work to the DGX cluster while keeping lighter tasks local. Provenance and lineage stored in Neo4j support AI-assisted understanding of theory–simulation–observation–publication chains. These integrations distinguish ArchiMeades from conventional tools that treat AI as an add-on rather than a core part of the research workflow.

### 1.3 Advanced AI for Research

ArchiMeades is designed to support advanced AI use cases that can meaningfully advance gravitational physics research:

- **Anomaly detection in residuals**: AI can flag systematic deviations from theory predictions in Hubble diagrams or parameter scans—potential signatures of new physics or unmodeled systematics—that might be missed by visual inspection.
- **AI-guided parameter exploration**: Bayesian optimization or other surrogate-based methods can focus MCMC and scan runs on promising regions of parameter space, reducing compute time compared to uniform grids.
- **Prior elicitation and consistency**: AI can help translate physical intuition into prior distributions and check consistency between priors, likelihood, and posterior.
- **Automated literature synthesis**: Ingesting papers to extract constraints, priors, or dataset specifications for direct comparison with ArchiMeades runs.
- **Natural language to theory specification**: Converting prose descriptions of gravitational theories into executable solver code or parameter specifications.
- **Explanation generation**: Plain-language summaries of MCMC convergence, theory comparison (χ², Δχ²), and residual patterns for Methods sections or supplementary materials.

---

## 2. Platform Capabilities

### 2.1 Theory Engine

ArchiMeades implements a **theory engine** that computes cosmological and dynamical observables from gravitational theories. Supported models span **General Relativity (GR)**, **Newtonian**, and **alternative theories**:

- **GR-based (cosmological)**: **ΛCDM** — standard model with dark energy and cold dark matter. Expansion history via Friedmann equations; luminosity distance, angular diameter distance, and distance modulus computed via numerical integration. GR numerics (Christoffel symbols, geodesic acceleration) available for metric-based calculations.
- **Newtonian**: N-body particle dynamics with Newtonian gravity (F = G m₁m₂/r²); kinetic and potential energy, conservation laws. Used for simulations where v ≪ c.
- **Post-Newtonian**: 1PN corrections for regimes where v ~ c; regime detection (Newtonian vs post-Newtonian vs relativistic).
- **G4v (Gravitational 4-vector)**: Alternative theory with modified expansion dynamics. Cubic field equations (Cardano solver) for the scale factor; valid at low redshift (z ≲ 0.01) for comparison with local probes.
- **Retardation effects**: Discrete and smooth-Hubble formulations for gravitational retardation integrals.

The theory engine provides:
- **Field solvers**: Expansion history (a(t), H(z)), cubic solvers (G4v), perturbation power spectra (via CAMB/CLASS when available).
- **Observable predictions**: Luminosity distance d_L(z), angular diameter distance d_A(z), distance modulus μ(z), Hubble parameter H(z), BAO observables (D_V, D_A, H).
- **Physics & Numerics Library**: Adaptive quadrature, Romberg integration, root finding (Cardano, Newton-Raphson), GR numerics (Christoffel, geodesic), Newtonian and post-Newtonian force laws, method catalog with precision metadata.

### 2.2 Observational Datasets

The platform supports multiple observational datasets with a unified `ObservationalDataset` interface:

| Dataset | Type | Description |
|---------|------|-------------|
| **Pantheon** | Distance modulus | 1048 Type Ia supernovae, full covariance |
| **Synthetic** | Distance modulus | 5-point test set for validation |
| **DESI DR1 BGS** | Galaxy catalog | ~5M bright galaxies, z < 0.6 |
| **SDSS DR17 MPA-JHU** | Galaxy catalog | ~800K galaxies with stellar masses |

Simulation-derived datasets (from expansion or N-body runs) are registered as `Observation` records and can be used in inference via UUID. All datasets support zero-modification extension: new loaders integrate with MCMC, likelihood, and exploration tools without code changes.

### 2.3 Simulations

- **Expansion simulations**: Compute distance-modulus curves for GR (ΛCDM) or alternative (G4v) theories. Parameters: ω_m, H₀, i_rel (G4v). Output is `ObservationalDataset`-compatible for direct use in inference or comparison.
- **N-body simulations**: Particle dynamics with **Newtonian** gravity (optionally post-Newtonian corrections); positions and masses post-processed to distance-modulus observables. WebGL 3D visualization (Three.js) with orbit controls, frame stepping, and export.
- **Parameter scans**: Grid-based exploration over theory parameters.

### 2.4 Bayesian Inference (MCMC)

- **Samplers**: NumPyro (HMC-NUTS on JAX) and Emcee (affine-invariant ensemble).
- **Likelihood**: χ² with full covariance support for distance-modulus datasets.
- **Priors**: Configurable per parameter (uniform, normal, etc.).
- **Output**: Posterior samples, convergence diagnostics (R̂, ESS), trace plots, triangle plots, GetDist-compatible chain export for comparison with Cobaya/CosmoMC.

### 2.5 Compute Backends and the 8-Node DGX Cluster

Theory evaluation and MCMC can run on multiple backends:

- **CPU**: Reference implementation for validation.
- **Mac GPU (MLX)**: Apple Silicon acceleration for local development and lighter workloads.
- **DGX cluster (JAX)**: Primary backend for production experiments. NVIDIA DGX nodes (16, scalable to 64), interconnected via InfiniBand, provide dedicated GPU capacity; jobs are routed to the cluster when estimated cost exceeds 10¹¹ FLOPS. The platform polls a heartbeat endpoint for cluster availability and node count; Celery workers on the DGX consume tasks from a dedicated queue. Cross-backend validation ensures numerical agreement (relative error < 10⁻⁸) between CPU, Mac GPU, and DGX.

### 2.6 Publication Export

- **Theory comparison tables**: χ² and Δχ² for multiple theories vs. a dataset.
- **Export formats**: LaTeX tables, PDF, PNG.
- **Style presets**: ApJ, MNRAS, PRD, Nature.
- **Hubble diagram export**: SVG for figures.

---

## 3. Technical Architecture

### 3.1 Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3.11+, SQLModel (PostgreSQL/SQLite) |
| Frontend | React, TypeScript, Vite, shadcn/ui, Tailwind CSS |
| GPU / numerics | NumPy, SciPy, JAX, NumPyro, PyTorch (optional), MLX (optional) |
| **Compute cluster** | **NVIDIA DGX (16 nodes, scalable to 64), InfiniBand, Celery, Redis** |
| Data | Aurora PostgreSQL, Neo4j, S3 |
| Infrastructure | AWS (ECS Fargate, Cognito, ElastiCache Redis), Docker |

### 3.2 Workflow Modes

The user interface organizes the research workflow into:

1. **Explore**: Interactive Hubble diagram with parameter sliders, theory overlay, residuals, χ² display.
2. **N-body**: Configuration and 3D visualization of N-body simulations.
3. **Parameter Scan**: Grid-based parameter exploration.
4. **MCMC Inference**: Configure priors and sampler, run chains, view posteriors.
5. **Publish**: Theory comparison, artifact export (tables, figures).

### 3.3 Provenance and Reproducibility

- Theories, observations, and simulations are stored with metadata and versioning.
- MCMC runs record theory ID, dataset ID, prior specification, and sampler configuration.
- Export artifacts can include provenance metadata for reproducibility.

---

## 4. Prose for Paper Inclusion

The following paragraphs are written in formal academic prose and may be included directly in a Methods section or supplementary materials.

### 4.A Methods (Single Paragraph)

> All simulations and Bayesian inference were performed using ArchiMeades, an integrated research platform for gravitational physics named after Carver Mead. ArchiMeades encompasses both software and dedicated hardware: a web-based application for theory definition, observational data management, and workflow orchestration, coupled with a 16-node NVIDIA DGX GPU cluster interconnected via InfiniBand. The platform leverages AI in unique ways—including a contextual AI assistant for workflow guidance, intelligent cost-based job routing, and provenance-aware support for research lineage—integrating AI into the core workflow rather than as an add-on. Compute-intensive tasks—including Markov chain Monte Carlo (MCMC) sampling, parameter scans, and expansion simulations—are automatically routed to the cluster when estimated cost exceeds 10¹¹ FLOPS; lighter workloads execute on local CPU or Apple Silicon GPU. The platform implements ΛCDM and G4v expansion solvers, supports the Pantheon supernova sample (1048 SNe Ia) and synthetic datasets, and provides MCMC via NumPyro (HMC-NUTS on JAX) and Emcee. Chains were exported in GetDist format and validated against Cobaya where applicable.

### 4.B Methods (Extended, Two Paragraphs)

> All simulations and Bayesian inference were performed using ArchiMeades, an integrated research platform for gravitational physics named after Carver Mead. ArchiMeades encompasses both software and dedicated hardware: a web-based application for theory definition, observational data management, and workflow orchestration, coupled with a 16-node NVIDIA DGX GPU cluster (scalable to 64 nodes) interconnected via InfiniBand. The platform leverages AI in unique ways—a contextual AI assistant provides workflow-aware guidance and suggestions; intelligent cost-based routing automatically dispatches compute-intensive tasks to the DGX cluster; and provenance stored in a graph database supports AI-assisted understanding of theory–simulation–observation–publication chains. Unlike shared HPC or cloud-pay-per-use setups, ArchiMeades provides dedicated GPU capacity: compute-intensive tasks—including MCMC sampling, parameter scans, and expansion simulations—are automatically dispatched when estimated cost exceeds 10¹¹ FLOPS, while lighter workloads run on local CPU or Apple Silicon GPU. The cluster is orchestrated via a heartbeat-based discovery system; Celery workers consume tasks from a dedicated queue, and cross-backend validation ensures numerical agreement (relative error < 10⁻⁸) between CPU, Mac GPU, and DGX.
>
> The platform implements a theory engine with ΛCDM and G4v expansion solvers, cosmological distance computations (luminosity distance, angular diameter distance, distance modulus), and support for observational datasets including the Pantheon supernova sample (1048 SNe Ia) and synthetic test sets. MCMC sampling is provided via NumPyro (HMC-NUTS on JAX) and Emcee, with χ² likelihood and full covariance support. Publication export includes theory comparison tables (χ², Δχ²), LaTeX tables, and Hubble diagram figures. MCMC chains were exported in GetDist format and validated against Cobaya where applicable.

### 4.C Software and Data Availability (Short)

> All software and datasets are available at https://github.com/33fg/archiMeades. MCMC runs used NumPyro 0.15+, JAX 0.4+, and ArviZ 0.18+ for diagnostics.

---

## 5. Suggested Text for Papers (Bullet-Style)

### 5.1 Methods (Short)

> Simulations and Bayesian inference were performed using **ArchiMeades** (named after Carver Mead), an integrated gravitational physics platform encompassing software and a dedicated **NVIDIA DGX GPU cluster** (16 nodes, InfiniBand). ArchiMeades supports GR-based (ΛCDM) and Newtonian models plus alternative theories (G4v), and leverages AI in unique ways—contextual workflow guidance, intelligent job routing, provenance-aware lineage, and advanced use cases (anomaly detection, AI-guided parameter exploration). Compute-intensive jobs are automatically routed to the DGX cluster; the platform implements ΛCDM and G4v expansion solvers, Newtonian N-body dynamics, Pantheon and synthetic datasets, and exports GetDist-compatible chains for validation against Cobaya.

### 5.2 Methods (Extended)

> We used **ArchiMeades** (https://github.com/33fg/archiMeades), an integrated gravitational physics platform named after Carver Mead, for all simulations and inference. ArchiMeades encompasses both software and hardware: application, orchestration, and a dedicated **NVIDIA DGX GPU cluster** (16 nodes, scalable to 64, InfiniBand interconnect) that provides high-throughput compute for MCMC, parameter scans, and expansion simulations. The platform supports GR-based (ΛCDM) and Newtonian models plus alternative theories (G4v), and leverages AI in unique ways—a contextual AI assistant, intelligent cost-based job routing, provenance-aware lineage, and advanced use cases (anomaly detection in residuals, AI-guided parameter exploration). Jobs are routed to the cluster when estimated cost exceeds 10¹¹ FLOPS; lighter workloads run on local CPU or Mac GPU. ArchiMeades provides: (1) a theory engine with ΛCDM and G4v expansion solvers, Newtonian and post-Newtonian dynamics, and cosmological distance computations; (2) observational datasets including the Pantheon supernova sample (1048 SNe Ia) and synthetic test sets; (3) MCMC sampling via NumPyro (HMC-NUTS on JAX) and Emcee; (4) multi-backend execution with cross-backend validation; and (5) publication export (LaTeX tables, Hubble diagrams). MCMC chains were exported in GetDist format and validated against Cobaya where applicable.

### 5.3 Software Availability

> All software and datasets are available at https://github.com/33fg/archiMeades. MCMC runs used NumPyro 0.15+, JAX 0.4+, and ArviZ 0.18+ for diagnostics.

---

## 6. Reproducibility Checklist

For experiments run on ArchiMeades, we recommend reporting:

- [ ] **Platform version**: gravitational-platform 0.1.0 (or commit hash)
- [ ] **Theory identifier**: e.g., `lcdm`, `g4v`
- [ ] **Dataset**: e.g., `pantheon`, `synthetic`, or Observation UUID
- [ ] **Prior specification**: Parameter ranges and prior types
- [ ] **Sampler**: `numpyro` or `emcee`
- [ ] **MCMC settings**: num_samples, num_warmup, num_chains
- [ ] **Backend**: CPU, mac_gpu, or dgx (DGX cluster for heavy jobs)
- [ ] **DGX cluster size**: If using DGX, report node count (e.g., 16 or 64 nodes)
- [ ] **Random seed**: If fixed (e.g., for NumPyro)

---

## 7. Validation and Benchmarking

ArchiMeades MCMC and likelihood pipelines can be validated against:

- **Cobaya** (or CosmoMC): Use equivalent ΛCDM + Pantheon setup; compare best-fit χ² and posterior means. See `scripts/benchmark_cobaya.md` for configuration.
- **Cross-backend**: Run the same theory/dataset on CPU and GPU; relative differences should be < 10⁻⁸.

---

## 8. References

When citing ArchiMeades in publications, please include:

- Platform name: **ArchiMeades** (named after Carver Mead)
- Scope: **Integrated software + hardware** (application, orchestration, DGX cluster)
- AI: **Contextual assistant, intelligent job routing, provenance-aware lineage, advanced use cases** (anomaly detection, AI-guided exploration)
- Key infrastructure: **NVIDIA DGX GPU cluster** (16 nodes, scalable to 64, InfiniBand)
- Repository: https://github.com/33fg/archiMeades
- Key dependencies: NumPyro, JAX, ArviZ, Astropy, SciPy

---

*Last updated: 2025-03-14*
