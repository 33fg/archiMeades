# Documentation Changelog

## 2026-03-14 - Platform Naming: ArchiMeades (Carver Mead)

### :memo: Documentation / :wrench: Refactor

- **Change**: Renamed platform from "Archimedes" to **ArchiMeades** (named after Carver Mead)
- **Scope**: Platform encompasses both **software** and **hardware** (application, orchestration, DGX cluster)
- **Code Changes**: PLATFORM_DESCRIPTION.md, README.md, INFINIBAND_SPECS.md, DGX-SETUP.md, dgx_orchestrator/README.md, api_v1_app.py, api_v1_theories.py, provenanceSettings.ts, Header.tsx, Footer.tsx, HomePage.tsx, LoginPage.tsx, index.html
- **Details**: Updated cluster scale to 16 nodes (scalable to 64), InfiniBand interconnect. Citation and Methods text updated.

## 2026-03-14 - InfiniBand Specifications (16–64 Node DGX Cluster)

### :memo: Documentation

- **Change**: Added `docs/INFINIBAND_SPECS.md` — verified InfiniBand specs for DGX A100/H100, Quantum switches, fabric topology
- **Reason**: Accurate reference for 16–64 node cluster with high-performance InfiniBand interconnect
- **Details**: DGX A100 (ConnectX-6/7, 200 Gb/s HDR, QM8700); DGX H100 (ConnectX-7, 400 Gb/s NDR, QM9700); SuperPOD fabric counts for 16/64 nodes; cable types; software requirements.

## 2026-03-14 - Platform Description for Experiments and Publications

### :memo: Documentation

- **Change**: Added `docs/PLATFORM_DESCRIPTION.md` — formal platform description for use in papers and experiments
- **Reason**: Need for clear, publication-ready description of Archimedes for Methods sections and reproducibility
- **Details**: Overview with **8-node DGX cluster** as key differentiator; theory engine, datasets, simulations, MCMC, compute backends (CPU, Mac GPU, DGX), publication export. Suggested Methods text emphasizes DGX cluster. Reproducibility checklist, validation notes, citation guidance.

## 2026-03-14 - Tool Integrations: Emcee, Astropy, Cobaya Benchmarking

### :rocket: New Feature

- **Change**: Emcee MCMC sampler, Astropy constants, Cobaya benchmarking guide
- **Code Changes**:
  - `backend/app/mcmc/emcee_sampler.py`: New - gradient-free ensemble MCMC
  - `backend/app/mcmc/sampler.py`: run_mcmc() dispatcher for numpyro | emcee
  - `backend/app/routers/mcmc.py`: sampler param in CreateMCMCRunRequest
  - `backend/app/tasks/mcmc.py`: sampler from payload for async jobs
  - `backend/app/physics_numerics/distances.py`: astropy.constants.c for C_KM_S
  - `backend/app/simulations/nbody.py`: astropy.constants.G for G_SI
  - `frontend/src/contexts/MCMCContext.tsx`: sampler state, setSampler
  - `frontend/src/components/mcmc/MCMCConfigControls.tsx`: Sampler dropdown
  - `scripts/benchmark_cobaya.md`: Cobaya validation guide
  - `pyproject.toml`: emcee optional dependency
- **Details**: NumPyro (HMC-NUTS) and Emcee (gradient-free) selectable in UI. Astropy used for c, G where available. Cobaya doc for ΛCDM cross-validation.

## 2026-03-14 - WO-39 Job Persistence, Checkpointing, and Recovery

### :rocket: New Feature

- **Change**: Job persistence before execution, partial result preservation on failure, orphan recovery
- **Reason**: WO-39 - Build Job Persistence, Checkpointing, and Recovery
- **Code Changes**:
  - `backend/app/models/job.py`: Added checkpoint_s3_key
  - `backend/app/services/checkpoint.py`: New - save/load checkpoint, save_partial_result
  - `backend/app/services/s3.py`: Added "jobs" resource type for checkpoint keys
  - `backend/app/routers/jobs.py`: AC-JOB-004.1 - commit job before enqueue
  - `backend/app/tasks/mcmc.py`: AC-JOB-004.4 - save partial result to S3 on failure
  - `backend/app/tasks/beat.py`: recover_orphaned_jobs - re-enqueue PENDING, mark stale RUNNING
  - `backend/alembic/versions/g7h8i9j0k1l2_add_job_checkpoint_wo39.py`: Migration
- **Details**: Job spec persisted to DB before Celery enqueue. On MCMC failure, payload and error saved to S3. Beat task every 15 min recovers orphaned PENDING (re-enqueue) and marks RUNNING >6h as failed.

## 2026-03-13 - N-Body Three.js Visualization (Replace Plotly)

### :rocket: New Feature / :wrench: Refactor

- **Change**: Replaced Plotly with Three.js (React Three Fiber) for N-body 3D visualization
- **Reason**: Plotly not suited for real-time particle simulation; Three.js offers smoother rendering, better controls, smaller bundle
- **Code Changes**:
  - `frontend/src/components/simulations/NBodyVisualization.tsx`: Rewritten with @react-three/fiber, @react-three/drei
  - Added: three, @react-three/fiber, @react-three/drei
  - Removed: plotly.js-dist-min, react-plotly.js, react-plotly.d.ts
- **Details**: WebGL particle system, OrbitControls (drag/scroll), frame stepping, Play/pause. Positions normalized for view. Bundle size reduced (~5.3MB → ~1.5MB).

## 2026-03-13 - N-Body Full Center Panel View

### :rocket: New Feature

- **Change**: Dedicated N-body workflow mode with full center panel visualization
- **Reason**: Work order — full center panel view for N-body simulation
- **Code Changes**:
  - `frontend/src/pages/NBodyPage.tsx`: New — full center panel N-body view
  - `frontend/src/contexts/NBodyContext.tsx`: Shared N-body state (simulation, preview params)
  - `frontend/src/components/nbody/NBodyConfigControls.tsx`: Right sidebar config (Live preview vs Simulation, params)
  - `frontend/src/components/simulations/NBodyVisualization.tsx`: fullHeight prop for flexible layout
  - `frontend/src/App.tsx`: Route /nbody, NBodyProvider
  - `frontend/src/components/layout/LeftSidebar.tsx`: N-body in Workflow nav
  - `frontend/src/components/layout/RightSidebar.tsx`: NBodyConfigControls when on /nbody
- **Details**: Workflow → N-body opens full center panel. Right sidebar: Live preview (particles, steps) or select completed simulation.

## 2026-03-13 - N-Body 3D Visualization

