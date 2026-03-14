"""WO-31: Tests for parameter grid generation."""

import numpy as np
import pytest

from app.grid import generate_1d, generate_2d, generate_3d, generate_grid


class TestGenerate1D:
    """AC-SCN-001.1: 1D grid with N points."""

    def test_linear(self) -> None:
        g = generate_1d(0.1, 0.5, 5, scale="linear")
        assert len(g) == 5
        np.testing.assert_allclose(g[0], 0.1)
        np.testing.assert_allclose(g[-1], 0.5)

    def test_log(self) -> None:
        g = generate_1d(0.1, 1.0, 5, scale="log")
        assert len(g) == 5
        assert g[0] > 0
        assert g[-1] == 1.0


class TestGenerate2D:
    """AC-SCN-001.2: 2D grid N×M."""

    def test_shape(self) -> None:
        g1, g2 = generate_2d((0.2, 0.4, 3), (70, 75, 4))
        assert g1.shape == (3, 4)
        assert g2.shape == (3, 4)


class TestGenerate3D:
    """AC-SCN-001.3: 3D grid N×M×P."""

    def test_shape(self) -> None:
        g1, g2, g3 = generate_3d((0.2, 0.4, 2), (70, 72, 2), (1.4, 1.5, 2))
        assert g1.shape == (2, 2, 2)
        assert g2.shape == (2, 2, 2)
        assert g3.shape == (2, 2, 2)


class TestGenerateGrid:
    """Unified grid API."""

    def test_1d_flat(self) -> None:
        names, flat, shape = generate_grid([
            ("omega_m", 0.2, 0.4, 5, "linear"),
        ])
        assert names == ["omega_m"]
        assert len(flat[0]) == 5
        assert list(shape) == [5]

    def test_2d_flat(self) -> None:
        names, flat, shape = generate_grid([
            ("omega_m", 0.2, 0.4, 3, "linear"),
            ("h0", 68, 72, 4, "linear"),
        ])
        assert names == ["omega_m", "h0"]
        assert len(flat[0]) == 12
        assert list(shape) == [3, 4]
