# ArchiMeades: Prose for Paper Inclusion

Copy-paste ready text for Methods sections and supplementary materials.

---

## Single Paragraph (Methods)

All simulations and Bayesian inference were performed using ArchiMeades, an integrated research platform for gravitational physics named after Carver Mead. ArchiMeades encompasses both software and dedicated hardware: a web-based application for theory definition, observational data management, and workflow orchestration, coupled with a 16-node NVIDIA DGX GPU cluster interconnected via InfiniBand. The platform supports GR-based (ΛCDM) and Newtonian models, plus alternative theories (G4v), and leverages AI in unique ways—including a contextual AI assistant, intelligent cost-based job routing, provenance-aware lineage, and advanced use cases such as anomaly detection in residuals and AI-guided parameter exploration—integrating AI into the core research workflow. Compute-intensive tasks—including Markov chain Monte Carlo (MCMC) sampling, parameter scans, and expansion simulations—are automatically routed to the cluster when estimated cost exceeds 10¹¹ FLOPS; lighter workloads execute on local CPU or Apple Silicon GPU. The platform implements ΛCDM and G4v expansion solvers, Newtonian and post-Newtonian dynamics for N-body simulations, supports the Pantheon supernova sample (1048 SNe Ia) and synthetic datasets, and provides MCMC via NumPyro (HMC-NUTS on JAX) and Emcee. Chains were exported in GetDist format and validated against Cobaya where applicable.

---

## Extended (Two Paragraphs, Methods)

All simulations and Bayesian inference were performed using ArchiMeades, an integrated research platform for gravitational physics named after Carver Mead. ArchiMeades encompasses both software and dedicated hardware: a web-based application for theory definition, observational data management, and workflow orchestration, coupled with a 16-node NVIDIA DGX GPU cluster (scalable to 64 nodes) interconnected via InfiniBand. The platform supports GR-based (ΛCDM) and Newtonian models, plus alternative theories (G4v), and leverages AI in unique ways—a contextual AI assistant, intelligent cost-based routing, provenance-aware lineage, and advanced use cases such as anomaly detection in residuals, AI-guided parameter exploration, and prior elicitation. Unlike shared HPC or cloud-pay-per-use setups, ArchiMeades provides dedicated GPU capacity: compute-intensive tasks—including MCMC sampling, parameter scans, and expansion simulations—are automatically dispatched when estimated cost exceeds 10¹¹ FLOPS, while lighter workloads run on local CPU or Apple Silicon GPU. The cluster is orchestrated via a heartbeat-based discovery system; Celery workers consume tasks from a dedicated queue, and cross-backend validation ensures numerical agreement (relative error < 10⁻⁸) between CPU, Mac GPU, and DGX.

The platform implements a theory engine with GR-based ΛCDM and Newtonian (plus post-Newtonian) expansion and dynamics solvers, cosmological distance computations (luminosity distance, angular diameter distance, distance modulus), and support for observational datasets including the Pantheon supernova sample (1048 SNe Ia) and synthetic test sets. MCMC sampling is provided via NumPyro (HMC-NUTS on JAX) and Emcee, with χ² likelihood and full covariance support. Publication export includes theory comparison tables (χ², Δχ²), LaTeX tables, and Hubble diagram figures. MCMC chains were exported in GetDist format and validated against Cobaya where applicable.

---

## Full Methods (Multi-Paragraph)

All simulations and Bayesian inference were performed using ArchiMeades, an integrated research platform for gravitational physics named after Carver Mead. ArchiMeades encompasses both software and dedicated hardware: a web-based application for theory definition, observational data management, and workflow orchestration, coupled with a 16-node NVIDIA DGX GPU cluster (scalable to 64 nodes) interconnected via InfiniBand. Unlike shared HPC or cloud-pay-per-use setups, ArchiMeades provides dedicated GPU capacity with intelligent job routing: compute-intensive tasks—including Markov chain Monte Carlo (MCMC) sampling, parameter scans, and expansion simulations—are automatically dispatched to the cluster when estimated cost exceeds 10¹¹ FLOPS, while lighter workloads run on local CPU or Apple Silicon GPU. The cluster is orchestrated via a heartbeat-based discovery system; Celery workers consume tasks from a dedicated queue, and cross-backend validation ensures numerical agreement (relative error < 10⁻⁸) between CPU, Mac GPU, and DGX.

The platform implements a theory engine supporting GR-based (ΛCDM) and Newtonian models, plus alternative theories such as G4v. Cosmological expansion uses Friedmann equations for ΛCDM and cubic field solvers for G4v; N-body simulations use Newtonian gravity with optional post-Newtonian corrections. The platform provides cosmological distance computations (luminosity distance, angular diameter distance, distance modulus), GR numerics (Christoffel symbols, geodesic acceleration), and support for observational datasets including the Pantheon supernova sample (1048 SNe Ia) and synthetic test sets. MCMC sampling is provided via NumPyro (HMC-NUTS on JAX) and Emcee, with χ² likelihood and full covariance support. Publication export includes theory comparison tables (χ², Δχ²), LaTeX tables, and Hubble diagram figures. MCMC chains were exported in GetDist format and validated against Cobaya where applicable.

ArchiMeades leverages AI in unique ways to accelerate gravitational physics research. A contextual AI assistant provides workflow-aware guidance; intelligent cost-based routing automatically dispatches compute-intensive work to the DGX cluster; and provenance stored in a graph database supports AI-assisted understanding of theory–simulation–observation–publication chains. The platform is designed to support advanced AI use cases that can meaningfully advance research: anomaly detection in residuals to flag systematic deviations that may indicate new physics; AI-guided parameter exploration to focus MCMC and scans on promising regions; and prior elicitation to translate physical intuition into prior distributions. These integrations distinguish ArchiMeades from conventional tools that treat AI as an add-on rather than a core part of the research workflow.

---

## Advanced AI Use Cases (for Supplementary or Future Work)

ArchiMeades is designed to support AI capabilities that can meaningfully advance gravitational physics research:

- **Anomaly detection in residuals**: Flag systematic deviations from theory predictions that may indicate new physics or unmodeled systematics.
- **AI-guided parameter exploration**: Bayesian optimization or surrogate-based methods to focus MCMC and scans on promising regions, reducing compute time.
- **Prior elicitation and consistency**: Translate physical intuition into priors; check consistency between priors, likelihood, and posterior.
- **Automated literature synthesis**: Ingest papers to extract constraints, priors, or dataset specs for comparison.
- **Natural language to theory specification**: Convert prose descriptions of theories into executable code or parameter specs.
- **Explanation generation**: Plain-language summaries of MCMC convergence, theory comparison, and residual patterns for Methods or supplementary materials.

---

## Software and Data Availability

All software and datasets are available at https://github.com/33fg/archiMeades. MCMC runs used NumPyro 0.15+, JAX 0.4+, and ArviZ 0.18+ for diagnostics.