### :rocket: New Feature

- **Change**: N-body particle visualization on Simulation detail page — 3D scatter with frame slider and play/pause
- **Reason**: Allow users to see the N-body system evolve over time
- **Code Changes**:
  - `backend/app/simulations/nbody.py`: run_nbody_simulation includes particle_positions (subsampled frames)
  - `backend/app/routers/simulations.py`: GET /api/simulations/{id}/output-data
  - `frontend/src/components/simulations/NBodyVisualization.tsx`: Plotly 3D scatter, frame slider, play/pause
  - `frontend/src/pages/SimulationDetailPage.tsx`: Render NBodyVisualization when completed N-body sim
- **Details**: Interactive 3D view of particles; positions in SI (m). Play animates through timesteps.

## 2026-03-13 - WO-69 N-Body Simulation Engine

### :rocket: New Feature

- **Change**: N-body simulation type added to Simulations; produces ObservationalDataset-compatible distance modulus
- **Reason**: WO-69 Simulation Engine — use Physics & Numerics Library for N-body; WO-67 register-as-dataset support
- **Code Changes**:
  - `backend/app/simulations/nbody.py`: New — run_nbody (leapfrog), nbody_to_distance_modulus, run_nbody_simulation
  - `backend/app/tasks/simulation.py`: Branch on observable_type; nbody → run_nbody_simulation
  - `backend/app/routers/simulations.py`: SimulationCreate adds n_particles, n_steps, dt
  - `frontend/src/pages/SimulationsPage.tsx`: N-body option in observable type; particles/steps controls
  - `backend/tests/test_nbody.py`: Tests for run_nbody, nbody_to_distance_modulus, run_nbody_simulation
- **Details**: Uses direct_summation_forces (WO-54) and newtonian_pair_forces (WO-52). Leapfrog integration. Output maps particle radial distances to redshift/distance-modulus for Explore/Scan/MCMC.

## 2026-03-12 - WO-37/44 MCMC Config in Right Panel

### :rocket: New Feature / :memo: UI

- **Change**: MCMC configuration moved to right sidebar (consistent with Explore, Scan)
- **Reason**: WO-44 MCMC Sampling Mode; all mode config in right panel
- **Code Changes**:
  - `frontend/src/contexts/MCMCContext.tsx`: Shared MCMC state (theory, dataset, priors, samples, chains, run, async job polling)
  - `frontend/src/components/mcmc/MCMCConfigControls.tsx`: MCMC config component for right sidebar
  - `frontend/src/components/layout/RightSidebar.tsx`: Render MCMCConfigControls when on /inference
  - `frontend/src/pages/InferencePage.tsx`: Use MCMCContext; center shows only MCMCResultView (trace, triangle plot)
  - `frontend/src/App.tsx`: Wrap AppShell with MCMCProvider
- **Details**: Theory/dataset, priors (uniform/normal), samples/warmup/chains, Run in background, cost estimate, Run MCMC, progress in right panel. Center shows posterior results.

## 2026-03-12 - WO-43 Parameter Scanning Mode (Grid Config in Right Panel)

### :rocket: New Feature / :memo: UI

- **Change**: Scan grid configuration in right sidebar (consistent with Explore parameters)
- **Reason**: All mode config (Explore params, Scan grid) in right panel per user preference
- **Code Changes**:
  - `frontend/src/contexts/ScanContext.tsx`: Shared scan state (theory, dataset, axes, createScan, scans)
  - `frontend/src/components/scan/ScanGridControls.tsx`: Grid config component for left sidebar
  - `frontend/src/components/layout/RightSidebar.tsx`: Render ScanGridControls when on /scan
  - `frontend/src/pages/ScanPage.tsx`: Use ScanContext; center panel shows only scan results (contour plots)
  - `frontend/src/App.tsx`: Wrap AppShell with ScanProvider
- **Details**: Theory/dataset selectors, axes config (param, min, max, n, scale), Run Scan in right panel. Center shows Recent Scans with contour plots.

## 2026-03-12 - WO-30 Pantheon Distance Modulus Fix (Chi-Squared Likelihood)

### :bug: Bug Fix / :rocket: WO-30

- **Change**: Fixed Pantheon mb→distance modulus conversion; chi-squared now matches published values
- **Reason**: AC-LIK-001.2 requires Pantheon LCDM chi2 within 1.0 of published; mb is apparent magnitude, not μ
- **Code Changes**:
  - `backend/app/datasets/loaders/pantheon.py`: Convert mb to μ = mb - M (M = -19.35)
  - `backend/tests/test_likelihood.py`: Add test_ac_lik_001_2_pantheon_lcdm
- **Details**: Pantheon lcparam 'mb' is apparent magnitude. Distance modulus μ = mb - M. With M = -19.35, LCDM (Ωₘ=0.31, H₀=70) yields χ² ≈ 1029 (published ~1035).

## 2026-03-12 - WO-42 Explore Right Sidebar + Left Simulations Section

### :rocket: New Feature / :memo: UI

- **Change**: Explore parameter controls in right sidebar; Simulations section in left sidebar
- **Reason**: Parameters belong in right panel; left sidebar shows contextual navigation (simulation history per Frontend blueprint)
- **Code Changes**:
  - `frontend/src/contexts/ExploreContext.tsx`: Shared Explore state (theory, dataset, params, API fetch)
  - `frontend/src/components/explore/ExploreParameterControls.tsx`: Parameter controls component
  - `frontend/src/components/layout/RightSidebar.tsx`: Render ExploreParameterControls when on /explore
  - `frontend/src/components/layout/LeftSidebar.tsx`: Add SimulationsSection (recent simulations)
  - `frontend/src/components/layout/SimulationsSection.tsx`: New - recent simulations list with links
  - `frontend/src/pages/ExplorePage.tsx`: Use ExploreContext; center panel shows only Hubble diagram and residuals
  - `frontend/src/App.tsx`: Wrap AppShell with ExploreProvider
- **Details**: Theory/dataset selectors, Ωₘ/H₀/i_rel sliders, χ² in right sidebar. Left sidebar shows Simulations (recent 5 + View all).

## 2026-03-13 - WO-54/55/56 Completion (Full Library Chain)

### :rocket: New Feature

- **Change**: Implemented WO-54 Force Acceleration, WO-55 Accuracy, WO-56 GR numerics
- **Reason**: Complete WO-51→52→53→54→55→56→69 dependency chain
- **Code Changes**:
  - `backend/app/physics_numerics/force_acceleration.py`: direct_summation_forces (WO-54)
  - `backend/app/physics_numerics/accuracy.py`: kahan_sum, richardson_extrapolate (WO-55)
  - `backend/app/physics_numerics/gr_numerics.py`: christoffel_symbols, geodesic_acceleration (WO-56)
  - Catalog updated with 6 new method entries
