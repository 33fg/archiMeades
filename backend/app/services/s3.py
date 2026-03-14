"""S3 service - presigned URLs, upload/download/delete/list.
WO-4: Configure S3 Storage and Access Patterns
"""

import re
from typing import Literal

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import settings

# Key format: {prefix}/{resource_type}/{id}/{filename}
# Example: grav/simulations/abc123/output.h5, grav/jobs/abc123/checkpoint.json
KEY_PREFIX = "grav"
RESOURCE_TYPES = ("simulations", "observations", "inference", "jobs")
KEY_PATTERN = re.compile(
    rf"^{KEY_PREFIX}/({'|'.join(RESOURCE_TYPES)})/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$"
)
MAX_KEY_LENGTH = 512
ALLOWED_CONTENT_TYPES = {
    "application/octet-stream",
    "application/json",
    "text/csv",
    "application/x-hdf5",
    "application/x-hdf",
}


def _client():
    """Create boto3 S3 client. Uses aws_endpoint_url when set (e.g. LocalStack)."""
    kwargs = {
        "region_name": settings.aws_region,
        "config": BotoConfig(signature_version="s3v4"),
    }
    if settings.aws_endpoint_url:
        kwargs["endpoint_url"] = settings.aws_endpoint_url
    return boto3.client("s3", **kwargs)


def validate_key(key: str) -> bool:
    """Validate S3 key format and length."""
    return bool(KEY_PATTERN.match(key)) and len(key) <= MAX_KEY_LENGTH


def build_key(
    resource_type: Literal["simulations", "observations", "inference", "jobs"],
    resource_id: str,
    filename: str,
) -> str:
    """Build valid S3 key from components."""
    if not re.match(r"^[a-zA-Z0-9_.-]+$", filename):
        raise ValueError("Invalid filename characters")
    if resource_type not in RESOURCE_TYPES:
        raise ValueError(f"Invalid resource_type: {resource_type}")
    if not re.match(r"^[a-zA-Z0-9_-]+$", resource_id):
        raise ValueError("Invalid resource_id")
    return f"{KEY_PREFIX}/{resource_type}/{resource_id}/{filename}"


def generate_presigned_upload_url(
    key: str,
    content_type: str = "application/octet-stream",
    expires_in: int | None = None,
    max_file_size_mb: int = 100,
) -> str:
    """Generate presigned PUT URL for client upload."""
    if not validate_key(key):
        raise ValueError("Invalid S3 key")
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Content type not allowed: {content_type}")
    client = _client()
    params = {
        "Bucket": settings.s3_bucket,
        "Key": key,
        "ContentType": content_type,
    }
    conditions = [
        {"Content-Type": content_type},
        ["content-length-range", 0, max_file_size_mb * 1024 * 1024],
    ]
    url = client.generate_presigned_post(
        Bucket=settings.s3_bucket,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=conditions,
        ExpiresIn=expires_in or settings.s3_presigned_expiry,
    )
    # generate_presigned_post returns a dict with url and fields; for simple PUT use put_object
    return client.generate_presigned_url(
        "put_object",
        Params={**params, "ContentType": content_type},
        ExpiresIn=expires_in or settings.s3_presigned_expiry,
    )


def generate_presigned_download_url(
    key: str,
    expires_in: int | None = None,
) -> str:
    """Generate presigned GET URL for client download."""
    if not validate_key(key):
        raise ValueError("Invalid S3 key")
    client = _client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires_in or settings.s3_presigned_expiry,
    )


def delete_object(key: str) -> bool:
    """Delete object from S3. Returns True if deleted."""
    if not validate_key(key):
        raise ValueError("Invalid S3 key")
    try:
        _client().delete_object(Bucket=settings.s3_bucket, Key=key)
        return True
    except ClientError:
        return False


def get_object(key: str) -> bytes:
    """Fetch object from S3. Returns body bytes. Raises ClientError if not found."""
    if not validate_key(key):
        raise ValueError("Invalid S3 key")
    resp = _client().get_object(Bucket=settings.s3_bucket, Key=key)
    return resp["Body"].read()


def put_object(key: str, body: bytes, content_type: str = "application/octet-stream") -> None:
    """Upload bytes to S3 (server-side). Used by Celery workers."""
    if not validate_key(key):
        raise ValueError("Invalid S3 key")
    if content_type not in ALLOWED_CONTENT_TYPES:
        content_type = "application/octet-stream"
    _client().put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
    )


def list_objects(prefix: str, max_keys: int = 1000) -> list[dict]:
    """List objects under prefix. Returns list of {key, size} dicts."""
    if not prefix.startswith(f"{KEY_PREFIX}/") or len(prefix) > MAX_KEY_LENGTH:
        raise ValueError("Invalid prefix")
    client = _client()
    resp = client.list_objects_v2(
        Bucket=settings.s3_bucket,
        Prefix=prefix,
        MaxKeys=max_keys,
    )
    contents = resp.get("Contents") or []
    return [{"key": obj["Key"], "size": obj.get("Size", 0)} for obj in contents]
