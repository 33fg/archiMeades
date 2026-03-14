"""WO-33: HDF5 scan result storage with gzip compression."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import h5py
import numpy as np

from app.grid import generate_grid

SCAN_STORAGE_DIR = Path(os.environ.get("SCAN_STORAGE_DIR", "data/scans"))


def _ensure_dir() -> Path:
    SCAN_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    return SCAN_STORAGE_DIR


def _axes_to_specs(axes_config: list[dict]) -> list[tuple[str, float, float, int, str]]:
    return [
        (a.get("name", ""), float(a.get("min", 0)), float(a.get("max", 1)), int(a.get("n", 1)), a.get("scale", "linear"))
        for a in axes_config
    ]


def save_scan_hdf5(
    scan_id: str,
    chi2: np.ndarray,
    shape: list[int],
    axes_config: list[dict],
    fixed_params: dict,
    theory_id: str,
    dataset_id: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Save scan results to HDF5 with gzip compression. Returns relative path."""
    base = _ensure_dir()
    path = base / f"{scan_id}.h5"

    with h5py.File(path, "w") as f:
        f.attrs["theory_id"] = theory_id
        f.attrs["dataset_id"] = dataset_id
        f.attrs["scan_id"] = scan_id
        f.attrs["axes_config"] = json.dumps(axes_config)
        f.attrs["fixed_params"] = json.dumps(fixed_params)
        if metadata:
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    f.attrs[k] = v

        f.create_dataset(
            "chi2",
            data=chi2.reshape(tuple(shape)),
            compression="gzip",
            compression_opts=4,
        )
        f.create_dataset("shape", data=np.array(shape, dtype=np.int64))

        # Store axis grid values for slice/profile
        specs = _axes_to_specs(axes_config)
        _, flat_arrays, _ = generate_grid(specs)
        axes_grp = f.create_group("axes")
        for i, arr in enumerate(flat_arrays):
            axes_grp.create_dataset(str(i), data=arr, compression="gzip")

    return str(path.relative_to(base))


def _axis_1d_values(flat_arrays: list[np.ndarray], shape: list[int], axis_idx: int) -> np.ndarray:
    """Extract 1D grid values for axis axis_idx from flat arrays."""
    stride = 1
    for j in range(axis_idx + 1, len(shape)):
        stride *= shape[j]
    return flat_arrays[axis_idx][::stride][: shape[axis_idx]].copy()


def load_scan_hdf5(scan_id: str) -> dict:
    """Load scan from HDF5. Path can be scan_id or relative path like 'xyz.h5'."""
    base = _ensure_dir()
    path = base / scan_id if scan_id.endswith(".h5") else base / f"{scan_id}.h5"
    if not path.exists():
        raise FileNotFoundError(f"Scan file not found: {path}")

    with h5py.File(path, "r") as f:
        chi2 = np.array(f["chi2"])
        shape = [int(x) for x in f["shape"][:]]
        theory_id = str(f.attrs.get("theory_id", ""))
        dataset_id = str(f.attrs.get("dataset_id", ""))
        axes_config = json.loads(f.attrs.get("axes_config", "[]"))
        fixed_params = json.loads(f.attrs.get("fixed_params", "{}"))
        flat_arrays = []
        for i in sorted(f["axes"].keys(), key=int):
            flat_arrays.append(np.array(f["axes"][i][:]))

    axis_1d = [_axis_1d_values(flat_arrays, shape, i) for i in range(len(shape))]

    return {
        "chi2": chi2,
        "shape": shape,
        "theory_id": theory_id,
        "dataset_id": dataset_id,
        "axes_config": axes_config,
        "flat_arrays": flat_arrays,
        "axis_1d": axis_1d,
        "fixed_params": fixed_params,
    }