- **Details**: Force acceleration delegates to physics_methods; Kahan reduces float error; Richardson estimates discretization error; Christoffel/geodesic for curved spacetime.

## 2026-03-13 - WO-52/53 Dependency Chain Completion

### :rocket: New Feature

- **Change**: Implemented WO-52 Physics Methods (classical mechanics, post-Newtonian) and WO-53 Romberg integration
- **Reason**: Complete dependency chain WO-51 → WO-52 → WO-53 → WO-69
- **Code Changes**:
  - `backend/app/physics_methods/`: New module — classical.py (Newtonian force, energy, momentum), relativistic.py (1PN, regime_beta), catalog.py
  - `backend/app/physics_numerics/integration.py`: Romberg integration implemented
  - `backend/app/routers/physics_methods.py`: GET /api/physics-methods/catalog
  - `frontend/src/pages/PhysicsNumericsPage.tsx`: Layer 2 (WO-52) physics methods table
- **Details**: WO-52 provides Newtonian gravity, kinetic/potential energy, conservation laws, 1PN correction. WO-53 Romberg available for numerical integration. Dependency chain verified.

## 2026-03-13 - Celery Docker + Session Fix

### :bug: Bug Fix / :rocket: New Feature

- **Change**: Fixed simulation task AttributeError('status'); added Celery to docker-compose; fixed Redis URL (6379)
- **Reason**: session.exec().first() returns tuple not model; user requested Docker setup for Celery
- **Code Changes**:
  - `backend/app/tasks/simulation.py`: Use .scalars().first() instead of .first() (4 places)
  - `docker-compose.yml`: Added celery service
  - `Dockerfile`: New image for backend/celery
  - `backend/.env`, `package.json`: REDIS_URL=redis://localhost:6379/0
- **Details**: Simulations now complete. Run `npm run celery:docker` to start Redis + Celery in Docker.

## 2026-03-12 - WO-51/52/67/68/69 Implementation (Library Migration, Simulation Engine, Output Integration)

### :rocket: New Feature / :memo: Migration

- **Change**: WO-51 migration (g4v_cubic, observables/distance → physics_numerics), WO-69 Simulation Engine (Library-based expansion output), WO-67 Register-as-dataset, WO-68 simulation FLOPS, frontend updates
- **Reason**: Implement dependency chain WO-51 → WO-52 → WO-69 → WO-67, WO-68 orchestration
- **Code Changes**:
  - `backend/app/field_solvers/g4v_cubic.py`: Use `physics_numerics.roots.solve_cubic` (WO-51)
  - `backend/app/observables/distance.py`: Use `physics_numerics.distances` (WO-51)
  - `backend/app/tasks/simulation.py`: Real expansion simulation via Library, ObservationalDataset output (WO-69)
  - `backend/app/routers/simulations.py`: POST `/{id}/register-as-dataset` (WO-67)
  - `backend/app/routers/observations.py`: get_dataset_data supports ObservationData (WO-67)
  - `backend/app/datasets/__init__.py`: `load_dataset` accepts Observation UUID (WO-67)
  - `backend/app/services/job_routing.py`: `estimate_simulation_flops` (WO-68)
  - `frontend/src/pages/PhysicsNumericsPage.tsx`: Layer 1 architecture context
  - `frontend/src/pages/SimulationDetailPage.tsx`: Register as dataset button (WO-67)
  - `frontend/src/pages/ExplorePage.tsx`: Dataset selector from API (builtin + custom)
- **Details**: Layer 1 (Library), Layer 2 (Engines), Layer 3 (Orchestrator). Simulated data flows to Explore/Scan/MCMC via register-as-dataset.

## 2026-03-12 - WO-37 MCMC UI Completion (Prior Preview, Cost, Parameter Selection)

### :rocket: New Feature

- **Change**: Prior distribution preview plots, cost estimation display, parameter selection for triangle plot
- **Reason**: WO-37 - Build MCMC Configuration and Posterior Visualization UI (remaining gaps)
- **Code Changes**:
  - `frontend/src/components/mcmc/PriorPreview.tsx`: New component - mini SVG preview of uniform/normal priors
  - `frontend/src/pages/InferencePage.tsx`: PriorPreview, cost estimation (GFLOP) matching backend job_routing
  - `frontend/src/components/mcmc/MCMCResultView.tsx`: Checkboxes to select which parameters appear in triangle plot
- **Details**: Prior preview shows flat bar (uniform) or bell curve (normal). Cost: ~(samples+warmup)*chains*1e6*params GFLOP; DGX hint when >100 GFLOP. Triangle plot: filter params via checkboxes.

## 2026-03-12 - Export SVG for Parameter Scan and MCMC (AC-IRE-006.4)

### :rocket: New Feature

- **Change**: Export SVG buttons on Parameter Scan contour plot and MCMC trace/triangle plots
- **Reason**: AC-IRE-006.4 - When any result is displayed, an export button shall be available; Publications page links to Scan and MCMC for figure export
- **Code Changes**:
  - `frontend/src/components/scan/LikelihoodContour.tsx`: Export SVG for 1D/2D likelihood views
  - `frontend/src/components/mcmc/TracePlot.tsx`: Export SVG for trace plot
  - `frontend/src/components/mcmc/TrianglePlot.tsx`: Export SVG for triangle plot
- **Details**: All result plots (Explore Hubble, Parameter Scan contour, MCMC trace, MCMC triangle) now have Export SVG for publication.

## 2026-03-13 - WO-45 Publication Export Mode (Complete)

### :rocket: New Feature

- **Change**: Publication Export Mode with theory comparison table and export
- **Reason**: WO-45 - Implement Publication Export Mode
- **Code Changes**:
  - `frontend/src/pages/PublicationsPage.tsx`: Export config (artifact type, style preset), theory comparison table (χ², Δχ²), LaTeX download
  - `frontend/src/pages/ExplorePage.tsx`: Export SVG button for Hubble diagram (AC-IRE-006.4)
- **Details**: AC-IRE-006.3 theory comparison (LCDM, G4v vs dataset). AC-IRE-006.4 Export LaTeX for tables, Export SVG for Explore Hubble diagram.

## 2026-03-13 - WO-42 Theory Exploration Mode Interface (Complete)

### :rocket: New Feature

