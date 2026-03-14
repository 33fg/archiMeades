"""WO-31: Tests for scan runner."""

import numpy as np
import pytest

from app.scans.runner import run_scan


class TestRunScan:
    """AC-SCN-001: Grid evaluation."""

    def test_1d_omega_m(self) -> None:
        """AC-SCN-001.1: 1D scan returns 1D chi2 array."""
        chi2, shape = run_scan(
            theory_id="lcdm",
            dataset_id="synthetic",
            axes_config=[{"name": "omega_m", "min": 0.25, "max": 0.35, "n": 5, "scale": "linear"}],
            fixed_params={"h0": 70},
        )
        assert len(chi2) == 5
        assert list(shape) == [5]
        assert np.all(np.isfinite(chi2) | np.isinf(chi2))

    def test_2d_omega_m_h0(self) -> None:
        """AC-SCN-001.2: 2D scan returns 2D shape."""
        chi2, shape = run_scan(
            theory_id="lcdm",
            dataset_id="synthetic",
            axes_config=[
                {"name": "omega_m", "min": 0.28, "max": 0.32, "n": 3, "scale": "linear"},
                {"name": "h0", "min": 68, "max": 72, "n": 4, "scale": "linear"},
            ],
        )
        assert len(chi2) == 12
        assert list(shape) == [3, 4]

    def test_ac_scn_001_4_unphysical_inf(self) -> None:
        """AC-SCN-001.4: Unphysical params => Inf, continue."""
        # G4v at high z yields inf - scan should continue
        chi2, _ = run_scan(
            theory_id="g4v",
            dataset_id="synthetic",
            axes_config=[{"name": "omega_m", "min": 0.3, "max": 0.32, "n": 3, "scale": "linear"}],
        )
        assert len(chi2) == 3
        # G4v may return inf for synthetic redshifts
        assert np.all(np.isinf(chi2) | np.isfinite(chi2))

    def test_parallel_scan_80_points(self) -> None:
        """WO-32: Scan with >=64 points uses parallel batch path."""
        chi2, shape = run_scan(
            theory_id="lcdm",
            dataset_id="synthetic",
            axes_config=[
                {"name": "omega_m", "min": 0.28, "max": 0.34, "n": 8, "scale": "linear"},
                {"name": "h0", "min": 68, "max": 72, "n": 10, "scale": "linear"},
            ],
        )
        assert len(chi2) == 80
        assert list(shape) == [8, 10]
        assert np.all(np.isfinite(chi2))
