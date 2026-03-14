"""WO-22: Multi-backend theory execution - CPU, MLX, JAX."""

from app.backends.base import BackendResult, TheoryBackend, get_available_backends
from app.backends.cpu import CPUBackend

__all__ = [
    "TheoryBackend",
    "BackendResult",
    "CPUBackend",
    "get_available_backends",
]