- **Change**: Interactive Exploration View with parameter sliders, Hubble diagram, residuals, chi-squared
- **Reason**: WO-42 - Build Theory Exploration Mode Interface
- **Code Changes**:
  - `frontend/src/pages/ExplorePage.tsx`: Parameter controls (Ωₘ, H₀, i_rel), theory/dataset selectors, SVG Hubble plot, residual plot, debounced chi² display
  - `backend/app/routers/observables.py`: POST /api/observables/distance_modulus - theory predictions at redshifts
  - `backend/app/routers/observations.py`: GET /api/observations/datasets/{id}/data - redshift, observable, stat_unc arrays for plotting
  - `backend/app/main.py`: observables router
- **Details**: AC-IRE-002 sliders; AC-IRE-003 distance modulus plot; AC-IRE-004 residual plot; 100ms debounce. LCDM/G4v, Pantheon/Synthetic datasets.

## 2026-03-12 - WO-27 BAO and Derived Observables (Complete)

### :rocket: New Feature

- **Change**: Complete WO-27 - BAO observables, effective equation of state w_eff(z), Hubble parameter H(z)
- **Reason**: WO-27 - Implement BAO and Derived Observable Predictions
- **Code Changes**:
  - `backend/app/observables/bao.py`: hubble_parameter, hubble_parameter_theory, effective_equation_of_state, sound_horizon_rd, bao_observables_theory
  - `backend/tests/test_bao.py`: 11 tests covering AC-OBS-004, 005, 006 including DESI compatibility, numerical accuracy (<1e-6), high-z matter limit
- **Details**: REQ-OBS-004 H(z)·r_d, d_A/r_d; REQ-OBS-005 w_eff(z); REQ-OBS-006 H(z)=H0·E(z). AC-OBS-004.3 DESI redshifts; AC-OBS-005.4 analytical vs numerical w_eff; AC-OBS-006.3 matter-dominated limit. WO-27 set to in_review.

## 2026-03-13 - WO-26 Distance Observable Computations (Complete)

### :rocket: New Feature

- **Change**: Complete WO-26 - Luminosity distance, distance modulus, angular diameter distance with adaptive quadrature, result caching, and benchmarks
- **Reason**: WO-26 - Implement Distance Observable Computations
- **Code Changes**:
  - `backend/app/observables/distance.py`: epsrel=1e-6 for AC-OBS-001.4 (< 10^-6 relative error); result cache keyed by (theory, params, redshift) max 500 entries
  - `backend/tests/test_observables.py`: test_ac_obs_007_2_pantheon_timing benchmark
  - `pyproject.toml`: pytest markers for `slow`
- **Details**: AC-OBS-001.4 adaptive quadrature; WO-26 result caching. All 16 observable tests pass including Planck/Pantheon validation and vectorized vs sequential accuracy (10^-12).

## 2026-03-13 - WO-38 Job Submission and Cost-Based Routing

### :rocket: New Feature

- **Change**: Job submission with cost estimation and routing (10^11 FLOPS threshold)
- **Reason**: WO-38 - Implement Job Submission and Cost-Based Routing
- **Code Changes**:
  - `backend/app/models/job.py`: priority, retry_count, max_retries, estimated_flops, estimated_memory_mb, target_backend, payload_json, user_id
  - `backend/app/services/job_routing.py`: estimate_job_cost, route_job (mcmc/scan/theory_validation)
  - `backend/app/routers/jobs.py`: POST /api/jobs/submit, GET /api/jobs/queue
  - `backend/app/tasks/mcmc.py`: run_mcmc_task Celery task
  - `backend/app/celery_app.py`: MCMC task routing to DGX queue when configured
- **Details**: AC-JOB-001 cost estimation and routing; AC-JOB-002 queue depth and warning (>10 jobs). POST /api/jobs/submit returns job ID immediately for MCMC. GET /api/jobs/queue lists pending jobs.

## 2026-03-13 - WO-44 MCMC Sampling Mode Async Integration

### :rocket: New Feature

- **Change**: MCMC Inference UI integrates with job submission API for async runs
- **Reason**: WO-44 - Build MCMC Sampling Mode - Integration with MCMC Inference API for job submission
- **Code Changes**:
  - `frontend/src/pages/InferencePage.tsx`: "Run in background (async)" checkbox; POST /api/jobs/submit when checked; poll job status; load result_ref into MCMCResultView when completed
  - `backend/app/routers/jobs.py`: Added result_ref to JobStatusRead for WO-44 result loading
- **Details**: When "Run in background" is checked, MCMC runs via job queue; progress bar and status shown; results auto-load when job completes. Footer Jobs count updates via query invalidation.

## 2026-03-13 - WO-37 Trace Plot Axis Labels

### :memo: Documentation / Polish

- **Change**: Trace plot axis labels and tick marks for interpretability
- **Reason**: Improve MCMC posterior visualization readability
- **Code Changes**: `frontend/src/components/mcmc/TracePlot.tsx`: Y-axis value ticks (min/max), X-axis iteration ticks (0, n/2, n), "Iteration" label
- **Details**: WO-37 polish. Enables researchers to quickly read parameter ranges and sample count from trace plots.

## 2026-03-12 - WO-36 GetDist Output Format Export

### :rocket: New Feature

- **Change**: GetDist-compatible chain and paramnames export for MCMC posteriors
- **Reason**: WO-36 - Implement GetDist Output Format Export
- **Code Changes**:
  - `backend/app/mcmc/getdist_export.py`: export_getdist, export_getdist_to_strings (weight, like, params)
  - `backend/app/routers/mcmc.py`: getdist.chains_txt and getdist.paramnames_txt in MCMC response
  - `frontend/src/components/mcmc/MCMCResultView.tsx`: GetDist download button
  - `backend/tests/test_getdist_export.py`: AC-MCC-003.1 format tests
- **Details**: AC-MCC-003.1 text chains (whitespace columns), .paramnames with LaTeX labels. Thinning supported. Download as chains.txt + paramnames.

## 2026-03-12 - WO-35 Multi-Chain Convergence Diagnostics

### :rocket: New Feature

- **Change**: R-hat, ESS, divergence metrics from NumPyro MCMC
- **Reason**: WO-35 - Build Multi-Chain Convergence Diagnostics
- **Code Changes**:
  - `backend/app/mcmc/diagnostics.py`: compute_convergence_diagnostics (ArviZ rhat, ess_bulk, ess_tail)
  - `backend/app/mcmc/sampler.py`: Returns diagnostics in MCMC result
  - `backend/app/routers/mcmc.py`: diagnostics in POST /api/mcmc/runs response
  - `pyproject.toml`: arviz in numpyro extra
  - `backend/tests/test_mcmc.py`: test_diagnostics_returned (2 chains)
