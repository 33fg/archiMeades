"""WO-28: Tests for ObservationalDataset and Pantheon loader."""

import numpy as np
import pytest

from app.datasets import ObservationalDataset, load_dataset, load_pantheon


def test_observational_dataset_validation() -> None:
    """AC-DAT-001.2: Missing required fields raise descriptive error."""
    n = 5
    z = np.linspace(0.1, 1.0, n)
    obs = np.ones(n)
    stat = np.ones(n) * 0.1
    cov = np.eye(n) + 0.01  # ensure PD

    with pytest.raises(ValueError, match="missing required fields"):
        ObservationalDataset(
            redshift=z,
            observable=obs,
            statistical_uncertainty=stat,
            systematic_covariance=cov,
            observable_type="x",
            name="test",
            citation="",  # missing
        )


def test_observational_dataset_cov_inv_cache() -> None:
    """AC-DAT-003.1, AC-DAT-003.3: Covariance inverse cached and invalidatable."""
    n = 4
    z = np.linspace(0.1, 0.5, n)
    obs = np.ones(n)
    stat = np.ones(n) * 0.1
    cov = np.eye(n) * 2 + 0.1

    ds = ObservationalDataset(
        redshift=z,
        observable=obs,
        statistical_uncertainty=stat,
        systematic_covariance=cov,
        observable_type="x",
        name="test",
        citation="Test 2024",
    )
    inv1 = ds.cov_inv
    inv2 = ds.cov_inv
    np.testing.assert_array_equal(inv1, inv2)
    ds.invalidate_cov_cache()
    inv3 = ds.cov_inv
    np.testing.assert_array_equal(inv1, inv3)


def test_load_dataset_unknown() -> None:
    """Unknown dataset raises ValueError."""
    with pytest.raises(ValueError, match="Unknown dataset"):
        load_dataset("nonexistent")


@pytest.mark.skip(reason="Requires network - run manually or in CI with fetch")
def test_load_pantheon() -> None:
    """AC-DAT-002.1, AC-DAT-002.2, AC-DAT-002.3, AC-DAT-002.4."""
    ds = load_pantheon(use_cache=False)
    assert ds.num_points == 1048
    assert ds.name == "pantheon"
    assert "Scolnic" in ds.citation
    assert ds.observable_type == "distance_modulus"
    assert np.all(ds.redshift >= 0.01) and np.all(ds.redshift <= 2.3)
    assert ds.systematic_covariance.shape == (1048, 1048)
    # Cholesky should succeed (AC-DAT-002.2)
    total_cov = ds.systematic_covariance + np.diag(ds.statistical_uncertainty**2)
    np.linalg.cholesky(total_cov)
