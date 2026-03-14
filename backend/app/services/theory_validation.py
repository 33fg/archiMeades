"""Theory interface validation - WO-21.
Checks that theory code defines required methods: luminosity_distance, age_of_universe, etc.
"""

import ast
from dataclasses import dataclass


REQUIRED_METHODS = frozenset({
    "luminosity_distance",
    "age_of_universe",
})


@dataclass
class ValidationResult:
    """Result of interface validation."""

    passed: bool
    missing_methods: list[str]
    errors: list[str]


def validate_theory_interface(code: str) -> ValidationResult:
    """Validate that theory code defines required methods. Uses AST parsing (no execution)."""
    missing = list(REQUIRED_METHODS)
    errors: list[str] = []

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return ValidationResult(
            passed=False,
            missing_methods=list(REQUIRED_METHODS),
            errors=[f"Syntax error at line {e.lineno}: {e.msg}"],
        )

    defined = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defined.add(node.name)

    for method in REQUIRED_METHODS:
        if method in defined:
            missing.remove(method)

    if missing:
        errors.append(f"Missing required methods: {', '.join(missing)}")

    return ValidationResult(
        passed=len(missing) == 0,
        missing_methods=missing,
        errors=errors,
    )