- **Details**: AC-MCC-001.2 R-hat < 1.1 convergence. Divergence rate warning when >1%. ESS bulk/tail via ArviZ.

## 2026-03-12 - WO-37 MCMC Configuration and Posterior Visualization UI

### :rocket: New Feature

- **Change**: MCMC configuration dialog, posterior visualization, trace/triangle plots
- **Reason**: WO-37 - Build MCMC Configuration and Posterior Visualization UI
- **Code Changes**:
  - `frontend/src/pages/InferencePage.tsx`: Config form (theory, dataset, priors, samples, chains), Run MCMC
  - `frontend/src/components/mcmc/MCMCResultView.tsx`: Summary stats, diagnostics (R-hat, ESS color-coded), trace, triangle
  - `frontend/src/components/mcmc/TracePlot.tsx`: SVG trace plots per parameter
  - `frontend/src/components/mcmc/TrianglePlot.tsx`: 2D scatter matrix for param pairs
- **Details**: Prior spec UI (uniform/normal), G4v adds i_rel. Green/yellow/red for R-hat and ESS. Credible intervals 5%/50%/95%.

## 2026-03-12 - WO-34 NumPyro HMC-NUTS Sampling Integration

### :rocket: New Feature

- **Change**: NumPyro HMC-NUTS MCMC sampling with JAX-compatible likelihood
- **Reason**: WO-34 - Implement NumPyro HMC-NUTS Sampling Integration
- **Code Changes**:
  - `backend/app/observables/distance_jax.py`: JAX trapezoidal luminosity distance
  - `backend/app/mcmc/model.py`: build_sn_model (NumPyro prior + chi² likelihood)
  - `backend/app/mcmc/sampler.py`: run_numpyro_mcmc (NUTS kernel)
  - `backend/app/routers/mcmc.py`: POST /api/mcmc/runs
  - `backend/alembic/versions/f1a2b3c4d5e6_*`: numpyro_mcmc_runs table
  - `pyproject.toml`: numpyro in jax extra
  - `backend/tests/test_mcmc.py`: Conditional MCMC test (skips without jax/numpyro)
- **Details**: AC-MCC-001.1 JAX backend; AC-MCC-001.3 Inf likelihood => reject step. Uniform/normal/log_normal priors.

## 2026-03-12 - WO-33 Scan Results Storage and Visualization

### :rocket: New Feature

- **Change**: HDF5 scan storage, slice/profile/bestfit/download API, likelihood contour UI
- **Reason**: WO-33 - Build Scan Results Storage and Visualization
- **Code Changes**:
  - `backend/app/scans/storage.py`: save_scan_hdf5, load_scan_hdf5 (gzip compression)
  - `backend/app/routers/scans.py`: HDF5 storage, GET /slice, /profile, /bestfit, /download
  - `frontend/src/components/scan/LikelihoodContour.tsx`: 1D profile + 2D heatmap
  - `frontend/src/pages/ScanPage.tsx`: Expandable scan list, contour, best-fit, download
  - `pyproject.toml`: h5py dependency
  - `backend/tests/test_scan_storage.py`: Storage tests
- **Details**: All scans stored in HDF5. Slice for 2D/3D visualization. Profile for marginalized χ². Best-fit params extraction.

## 2026-03-12 - WO-32 Vectorized Likelihood Evaluation

### :rocket: New Feature

- **Change**: Batched/parallel chi-squared evaluation for parameter scans
- **Reason**: WO-32 - Vectorized GPU Likelihood Evaluation Engine (Phase 1: CPU parallelization)
- **Code Changes**:
  - `backend/app/likelihood/chi_squared_batch.py`: compute_chi_squared_batch (ProcessPoolExecutor, chunk-based)
  - `backend/app/scans/runner.py`: Uses batch path when grid >= 64 points
  - `backend/app/likelihood/__init__.py`: Export compute_chi_squared_batch
  - `backend/tests/test_likelihood.py`: TestChiSquaredBatch (batch vs sequential, unphysical => Inf)
  - `backend/tests/test_scans.py`: test_parallel_scan_80_points
- **Details**: REQ-SCN-003. Multiprocessing parallelization; JAX/GPU path deferred. AC-SCN-001.4 preserved.

## 2026-03-12 - WO-31 Parameter Grid and Scan Configuration

### :rocket: New Feature

- **Change**: Parameter grid generation (1D, 2D, 3D), scan runner, API, Scan config UI
- **Reason**: WO-31 - Build Parameter Grid Generation and Scan Configuration
- **Code Changes**:
  - `backend/app/grid/generator.py`: generate_1d, generate_2d, generate_3d, generate_grid (linear/log)
  - `backend/app/scans/runner.py`: run_scan (evaluates likelihood at each grid point)
  - `backend/app/models/scan.py`: ParameterScan model
  - `backend/app/routers/scans.py`: POST/GET /api/scans, GET /api/scans/{id}
  - `frontend/src/pages/ScanPage.tsx`: Scan configuration form, theory/dataset/axes, run scan, recent scans list
  - `backend/tests/test_grid.py`, `test_scans.py`: AC-SCN-001 tests
- **Details**: REQ-SCN-001. Grid max 100k points. AC-SCN-001.4: unphysical => Inf, continue.

## 2026-03-12 - Center Panel Scroll Fix

### :bug: Bug Fix

- **Change**: Center/main panel scrolls when content overflows; app shell fixed to viewport height
- **Reason**: User report — center panel should scroll when needed
- **Code Changes**:
  - `frontend/src/components/layout/AppShell.tsx`: `h-screen max-h-dvh` on app-shell, `overflow-y-auto overflow-x-hidden` on main
- **Details**: App shell constrained to viewport so grid middle row has definite height; main scrolls with overflow-y-auto.

## 2026-03-12 - WO-30 Chi-Squared Likelihood Engine

### :rocket: New Feature

- **Change**: Chi-squared likelihood with full covariance, joint likelihood, API endpoints
- **Reason**: WO-30 - Implement Chi-Squared Likelihood Engine with Full Covariance
- **Code Changes**:
  - `backend/app/likelihood/chi_squared.py`: compute_chi_squared(dataset, theory_id, params)
  - `backend/app/likelihood/joint.py`: compute_joint_chi_squared(datasets, theory_id, params)
  - `backend/app/routers/likelihood.py`: POST /api/likelihood/evaluate, /api/likelihood/joint
  - `backend/app/datasets/__init__.py`: synthetic dataset for testing
  - `backend/tests/test_likelihood.py`: AC-LIK-001, AC-LIK-004 tests
