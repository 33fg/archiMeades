"""WO-22: Unified theory execution interface across CPU, MLX, JAX backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class BackendResult:
    """Result from a single backend execution."""

    backend_name: str
    passed: bool
    outputs: dict[str, float]
    error: str | None = None


@dataclass
class TestCase:
    """Single test case for theory validation."""

    case_id: str
    params: dict[str, float]
    method: str  # luminosity_distance, age_of_universe, etc.


class TheoryBackend(ABC):
    """Abstract backend for theory execution."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend identifier (cpu, mlx, jax)."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend can run (dependencies installed, GPU available)."""
        ...

    @abstractmethod
    def execute(
        self,
        callables: dict[str, Any],
        test_cases: list[TestCase],
    ) -> BackendResult:
        """Run test cases using the backend. callables maps method name to callable."""
        ...


def get_available_backends() -> list[TheoryBackend]:
    """Return list of backends that are available."""
    from app.backends.cpu import CPUBackend

    backends: list[TheoryBackend] = [CPUBackend()]
    try:
        from app.backends.mlx_backend import MLXBackend

        if MLXBackend().is_available():
            backends.append(MLXBackend())
    except ImportError:
        pass
    try:
        from app.backends.jax_backend import JAXBackend

        if JAXBackend().is_available():
            backends.append(JAXBackend())
    except ImportError:
        pass
    return backends
