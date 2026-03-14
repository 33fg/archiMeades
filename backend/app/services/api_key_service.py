"""API key generation and hashing.
WO-48: API Authentication and Rate Limiting Infrastructure
"""

import hashlib
import secrets
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class GeneratedKey:
    """Raw key (shown once) and its hash for storage."""

    raw_key: str
    key_hash: str


def generate_api_key() -> GeneratedKey:
    """Generate API key: grav_ + 32 bytes hex. SHA-256 hash for storage."""
    raw = "grav_" + secrets.token_hex(32)
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    return GeneratedKey(raw_key=raw, key_hash=key_hash)


def hash_api_key(raw_key: str) -> str:
    """Hash raw API key for lookup."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def is_api_key_format(token: str) -> bool:
    """True if token looks like API key (grav_ + hex), not JWT."""
    if not token or len(token) < 10:
        return False
    # JWT has 3 base64 parts separated by dots
    if "." in token:
        return False
    return token.startswith("grav_") and len(token) == 5 + 64