- **Details**: REQ-LIK-001, REQ-LIK-004. χ² = Δμᵀ C⁻¹ Δμ. NaN/Inf => Inf. Uses ObservationalDataset.cov_inv.

## 2026-03-12 - WO-27 BAO and Derived Observable Predictions

### :rocket: New Feature

- **Change**: BAO observables (H(z)·r_d, d_A/r_d), sound horizon r_d, w_eff(z), H(z)
- **Reason**: WO-27 - Implement BAO and Derived Observable Predictions
- **Code Changes**:
  - `backend/app/observables/bao.py`: hubble_parameter, effective_equation_of_state, sound_horizon_rd, bao_observables_theory, NotSupportedError
  - `backend/app/observables/__init__.py`: exports
  - `backend/tests/test_bao.py`: AC-OBS-004, 005, 006 tests
  - `pyproject.toml`: bao extra (classy)
- **Details**: REQ-OBS-004, 005, 006. r_d via CLASS when available; fallback ~147 Mpc. G4v raises NotSupported at high z.

## 2026-03-12 - WO-51 Physics & Numerics Library (Phase 1)

### :rocket: New Feature

- **Change**: Physics & Numerics Library foundation, method catalog API, UI access path
- **Reason**: WO-51 — critical foundation; Phase 1 creates structure and first modules
- **Code Changes**:
  - `backend/app/physics_numerics/`: roots (solve_cubic), distances (d_L, μ, d_A), catalog
  - `backend/app/routers/physics_numerics.py`: GET /api/physics-numerics/catalog
  - `backend/tests/test_physics_numerics.py`: 7 tests
  - `docs/WO-51-COORDINATION.md`: Added UI/API access section
- **Details**: Extracted from WO-23/26. Catalog API enables UI. Migration of g4v_cubic/observables in Phase 2.
- **UI**: `PhysicsNumericsPage` at `/library`, sidebar nav "Library", table of methods (formula, complexity, hardware, precision, status).

## 2026-03-12 - WO-51 Coordination and Implementation Plan

### :memo: Documentation

- **Change**: Added coordination document for WO-51 (Physics & Numerics Library) and migration path for WO-23, 24, 26
- **Reason**: Strategic alignment — WO-51 is foundation; WO-23/24/26 built ahead, need to align on shared library
- **Code Changes**:
  - `docs/WO-51-COORDINATION.md`: New — dependency graph, extract-from-prototype strategy, phase plan, file layout
- **Details**: Defines WO-51 implementation plan, migration from field_solvers/observables, WO-52 alignment.

## 2026-03-12 - WO-26 Distance Observable Computations

### :rocket: New Feature

- **Change**: Luminosity distance d_L(z), distance modulus μ, angular diameter d_A
- **Reason**: WO-26 - Implement Distance Observable Computations
- **Code Changes**:
  - `backend/app/observables/distance.py`: luminosity_distance, distance_modulus, angular_diameter_distance, luminosity_distance_theory
  - `backend/app/observables/__init__.py`: exports
  - `backend/app/datasets/loaders/pantheon.py`: load_pantheon_redshifts() for tests (no covariance)
  - `backend/tests/test_observables.py`: AC-OBS-001–003, AC-OBS-007 tests
  - `pyproject.toml`: scipy, observables extra (astropy)
- **Details**: REQ-OBS-001–003, REQ-OBS-007. Vectorized over redshift arrays. Planck 2020 params. G4v at z=0.01 (solver limited for a<0.99).

## 2026-03-12 - WO-29 CSV Upload UI

### :rocket: New Feature

- **Change**: CSV upload button on ObservationsPage; api client supports FormData
- **Reason**: WO-29 - Implement Dataset Management API and UI Components
- **Code Changes**:
  - `frontend/src/pages/ObservationsPage.tsx`: Upload CSV button, file input, uploadMutation, navigate to dataset detail on success
  - `frontend/src/lib/api.ts`: api.post accepts FormData (no JSON Content-Type)
- **Details**: Users can upload CSV datasets from Observations page; redirects to dataset detail after upload.

## 2026-03-12 - WO-25 Perturbation Theory Integration

### :rocket: New Feature

- **Change**: Perturbation theory interface for power spectra P(k,z)
- **Reason**: WO-25 - Build Perturbation Theory Integration with CLASS/CAMB
- **Code Changes**:
  - `backend/app/field_solvers/perturbations.py`: NotSupportedError, get_perturbation_solver, compute_power_spectrum
  - `backend/app/field_solvers/perturbations_camb.py`: CAMB solver for Lambda-CDM
  - `backend/app/field_solvers/perturbations_classy.py`: CLASS solver (optional)
  - `backend/app/field_solvers/perturbations_g4v.py`: G4v stub (NotSupported)
  - `backend/tests/test_perturbations.py`: AC-FLD-006.1, 006.4 tests
- **Details**: REQ-FLD-006. Optional camb dependency. G4v perturbations not yet implemented.

## 2026-03-12 - WO-24 Retardation Integral Engine

### :rocket: New Feature

- **Change**: Retardation integral for G4v Machian computation
- **Reason**: WO-24 - Implement Retardation Integral Engine with GPU Acceleration
- **Code Changes**:
  - `backend/app/field_solvers/retardation.py`: compute_retardation_smooth_hubble (1.451782), compute_retardation_discrete (Liénard-Wiechert sum)
  - `backend/app/field_solvers/retardation_jax.py`: JAX/GPU path for large particle counts
  - `backend/tests/test_retardation.py`: AC-FLD-003.1, 003.2, 003.3, 004.3, 004.4 tests
- **Details**: REQ-FLD-003. kappa regularization at v→c. 10^6 sources supported.

## 2026-03-12 - WO-23 G4v Cubic and Lambda-CDM Background Solvers

### :rocket: New Feature

- **Change**: Field solvers for G4v cubic equation and Lambda-CDM expansion history
- **Reason**: WO-23 - Implement G4v Cubic and Lambda-CDM Background Solvers
- **Code Changes**:
  - `backend/app/field_solvers/g4v_cubic.py`: Cardano + trigonometric formula for cubic
  - `backend/app/field_solvers/lcdm_background.py`: E(a) = sqrt(Omega_m*a^{-3} + (1-Omega_m))
  - `backend/app/field_solvers/dispatch.py`: get_expansion_solver(theory_id) for Theory Engine
  - `backend/tests/test_field_solvers.py`: AC-FLD-001, AC-FLD-002, AC-FLD-004 tests
