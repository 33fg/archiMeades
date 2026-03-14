"""WO-22: Multi-backend validation - run theory on CPU/MLX/JAX, compare results."""

from dataclasses import dataclass

from app.backends.base import BackendResult, TestCase, TheoryBackend, get_available_backends

ERROR_THRESHOLD = 1e-8


@dataclass
class ValidationComparison:
    """Result of cross-backend comparison."""

    passed: bool
    backend_results: dict[str, BackendResult]
    failures: list[dict]
    cpu_outputs: dict[str, float]


def _relative_error(a: float, b: float) -> float:
    """|a - b| / |b|, or 0 if b is 0."""
    if abs(b) < 1e-300:
        return 0.0 if abs(a) < 1e-300 else float("inf")
    return abs(a - b) / abs(b)


def compare_backend_results(
    results: list[BackendResult],
    cpu_result: BackendResult | None,
) -> ValidationComparison:
    """Compare all backend results against CPU reference. Threshold 1e-8."""
    by_name = {r.backend_name: r for r in results}
    cpu_outputs = cpu_result.outputs if cpu_result else {}
    failures: list[dict] = []

    for backend_name, result in by_name.items():
        if backend_name == "cpu":
            continue
        if not result.passed:
            failures.append(
                {
                    "backend": backend_name,
                    "error": result.error,
                    "type": "execution_failed",
                }
            )
            continue
        for key, value in result.outputs.items():
            cpu_val = cpu_outputs.get(key)
            if cpu_val is None:
                continue
            err = _relative_error(value, cpu_val)
            if err > ERROR_THRESHOLD:
                failures.append(
                    {
                        "backend": backend_name,
                        "test_case": key,
                        "cpu_value": cpu_val,
                        "backend_value": value,
                        "relative_error": err,
                        "threshold": ERROR_THRESHOLD,
                    }
                )

    passed = len(failures) == 0 and (cpu_result is None or cpu_result.passed)
    return ValidationComparison(
        passed=passed,
        backend_results=by_name,
        failures=failures,
        cpu_outputs=cpu_outputs,
    )


def run_multi_backend_validation(
    callables: dict[str, object],
    test_cases: list[TestCase],
    backends: list[TheoryBackend] | None = None,
) -> ValidationComparison:
    """Run validation across all available backends and compare to CPU."""
    if backends is None:
        backends = get_available_backends()
    if not backends:
        return ValidationComparison(
            passed=False,
            backend_results={},
            failures=[{"error": "No backends available"}],
            cpu_outputs={},
        )

    results: list[BackendResult] = []
    for backend in backends:
        if not backend.is_available():
            continue
        result = backend.execute(callables, test_cases)
        results.append(result)

    cpu_result = next((r for r in results if r.backend_name == "cpu"), None)
    return compare_backend_results(results, cpu_result)


def generate_test_cases(n: int = 100) -> list[TestCase]:
    """Generate n test cases for validation (WO-22: 100 test cases)."""
    import numpy as np

    cases: list[TestCase] = []
    np.random.seed(42)
    for i in range(n):
        z = float(np.random.uniform(0.01, 2.0))
        H0 = float(np.random.uniform(60, 80))
        Om = float(np.random.uniform(0.2, 0.4))
        params = {"z": z, "H0": H0, "Om": Om}
        cases.append(TestCase(case_id=f"tc_{i:03d}", params=params, method="luminosity_distance"))
        cases.append(TestCase(case_id=f"tc_{i:03d}", params=params, method="age_of_universe"))
    return cases
