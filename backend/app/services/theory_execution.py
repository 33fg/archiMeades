"""Theory execution - compile code and run predictions.
WO-49: Theory Query and Observable Prediction Endpoints
"""

from dataclasses import dataclass
from typing import Any

# Planck 2020 defaults (AC-API-002.3)
DEFAULT_PARAMS = {
    "H0": 67.36,
    "Om": 0.315,
    "Ode": 0.6847,
    "Ob": 0.0493,
    "Or": 9.0e-5,
}


@dataclass
class ExecutionResult:
    """Result from theory execution."""

    values: list[float]
    backend: str = "cpu"
    precision: str = "float64"


def _compile_theory_code(code: str) -> dict[str, Any]:
    """Compile theory code and return callables. Raises if invalid."""
    namespace: dict[str, Any] = {}
    exec(compile(code, "<theory>", "exec"), namespace)
    return namespace


def get_callables(code: str) -> dict[str, Any]:
    """Extract callables from theory code. Returns dict of method_name -> callable."""
    ns = _compile_theory_code(code)
    result: dict[str, Any] = {}
    for name in ("luminosity_distance", "age_of_universe", "hubble_parameter"):
        fn = ns.get(name)
        if callable(fn):
            result[name] = fn
    return result


def has_observable(callables: dict[str, Any], observable: str) -> bool:
    """Check if theory supports the observable."""
    return observable in callables


def compute_luminosity_distance(
    code: str, redshifts: list[float], params: dict[str, float] | None = None
) -> ExecutionResult:
    """Compute luminosity distances in Mpc for given redshifts."""
    callables = get_callables(code)
    if "luminosity_distance" not in callables:
        raise ValueError("Theory does not support luminosity_distance")
    fn = callables["luminosity_distance"]
    p = {**DEFAULT_PARAMS, **(params or {})}
    values: list[float] = []
    for z in redshifts:
        try:
            # Support both fn(z) and fn(z, params) signatures
            import inspect
            sig = inspect.signature(fn)
            if len(sig.parameters) >= 2:
                v = float(fn(z, p))
            else:
                v = float(fn(z))
            values.append(v)
        except Exception as e:
            raise ValueError(f"luminosity_distance failed at z={z}: {e}") from e
    return ExecutionResult(values=values)


def compute_hubble_parameter(
    code: str, redshifts: list[float], params: dict[str, float] | None = None
) -> ExecutionResult:
    """Compute H(z) in km/s/Mpc for given redshifts."""
    callables = get_callables(code)
    if "hubble_parameter" not in callables:
        raise ValueError("Theory does not support hubble_parameter")
    fn = callables["hubble_parameter"]
    p = {**DEFAULT_PARAMS, **(params or {})}
    values: list[float] = []
    for z in redshifts:
        try:
            import inspect
            sig = inspect.signature(fn)
            if len(sig.parameters) >= 2:
                v = float(fn(z, p))
            else:
                v = float(fn(z))
            values.append(v)
        except Exception as e:
            raise ValueError(f"hubble_parameter failed at z={z}: {e}") from e
    return ExecutionResult(values=values)
