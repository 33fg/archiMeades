# Gravitational Physics Simulations Platform

[![CI](https://github.com/33fg/archiMeades/actions/workflows/ci.yml/badge.svg)](https://github.com/33fg/archiMeades/actions/workflows/ci.yml)
[![CD](https://github.com/33fg/archiMeades/actions/workflows/cd.yml/badge.svg)](https://github.com/33fg/archiMeades/actions/workflows/cd.yml)

Research platform for physicists to define gravitational theories, run GPU-accelerated simulations, compare with observational data, perform MCMC inference, and publish results.

**ArchiMeades** (named after Carver Mead) encompasses both **software** and **hardware**: the application, orchestration, and a dedicated **NVIDIA DGX GPU cluster** (16 nodes, scalable to 64, InfiniBand) for high-throughput MCMC, parameter scans, and simulations. The platform supports **GR and Newtonian models** (ΛCDM, N-body, post-Newtonian) plus alternative theories (G4v), and leverages **AI in unique ways**—contextual workflow guidance, intelligent job routing, provenance-aware lineage, and advanced use cases (anomaly detection in residuals, AI-guided parameter exploration).

**Repository**: [https://github.com/33fg/archiMeades](https://github.com/33fg/archiMeades)

**For experiments and publications**: See [docs/PLATFORM_DESCRIPTION.md](docs/PLATFORM_DESCRIPTION.md) for a formal platform description suitable for Methods sections, supplementary materials, and reproducibility statements.

## Tech Stack

- **Backend**: FastAPI, Python, SQLModel (PostgreSQL), PyTorch/JAX (GPU)
- **Frontend**: React + TypeScript + Vite, shadcn/ui, Tailwind CSS
- **Data**: Aurora PostgreSQL, Neo4j, S3
- **Infrastructure**: AWS (ECS Fargate, Cognito, ElastiCache Redis)
- **CI/CD**: GitHub Actions with blue-green deployment

## Project Structure

```
gravitational/
├── backend/          # FastAPI application
│   └── app/
│       ├── core/     # Config, database, exceptions
│       ├── models/   # SQLModel entities
│       └── routers/  # API routes
├── frontend/         # React + Vite + shadcn/ui
└── pyproject.toml    # Shared Python deps
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- pnpm or npm
- Docker (for Postgres, Redis, Neo4j, LocalStack S3)

**Local dev uses SQLite** (no PostgreSQL required). For production, use PostgreSQL.

### Full stack (recommended)

```bash
# Start all services (Postgres, Redis, Neo4j, LocalStack S3) and create S3 bucket
npm run services:start

# Start backend + frontend (S3 env vars set automatically)
npm run dev
```

Or one command: `npm run start:full`

### Backend

```bash
cd gravitational
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -e .

# Backend uses SQLite by default (see backend/.env)
# Run the API on port 8002 (frontend proxy expects this)
cd backend && uvicorn app.main:app --reload --port 8002
```

API: http://localhost:8002 | Docs: http://localhost:8002/docs

### Frontend

```bash
cd gravitational/frontend
npm install
npm run dev
```

Frontend: http://localhost:5173 (or 5174 if 5173 is taken)

The frontend proxies `/api` and `/health` to the backend—start both for full functionality.

For API integration patterns (useApi, query keys, mutations), see [docs/API_INTEGRATION.md](docs/API_INTEGRATION.md).

### Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for CD workflow, health checks, rollback, and troubleshooting.

### Authentication

See [docs/AUTH.md](docs/AUTH.md) for JWT validation, RBAC, and API endpoint protection patterns.

### Security

See [docs/SECURITY.md](docs/SECURITY.md) for rate limiting, security headers, and developer checklist.

### Migrations

See [docs/MIGRATIONS.md](docs/MIGRATIONS.md) for Alembic workflow, testing, and batching patterns.

### Planning: WO-51 Coordination

See [docs/WO-51-COORDINATION.md](docs/WO-51-COORDINATION.md) for the Physics & Numerics Library foundation strategy and migration path for WO-23, WO-24, WO-26.

### Celery (optional, for async jobs)

Requires Redis at `localhost:6379`. See `backend/CELERY.md` for details.

```bash
# From project root
./scripts/celery-worker.sh worker   # Worker only
./scripts/celery-worker.sh beat    # Beat scheduler only
./scripts/celery-worker.sh both    # Both (default)
```

## Work Order Phases

- **Phase 1**: Foundational setup (PostgreSQL, Neo4j, S3, FastAPI, AWS, Cognito, React)
- **Phase 2**: Core framework (Alembic, Repository pattern, auth, security, layout)
- **Phase 3**: Advanced integration (Celery/Redis, Amplify auth, state management)
- **Phase 4**: GPU job dispatch
- **Phase 5**: CI/CD pipeline
