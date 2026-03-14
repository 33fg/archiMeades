"""WO-34: NumPyro MCMC API - POST /api/mcmc/runs."""

from typing import Any

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/mcmc", tags=["mcmc"])


class PriorSpec(BaseModel):
    type: str  # uniform, normal, log_normal
    low: float | None = None
    high: float | None = None
    mean: float | None = None
    std: float | None = None


class CreateMCMCRunRequest(BaseModel):
    theory_id: str
    dataset_id: str
    prior_spec: dict[str, dict[str, Any]]
    num_samples: int = 1000
    num_warmup: int = 500
    num_chains: int = 1
    sampler: str = "numpyro"  # numpyro | emcee


@router.post("/runs")
async def create_mcmc_run(body: CreateMCMCRunRequest) -> dict[str, Any]:
    """Submit MCMC run. sampler: numpyro (HMC-NUTS) or emcee (gradient-free)."""
    if body.sampler not in ("numpyro", "emcee"):
        raise HTTPException(422, "sampler must be 'numpyro' or 'emcee'")

    try:
        from app.mcmc.sampler import run_mcmc
    except ImportError as e:
        raise HTTPException(
            503,
            "MCMC requires JAX and NumPyro. Run: uv sync '.[numpyro]' or npm run sync",
        ) from e

    if body.sampler == "emcee":
        try:
            import emcee  # noqa: F401
        except ImportError:
            raise HTTPException(
                503,
                "Emcee sampler requires emcee. Run: uv sync '.[emcee]'",
            ) from None

    try:
        result = run_mcmc(
            theory_id=body.theory_id,
            dataset_id=body.dataset_id,
            prior_spec=body.prior_spec,
            num_samples=body.num_samples,
            num_warmup=body.num_warmup,
            num_chains=body.num_chains,
            sampler=body.sampler,
        )
        # WO-36: GetDist-compatible export
        from app.mcmc.getdist_export import export_getdist_to_strings
        chains_txt, paramnames_txt = export_getdist_to_strings(
            result["posterior_samples"], result["param_names"]
        )
        return {
            "status": "completed",
            "posterior_samples": result["posterior_samples"],
            "param_names": result["param_names"],
            "num_samples": result["num_samples"],
            "num_warmup": result["num_warmup"],
            "num_chains": result["num_chains"],
            "diagnostics": result.get("diagnostics"),
            "getdist": {"chains_txt": chains_txt, "paramnames_txt": paramnames_txt},
        }
    except ImportError as e:
        raise HTTPException(
            503,
            f"MCMC requires JAX and NumPyro: {e}. Run: uv sync '.[numpyro]' or npm run sync",
        ) from e
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    except Exception as e:
        structlog.get_logger().exception("MCMC run failed", error=str(e))
        raise HTTPException(500, str(e)) from e
