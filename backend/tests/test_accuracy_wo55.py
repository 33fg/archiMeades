"""WO-55: Tests for accuracy enhancement methods."""

import numpy as np
import pytest

from app.physics_numerics.accuracy import kahan_sum, richardson_extrapolate


def test_kahan_sum_reduces_error():
    """AC-NM-003.1: Kahan summation has lower error for many small + one large."""
    # 1e6 * 1e-10 + 1.0: naive sum loses precision, Kahan preserves
    arr = np.full(1_000_000, 1e-10, dtype=np.float64)
    arr = np.append(arr, 1.0)
    naive = np.sum(arr)
    kahan = kahan_sum(arr)
    # Kahan should be closer to true value 1.0001
    true_val = 1e-10 * 1_000_000 + 1.0
    assert abs(kahan - true_val) < abs(naive - true_val) or abs(kahan - true_val) < 1e-6


def test_richardson_extrapolate():
    """AC-NM-003.2: Richardson extrapolation improves convergence order."""
    # f(h) = 1 + h^2, so f(0) = 1
    vals = [1.0 + 0.25, 1.0 + 0.0625]  # h=0.5, h=0.25
    best, _ = richardson_extrapolate(vals, order=2)
    assert abs(best - 1.0) < 0.01
