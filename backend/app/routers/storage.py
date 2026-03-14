"""Storage API - presigned URLs for S3 uploads and downloads.
WO-4: Configure S3 Storage and Access Patterns
"""

from typing import Literal

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user_required
from app.core.exceptions import ValidationError
from app.services import s3
from pydantic import BaseModel

router = APIRouter(prefix="/api/storage", tags=["storage"])


class UploadUrlRequest(BaseModel):
    """Request for presigned upload URL."""

    resource_type: Literal["simulations", "observations", "inference"]
    resource_id: str
    filename: str
    content_type: str = "application/octet-stream"
    max_file_size_mb: int = 100


class DownloadUrlRequest(BaseModel):
    """Request for presigned download URL."""

    key: str


@router.post("/upload-url")
async def get_upload_url(
    data: UploadUrlRequest,
    _user=Depends(get_current_user_required),
):
    """Generate presigned PUT URL for client upload."""
    if data.max_file_size_mb < 1 or data.max_file_size_mb > 500:
        raise ValidationError("max_file_size_mb must be between 1 and 500")
    try:
        key = s3.build_key(data.resource_type, data.resource_id, data.filename)
        url = s3.generate_presigned_upload_url(
            key,
            content_type=data.content_type,
            max_file_size_mb=data.max_file_size_mb,
        )
        return {"url": url, "key": key, "method": "PUT"}
    except ValueError as e:
        raise ValidationError(str(e))


@router.post("/download-url")
async def get_download_url(
    data: DownloadUrlRequest,
    _user=Depends(get_current_user_required),
):
    """Generate presigned GET URL for client download."""
    try:
        url = s3.generate_presigned_download_url(data.key)
        return {"url": url, "key": data.key, "method": "GET"}
    except ValueError as e:
        raise ValidationError(str(e))
