"""WO-33: Tests for HDF5 scan storage."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from app.scans.storage import load_scan_hdf5, save_scan_hdf5


@pytest.fixture
def tmp_storage(monkeypatch):
    """Use temp dir for scan storage."""
    with tempfile.TemporaryDirectory() as d:
        monkeypatch.setenv("SCAN_STORAGE_DIR", d)
        yield d


def test_save_load_2d_scan(tmp_storage) -> None:
    """Save and load 2D scan result."""
    scan_id = "test-scan-123"
    chi2 = np.random.rand(4, 5).astype(np.float64)
    shape = [4, 5]
    axes_config = [
        {"name": "omega_m", "min": 0.28, "max": 0.32, "n": 4, "scale": "linear"},
        {"name": "h0", "min": 68, "max": 72, "n": 5, "scale": "linear"},
    ]
    fixed_params = {"i_rel": 1.45}
    rel_path = save_scan_hdf5(
        scan_id, chi2, shape, axes_config, fixed_params,
        "lcdm", "synthetic",
    )
    assert rel_path.endswith(".h5")

    data = load_scan_hdf5(scan_id)
    assert np.allclose(data["chi2"], chi2)
    assert data["shape"] == shape
    assert data["theory_id"] == "lcdm"
    assert data["dataset_id"] == "synthetic"
    assert len(data["axis_1d"]) == 2
    assert len(data["axis_1d"][0]) == 4
    assert len(data["axis_1d"][1]) == 5
