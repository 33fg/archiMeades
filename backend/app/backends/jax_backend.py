"""WO-22: JAX backend - DGX-1 GPU (optional)."""

from typing import Any

from app.backends.base import BackendResult, TestCase, TheoryBackend
from app.core.config import settings


class JAXBackend(TheoryBackend):
    """JAX-based GPU execution for DGX-1 cluster."""

    def __init__(self) -> None:
        self._dgx_host = settings.dgx_host

    @property
    def name(self) -> str:
        return "jax"

    def is_available(self) -> bool:
        try:
            import jax.numpy as jnp  # noqa: F401

            return True
        except ImportError:
            return False

    def execute(
        self,
        callables: dict[str, Any],
        test_cases: list[TestCase],
    ) -> BackendResult:
        """Run test cases on JAX. Uses CPU-style execution for cross-backend comparison."""
        outputs: dict[str, float] = {}
        for tc in test_cases:
            fn = callables.get(tc.method)
            if not fn:
                return BackendResult(
                    backend_name=self.name,
                    passed=False,
                    outputs={},
                    error=f"Missing callable for method {tc.method}",
                )
            try:
                if tc.method == "luminosity_distance":
                    z = tc.params.get("z", 0.1)
                    result = float(fn(z, tc.params))
                elif tc.method == "age_of_universe":
                    result = float(fn(tc.params))
                else:
                    result = float(fn(**tc.params))
                outputs[f"{tc.case_id}:{tc.method}"] = result
            except Exception as e:
                return BackendResult(
                    backend_name=self.name,
                    passed=False,
                    outputs=outputs,
                    error=f"{tc.case_id}: {e!s}",
                )
        return BackendResult(
            backend_name=self.name,
            passed=True,
            outputs=outputs,
        )
