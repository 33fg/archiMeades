"""WO-30: Chi-squared likelihood API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.datasets import load_dataset
from app.likelihood import compute_chi_squared, compute_joint_chi_squared

router = APIRouter(prefix="/api/likelihood", tags=["likelihood"])


class EvaluateRequest(BaseModel):
    theory_id: str
    dataset_id: str
    omega_m: float = 0.31
    i_rel: float = 1.451782
    h0: float = 70.0


class JointRequest(BaseModel):
    theory_id: str
    dataset_ids: list[str]
    omega_m: float = 0.31
    i_rel: float = 1.451782
    h0: float = 70.0


def _eval_request(
    theory_id: str,
    dataset_ids: list[str],
    omega_m: float = 0.31,
    i_rel: float = 1.451782,
    h0: float = 70.0,
) -> float:
    """Load datasets and compute chi-squared."""
    datasets = []
    for ds_id in dataset_ids:
        try:
            ds = load_dataset(ds_id)
        except Exception as e:
            raise HTTPException(422, f"Failed to load dataset '{ds_id}': {e}") from e
        datasets.append(ds)

    if len(datasets) == 1:
        return compute_chi_squared(
            datasets[0], theory_id, omega_m=omega_m, i_rel=i_rel, h0=h0
        )
    return compute_joint_chi_squared(
        datasets, theory_id, omega_m=omega_m, i_rel=i_rel, h0=h0
    )


@router.post("/evaluate")
def evaluate_likelihood(body: EvaluateRequest):
    """Compute χ² for theory vs dataset.

    AC-LIK-001: χ² = Δμᵀ C⁻¹ Δμ.
    Returns Inf for unphysical parameters.
    """
    chi2 = _eval_request(
        theory_id=body.theory_id,
        dataset_ids=[body.dataset_id],
        omega_m=body.omega_m,
        i_rel=body.i_rel,
        h0=body.h0,
    )
    return {
        "chi_squared": chi2,
        "theory_id": body.theory_id,
        "dataset_id": body.dataset_id,
    }


@router.post("/joint")
def joint_likelihood(body: JointRequest):
    """Compute joint χ² = Σ χ²_i across datasets.

    AC-LIK-004: Joint likelihood.
    """
    if not body.dataset_ids:
        raise HTTPException(422, "dataset_ids must be non-empty")
    chi2 = _eval_request(
        theory_id=body.theory_id,
        dataset_ids=body.dataset_ids,
        omega_m=body.omega_m,
        i_rel=body.i_rel,
        h0=body.h0,
    )
    return {
        "chi_squared": chi2,
        "theory_id": body.theory_id,
        "dataset_ids": body.dataset_ids,
    }