- **Details**: REQ-FLD-001, REQ-FLD-002. Numerical robustness (NaN/Inf => Inf). Vectorized NumPy.
  - `backend/app/field_solvers/jax_solvers.py`: JAX/GPU batch solvers (solve_g4v_cubic_batch, solve_lcdm_background_batch) for AC-FLD-001.4 (10k evals).

## 2026-03-12 - S3 Startup Integration

### :rocket: New Feature

- **Change**: LocalStack S3 integrated into startup scripts; S3 env vars set automatically for local dev
- **Reason**: S3 was showing red until manual setup; now services:start includes LocalStack and bucket creation
- **Code Changes**:
  - `package.json`: services:start includes localstack + setup-localstack-s3.sh; dev/start/restart set AWS_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY; new start:full script
  - `start.sh`, `scripts/start-app.sh`, `scripts/start-dev.sh`: S3 env vars when launching backend
- **Details**: Run `npm run services:start` (or `npm run start:full`) for full stack. Backend uses LocalStack at localhost:4566 by default.

## 2026-03-12 - Standard Dataset Type and Pantheon Loader (WO-28)

### :rocket: New Feature

- **Change**: ObservationalDataset type, Pantheon loader, load_dataset interface
- **Reason**: WO-28 - Build Standard Dataset Type and Pantheon Loader
- **Code Changes**:
  - `backend/app/datasets/observational_dataset.py`: ObservationalDataset with validation, cov_inv cache, checksum
  - `backend/app/datasets/loaders/pantheon.py`: load_pantheon() fetches from dscolnic/Pantheon, 1048 SNe
  - `backend/app/datasets/__init__.py`: load_dataset('pantheon') interface
  - `scripts/fetch-pantheon-data.py`: Optional script to pre-fetch data
- **Details**: REQ-DAT-001, REQ-DAT-002. Data cached to data/pantheon/. Scolnic et al. 2018 citation.

## 2026-03-12 - CD Pipeline and Blue-Green Deployment (WO-19)

### :rocket: New Feature

- **Change**: Enhanced CD workflow with Redis smoke tests, deploy stubs, Slack notifications
- **Reason**: WO-19 - Implement CD Pipeline and Blue-Green Deployment
- **Code Changes**:
  - `.github/workflows/cd.yml`: Redis service for staging smoke; database/Redis connectivity checks; deploy-staging and deploy-production job stubs; Slack notification step
  - `docs/DEPLOYMENT.md`: Staging smoke details, Slack setup, deploy enablement steps
- **Details**: Deploy jobs disabled until AWS infra (WO-7). Add SLACK_WEBHOOK_URL for notifications.

## 2026-03-12 - Provenance Verification and Viewer UI (WO-47)

### :rocket: New Feature

- **Change**: Provenance verification, unified endpoint, citation formatting, output checksum verification
- **Reason**: WO-47 - Build Provenance Verification and Viewer UI
- **Code Changes**:
  - `backend/app/routers/provenance.py`: GET /api/provenance/{result_type}/{result_id} unified endpoint
  - `backend/app/routers/outputs.py`: GET /api/outputs/{id}/verify for checksum verification (AC-PRV-001.4)
  - `backend/app/services/s3.py`: get_object for S3 fetch
  - `frontend/src/components/ProvenanceViewer.tsx`: Citation formatting for publication IDs
  - `frontend/src/pages/SimulationDetailPage.tsx`: Output verification UI with Verify button, warning for modified files
- **Details**: Outputs with checksum show Verify button; unified provenance supports theory|simulation result types.

## 2026-03-12 - DGX-1 Configuration (WO-22)

### :rocket: New Feature

- **Change**: Added DGX_HOST config for DGX-1 GPU cluster (JAX backend)
- **Reason**: Configure remote DGX-1 at 10.88.111.9 for future GPU execution
- **Code Changes**:
  - `backend/app/core/config.py`: Added `dgx_host` setting (default 10.88.111.9)
  - `backend/app/backends/jax_backend.py`: Use settings.dgx_host, renamed from DGX Spark to DGX-1
  - `backend/app/routers/health.py`: Include `dgx_host` in health response
  - `backend/.env`, `backend/.env.example`: Added DGX_HOST
- **Details**: Set `DGX_HOST` in .env to override. Health endpoint returns configured host.

## 2026-03-12 - DGX Orchestrator and Cluster Discovery

### :rocket: New Feature

- **Change**: DGX Orchestrator service, cluster discovery, UI shows "DGX Cluster (N)"
- **Code Changes**:
  - `dgx_orchestrator/`: Standalone FastAPI app for DGX - /health with cluster_size, Redis-based node registration
  - `backend/app/services/dgx.py`: Parse cluster_size from orchestrator response
  - `backend/app/routers/health.py`: Return dgx_cluster_size in /health
  - `frontend`: Footer and Settings show "DGX Cluster (N)" label
  - `scripts/start-dgx-orchestrator.sh`: Start orchestrator on DGX
- **Details**: Run orchestrator on each DGX node; daisy-chained nodes register in Redis; cluster_size = node count

## 2026-03-12 - DGX Configuration and Telemetry

### :rocket: New Feature

- **Change**: DGX GPU cluster config, health checks, rate limit fallback
- **Code Changes**:
  - `backend/app/core/config.py`: DGX_BASE_URL, DGX_HEALTH_PATH, DGX_TIMEOUT, DGX_ENABLED, DGX_CELERY_QUEUE
  - `backend/app/services/dgx.py`: DGX status service with HTTP health + Redis at_capacity signal
  - `backend/app/routers/health.py`: DGX status in /health response
  - `backend/app/core/security.py`: 500 req/hr fallback when DGX at capacity (AC-API-005.3)
  - `backend/app/celery_app.py`: Optional task routing to DGX queue
  - `frontend`: DGX status in Footer and Settings → System Status
  - `scripts/set-dgx-at-capacity.sh`: Set Redis flag for testing rate limit fallback
- **Details**: Set redis key `dgx:at_capacity` or DGX health returns `at_capacity: true` to trigger 500 req/hr

## 2026-03-12 - API Documentation and Error Handling (WO-50)

### :rocket: New Feature

- **Change**: OpenAPI docs at /api/v1/docs, error handling with unique IDs
- **Reason**: WO-50 - Build API Documentation and Error Handling
- **Code Changes**:
  - `backend/app/api_v1_app.py`: API v1 sub-app with Swagger at /api/v1/docs, openapi.json at /api/v1/openapi.json
  - `backend/app/main.py`: Mount api_v1_app at /api/v1; RequestValidationError handler with field-level errors; 500 handler with error_id
  - `backend/app/routers/api_v1*.py`: OpenAPI examples on request models
