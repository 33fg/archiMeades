"""WO-28: ObservationalDataset type - standard interface for all observational data.

REQ-DAT-001: Standard Dataset Type
AC-DAT-001.1: redshift, observable, statistical uncertainty, systematic covariance,
observable type, dataset name, citation metadata.
AC-DAT-001.2: Descriptive error when required fields missing.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

import numpy as np


REQUIRED_FIELDS = (
    "redshift",
    "observable",
    "statistical_uncertainty",
    "systematic_covariance",
    "observable_type",
    "name",
    "citation",
)


@dataclass
class ObservationalDataset:
    """Standard type for observational datasets. All likelihood/inference code accepts only this."""

    redshift: np.ndarray
    observable: np.ndarray
    statistical_uncertainty: np.ndarray
    systematic_covariance: np.ndarray
    observable_type: str
    name: str
    citation: str
    _cov_inv: np.ndarray | None = field(default=None, repr=False)
    _checksum: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self._validate()
        self._compute_checksum()

    def _validate(self) -> None:
        """AC-DAT-001.2: Raise descriptive error for missing/invalid fields."""
        missing: list[str] = []
        for f in REQUIRED_FIELDS:
            if not hasattr(self, f):
                missing.append(f)
                continue
            v = getattr(self, f)
            if v is None or (isinstance(v, (str, np.ndarray)) and (
                (isinstance(v, str) and v == "") or (isinstance(v, np.ndarray) and v.size == 0)
            )):
                missing.append(f)
        if missing:
            raise ValueError(
                f"ObservationalDataset missing required fields: {', '.join(missing)}. "
                "All of redshift, observable, statistical_uncertainty, systematic_covariance, "
                "observable_type, name, citation must be provided."
            )
        n = len(self.redshift)
        if len(self.observable) != n or len(self.statistical_uncertainty) != n:
            raise ValueError(
                f"Length mismatch: redshift={n}, observable={len(self.observable)}, "
                f"statistical_uncertainty={len(self.statistical_uncertainty)}"
            )
        if self.systematic_covariance.shape != (n, n):
            raise ValueError(
                f"systematic_covariance must be ({n}, {n}), got {self.systematic_covariance.shape}"
            )
        # AC-DAT-002.2: Total covariance (sys + diag(stat^2)) must be positive definite.
        # Systematic-only can be singular (e.g. Pantheon sys matrix); total is what we use.
        total = self.systematic_covariance.copy()
        np.fill_diagonal(total, np.diag(total) + self.statistical_uncertainty.astype(float) ** 2)
        try:
            np.linalg.cholesky(total)
        except np.linalg.LinAlgError as e:
            raise ValueError(
                f"Total covariance (systematic + diag(stat^2)) must be positive definite (Cholesky failed): {e}"
            ) from e

    def _compute_checksum(self) -> None:
        """Dataset checksum using SHA-256 of key arrays."""
        h = hashlib.sha256()
        h.update(self.redshift.tobytes())
        h.update(self.observable.tobytes())
        h.update(self.statistical_uncertainty.tobytes())
        h.update(self.systematic_covariance.tobytes())
        self._checksum = h.hexdigest()

    def _total_covariance(self) -> np.ndarray:
        """Total covariance = systematic + diag(statistical^2)."""
        C = self.systematic_covariance.copy()
        np.fill_diagonal(C, np.diag(C) + self.statistical_uncertainty.astype(float) ** 2)
        return C

    @property
    def cov_inv(self) -> np.ndarray:
        """AC-DAT-003.1: Covariance inverse (of total cov), computed and cached at load time."""
        if self._cov_inv is None:
            self._cov_inv = np.linalg.inv(self._total_covariance())
        return self._cov_inv

    def invalidate_cov_cache(self) -> None:
        """AC-DAT-003.3: Invalidate cached inverse when covariance is modified."""
        self._cov_inv = None

    @property
    def checksum(self) -> str:
        """SHA-256 checksum of dataset for integrity verification."""
        return self._checksum or ""

    @property
    def num_points(self) -> int:
        return len(self.redshift)
