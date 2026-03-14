"""Simulation outputs API - list outputs, presigned download URLs.
WO-13: Implement GPU Job Dispatch and Monitoring
WO-47: Checksum verification on result loading (AC-PRV-001.4)
"""

import hashlib
from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.core.exceptions import ResourceNotFoundError
from app.repositories.simulation import SimulationOutputRepository
from app.services.s3 import generate_presigned_download_url, get_object
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/outputs", tags=["outputs"])


class OutputRead(BaseModel):
    id: str
    simulation_id: str
    s3_key: str
    file_size: int
    content_type: str | None
    checksum: str | None = None

    model_config = {"from_attributes": True}


class OutputVerifyRead(BaseModel):
    output_id: str
    verified: bool | None  # True=ok, False=modified, None=no checksum
    message: str


@router.get("", response_model=list[OutputRead])
async def list_outputs(
    simulation_id: str | None = Query(None, description="Filter by simulation ID"),
    session: AsyncSession = Depends(get_db),
):
    """List simulation outputs, optionally filtered by simulation_id."""
    repo = SimulationOutputRepository(session)
    if simulation_id:
        result = await repo.list(simulation_id=simulation_id, limit=100)
    else:
        result = await repo.list(limit=100, order_by="-created_at")
    return list(result)


@router.get("/{output_id}/download")
async def get_output_download(
    output_id: str,
    session: AsyncSession = Depends(get_db),
    redirect: bool = True,
):
    """Generate presigned S3 URL for output download. Redirects by default."""
    repo = SimulationOutputRepository(session)
    output = await repo.get_by_id(output_id)
    if output is None:
        raise ResourceNotFoundError("Output not found", detail={"output_id": output_id})
    url = generate_presigned_download_url(output.s3_key)
    if redirect:
        return RedirectResponse(url=url, status_code=302)
    return {"download_url": url}


@router.get("/{output_id}/verify", response_model=OutputVerifyRead)
async def verify_output(
    output_id: str,
    session: AsyncSession = Depends(get_db),
):
    """WO-47: Verify output checksum. Fetches from S3, computes SHA-256, compares to stored."""
    repo = SimulationOutputRepository(session)
    output = await repo.get_by_id(output_id)
    if output is None:
        raise ResourceNotFoundError("Output not found", detail={"output_id": output_id})
    if not output.checksum:
        return OutputVerifyRead(
            output_id=output_id,
            verified=None,
            message="No checksum stored — verification unavailable",
        )
    try:
        body = get_object(output.s3_key)
        computed = hashlib.sha256(body).hexdigest()
        verified = computed.lower() == output.checksum.lower()
        return OutputVerifyRead(
            output_id=output_id,
            verified=verified,
            message="File modified" if not verified else "Checksum verified",
        )
    except Exception as e:
        return OutputVerifyRead(
            output_id=output_id,
            verified=False,
            message=f"Verification failed: {e!s}",
        )
