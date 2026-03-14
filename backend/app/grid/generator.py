"""WO-31: Multi-dimensional parameter grid generation.

REQ-SCN-001: 1D, 2D, 3D grids with linear and logarithmic spacing.
"""

from __future__ import annotations

from typing import Literal

import numpy as np

Scale = Literal["linear", "log"]


def _linspace(min_val: float, max_val: float, n: int, scale: Scale) -> np.ndarray:
    """Generate n points between min_val and max_val."""
    if scale == "log":
        if min_val <= 0 or max_val <= 0:
            raise ValueError("Log scale requires positive min and max")
        return np.logspace(np.log10(min_val), np.log10(max_val), n)
    return np.linspace(min_val, max_val, n)


def generate_1d(
    min_val: float,
    max_val: float,
    n: int,
    scale: Scale = "linear",
) -> np.ndarray:
    """Generate 1D grid. AC-SCN-001.1: N points."""
    return _linspace(min_val, max_val, n, scale)


def generate_2d(
    param1: tuple[float, float, int],
    param2: tuple[float, float, int],
    scale1: Scale = "linear",
    scale2: Scale = "linear",
) -> tuple[np.ndarray, np.ndarray]:
    """Generate 2D grid. AC-SCN-001.2: N×M points. Returns (grid1, grid2) 2D arrays."""
    min1, max1, n1 = param1
    min2, max2, n2 = param2
    g1 = _linspace(min1, max1, n1, scale1)
    g2 = _linspace(min2, max2, n2, scale2)
    gg1, gg2 = np.meshgrid(g1, g2, indexing="ij")
    return gg1, gg2


def generate_3d(
    param1: tuple[float, float, int],
    param2: tuple[float, float, int],
    param3: tuple[float, float, int],
    scale1: Scale = "linear",
    scale2: Scale = "linear",
    scale3: Scale = "linear",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate 3D grid. AC-SCN-001.3: N×M×P points."""
    min1, max1, n1 = param1
    min2, max2, n2 = param2
    min3, max3, n3 = param3
    g1 = _linspace(min1, max1, n1, scale1)
    g2 = _linspace(min2, max2, n2, scale2)
    g3 = _linspace(min3, max3, n3, scale3)
    gg1, gg2, gg3 = np.meshgrid(g1, g2, g3, indexing="ij")
    return gg1, gg2, gg3


def generate_grid(
    axes: list[tuple[str, float, float, int, Scale]],
) -> tuple[list[str], list[np.ndarray], np.ndarray]:
    """Generate N-dimensional grid from axis specs.

    Args:
        axes: List of (name, min, max, n, scale) for each axis.

    Returns:
        (param_names, flat_arrays_per_param, shape)
        flat_arrays_per_param[i] gives values for param i at each grid point (raveled).
    """
    if not axes:
        return [], [], np.array([])

    names = [a[0] for a in axes]
    grids = [
        _linspace(a[1], a[2], a[3], a[4]) for a in axes
    ]
    meshes = np.meshgrid(*grids, indexing="ij")
    shape = meshes[0].shape
    flat = [m.ravel() for m in meshes]
    return names, flat, np.array(shape)