- **Details**: AC-API-006.1 field-level validation; AC-API-006.4 unique error_id for 500s; AC-API-007.1 interactive docs

## 2026-03-12 - Theory Query and Observable Prediction Endpoints (WO-49)

### :rocket: New Feature

- **Change**: API v1 theory query and prediction endpoints
- **Reason**: WO-49 - Implement Theory Query and Observable Prediction Endpoints
- **Code Changes**:
  - `backend/app/services/theory_execution.py`: Compile theory code, compute luminosity_distance, hubble_parameter
  - `backend/app/routers/api_v1_theories.py`: GET /api/v1/theories, GET /api/v1/theory/{id}, POST luminosity_distance, POST hubble_parameter
  - `backend/app/repositories/theory.py`: get_by_identifier also matches name for legacy theories
  - `scripts/seed-api-theory.py`: Seed Lambda-CDM theory with executable code
- **Details**: Requires API key. Batch up to 10,000 redshifts. Provenance metadata and BibTeX citation in responses.

## 2026-03-12 - API Authentication and Rate Limiting (WO-48)

### :rocket: New Feature

- **Change**: API key management, Bearer auth, rate limiting, usage logging
- **Reason**: WO-48 - Build API Authentication and Rate Limiting Infrastructure
- **Code Changes**:
  - `backend/app/models/api_key.py`: APIKey and APIUsage models
  - `backend/app/repositories/api_key.py`: APIKeyRepository, APIUsageRepository
  - `backend/app/services/api_key_service.py`: Key generation (grav_ + hex), SHA-256 hashing
  - `backend/app/core/auth.py`: resolve_user_from_api_key for Bearer API key auth
  - `backend/app/core/api_key_middleware.py`: Resolve API key, 401 for /api/v1/ without key
  - `backend/app/core/usage_logging_middleware.py`: Log requests to api_usage when API key used
  - `backend/app/core/security.py`: Per-API-key rate limit (1000/hour), per-IP (120/min)
  - `backend/app/routers/api_v1.py`: POST /api/v1/register, POST /api/v1/quota_request
- **Details**: Register at POST /api/v1/register; use Bearer token for /api/v1/*; X-RateLimit-* headers in responses

## 2025-03-12 - LocalStack Support for S3 (WO-4)

### :rocket: New Feature

- **Change**: S3 works with LocalStack for local development
- **Code Changes**:
  - `app/core/config.py`: Added `aws_endpoint_url` (optional)
  - `app/services/s3.py`, `app/routers/health.py`: Use endpoint_url when set
  - `scripts/setup-localstack-s3.sh`: Create bucket in LocalStack
- **Details**: Set `AWS_ENDPOINT_URL=http://localhost:4566` and run LocalStack for local S3 without real AWS

## 2025-03-12 - Theory Registration and Validation (WO-21)

### :rocket: New Feature

- **Change**: Theory registration API with interface validation
- **Code Changes**:
  - Migration: add identifier, version, code, validation_passed, validation_report to theories
  - `POST /api/theories/register`: accepts identifier, version, code; validates interface (luminosity_distance, age_of_universe); returns 202 with theory_id and status_url
  - `GET /api/theories/{id}/validation-status`: returns validation report
  - `app/services/theory_validation.py`: AST-based interface validation
  - `app/tasks/theory_validation.py`: Celery task for async validation
- **Details**: Required methods: luminosity_distance, age_of_universe. Invalid code returns 422 with missing_methods list.

## 2025-03-12 - Telemetry Bar and Settings System Status

### :rocket: New Feature

- **Change**: Telemetry bar (Footer) and Settings modal with System Status
- **Code Changes**:
  - `frontend/src/components/layout/Footer.tsx`: Status dots for Database, Redis, S3, Workers; fetches `/health` and `/api/jobs/workers/health`
  - `frontend/src/components/SettingsModal.tsx`: New modal with System Status section (API, Database, Redis, S3, Celery Workers)
  - `frontend/src/components/layout/RightSidebar.tsx`: Settings button opens Settings modal
- **Details**: Footer shows compact status indicators; Settings modal shows detailed component status for admins

## 2025-03-12 - Celery Worker Health Check (WO-12)

### :rocket: New Feature

- **Document**: [CELERY.md](../backend/CELERY.md)
- **Change**: Added worker monitoring and health check endpoint
- **Reason**: WO-12 - Set Up Celery Task Queue with Redis
- **Code Changes**:
  - `backend/app/routers/jobs.py`: Added `GET /api/jobs/workers/health` (celery inspect ping)
  - `backend/CELERY.md`: Documented worker monitoring, inspect commands
- **Details**: Health endpoint returns worker list when workers respond; use for monitoring probes

## 2025-03-12 - Repository Pattern Enhancements (WO-6)

### :rocket: New Feature

- **Document**: [REPOSITORY.md](./REPOSITORY.md)
- **Change**: Enhanced repository pattern with eager loading and exists()
- **Reason**: WO-6 - Implement Repository Pattern and ORM Layer
- **Code Changes**:
  - `backend/app/repositories/base.py`: Added `exists()`, `options` param to `get_by_id` and `list`
  - `backend/app/repositories/simulation.py`: Added `get_by_id_with_theory()`, `list_with_theory()` using selectinload
  - `backend/app/models/simulation.py`, `theory.py`: Added Relationship for Simulation.theory and Theory.simulations
- **Details**:
  - Eager loading via `selectinload` prevents N+1 queries when loading simulations with theory
  - `exists(id)` for lightweight existence checks
  - REPOSITORY.md documents patterns, DI, soft delete

## 2025-03-12 - Monitoring and Observability (WO-8)

### :rocket: New Feature

- **Document**: [MONITORING.md](./MONITORING.md)
- **Change**: Added monitoring and observability documentation
- **Reason**: WO-8 - Configure Monitoring and Observability
- **Code Changes**:
  - `backend/app/core/security.py`: Added `RequestLoggingMiddleware` (method, path, status, duration, request_id)
  - `backend/app/main.py`: Added `merge_contextvars` to structlog, registered `RequestLoggingMiddleware`
- **Details**:
  - Request logging middleware logs every HTTP request with structured fields
  - `request_id` bound to structlog context for request-scoped log correlation
  - Runbooks for health degraded/unhealthy, high error rate, high latency, rate limits
  - AWS CloudWatch, X-Ray, dashboards, and alarms setup guide (when deployed)
