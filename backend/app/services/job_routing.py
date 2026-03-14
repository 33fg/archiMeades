"""WO-38: Cost estimation and routing for compute jobs.
AC-JOB-001.1: Estimate computational cost (FLOPS, memory).
AC-JOB-001.2/.3: Route to DGX if cost > 10^11 FLOPS, else Mac GPU.
WO-68: Compute Dispatch - orchestrates WO-69 Simulation Engine execution.
"""

from typing import Any

from app.core.config import settings
from app.models.job import TargetBackend

# 10^11 FLOPS threshold - jobs above this route to DGX Spark
FLOPS_THRESHOLD = 1e11


def estimate_simulation_flops(n_points: int = 50) -> float:
    """WO-68: Estimate FLOPS for expansion simulation (WO-69).

    Per point: luminosity_distance integral ~1e5 FLOPS, cubic solve ~1e3.
    """
    flops_per_point = 1e5
    return n_points * flops_per_point


def estimate_mcmc_flops(
    num_samples: int,
    num_warmup: int,
    num_chains: int,
    num_params: int = 4,
) -> float:
    """Estimate FLOPS for NumPyro HMC-NUTS MCMC run.
    HMC: ~O(samples * warmup * params * likelihood_eval) per chain.
    Likelihood eval: ~O(n_data * params) for SN chi-squared.
    Approximate: 1e6 FLOPS per HMC step per param (includes grad, log_prob).
    """
    steps_per_chain = num_warmup + num_samples
    total_steps = steps_per_chain * num_chains
    flops_per_step = 1e6 * num_params  # heuristic: grad + log_prob + NUTS tree
    return total_steps * flops_per_step


def estimate_scan_flops(
    total_points: int,
    num_params: int = 4,
) -> float:
    """Estimate FLOPS for parameter grid scan.
    Chi-squared per point: ~O(n_data * params) ~ 1e5 FLOPS.
    """
    flops_per_point = 1e5 * num_params
    return total_points * flops_per_point


def estimate_theory_validation_flops() -> float:
    """Theory validation: lightweight, typically < threshold."""
    return 1e9  # ~1 GFLOP


def estimate_job_cost(job_type: str, params: dict[str, Any]) -> tuple[float, float]:
    """Estimate FLOPS and memory (MB) for a job.
    Returns (estimated_flops, estimated_memory_mb).
    """
    if job_type == "mcmc":
        flops = estimate_mcmc_flops(
            num_samples=params.get("num_samples", 1000),
            num_warmup=params.get("num_warmup", 500),
            num_chains=params.get("num_chains", 1),
            num_params=len(params.get("prior_spec", {})),
        )
        # Memory: chains * samples * params * 8 bytes
        n = (params.get("num_samples", 0) + params.get("num_warmup", 0)) * params.get("num_chains", 1)
        memory_mb = n * len(params.get("prior_spec", {})) * 8 / (1024 * 1024) if n else 10
    elif job_type == "scan":
        flops = estimate_scan_flops(
            total_points=params.get("total_points", 100),
            num_params=len(params.get("axes_config", [])) + len(params.get("fixed_params", {})),
        )
        memory_mb = params.get("total_points", 100) * 0.001  # ~1KB per point
    elif job_type == "theory_validation":
        flops = estimate_theory_validation_flops()
        memory_mb = 10
    elif job_type == "simulation":
        flops = estimate_simulation_flops(n_points=params.get("n_points", 50))
        memory_mb = 50  # ObservationalDataset output
    else:
        flops = 1e9
        memory_mb = 10
    return flops, memory_mb


def should_route_to_dgx(estimated_flops: float) -> bool:
    """AC-JOB-001.2: Route to DGX if cost > 10^11 FLOPS and DGX is configured."""
    if not settings.dgx_celery_queue:
        return False
    return estimated_flops >= FLOPS_THRESHOLD


def get_target_backend(estimated_flops: float) -> str:
    """AC-JOB-001.2/.3: Return mac_gpu or dgx_spark based on cost and availability."""
    if should_route_to_dgx(estimated_flops):
        return TargetBackend.DGX_SPARK
    return TargetBackend.MAC_GPU


def route_job(
    estimated_flops: float,
    estimated_memory_mb: float = 0,
) -> tuple[str, bool]:
    """Return (target_backend, dgx_unavailable_warning).
    AC-JOB-001.2: If cost > threshold but DGX not configured, warn and use Mac.
    """
    target = get_target_backend(estimated_flops)
    if estimated_flops >= FLOPS_THRESHOLD and not settings.dgx_celery_queue:
        return TargetBackend.MAC_GPU, True  # would prefer DGX but not available
    return target, False


