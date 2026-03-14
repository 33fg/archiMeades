"""WO-28: Observational datasets - ObservationalDataset type and load_dataset.

REQ-DAT-004: Zero-modification extension - new loaders work with all inference tools.
WO-67: Support simulation-derived datasets (Observation with ObservationData).
"""

import json
import re

import numpy as np
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.datasets.loaders.pantheon import load_pantheon
from app.datasets.loaders.desi_dr1_bgs import load_desi_dr1_bgs
from app.datasets.loaders.sdss_dr17 import load_sdss_dr17
from app.datasets.observational_dataset import ObservationalDataset


def _load_synthetic(use_cache: bool = True) -> ObservationalDataset:
    """Minimal synthetic dataset for testing (diagonal cov, always loads)."""
    z = np.array([0.1, 0.2, 0.3, 0.5, 0.7])
    mu = 5 * np.log10(3000 * (1 + z)) + 25
    stat = np.full(5, 0.2)
    cov = np.eye(5) * 0.02**2
    return ObservationalDataset(
        redshift=z,
        observable=mu,
        statistical_uncertainty=stat,
        systematic_covariance=cov,
        observable_type="distance_modulus",
        name="synthetic",
        citation="Test dataset for likelihood",
    )


_REGISTRY: dict[str, object] = {
    "pantheon": load_pantheon,
    "synthetic": _load_synthetic,
    "desi_dr1_bgs": load_desi_dr1_bgs,
    "sdss_dr17_mpajhu": load_sdss_dr17,
}

BUILTIN_DATASET_NAMES: dict[str, str] = {
    "pantheon": "Pantheon (1048 SNe Ia)",
    "synthetic": "Synthetic (5 SNe, for testing)",
    "desi_dr1_bgs": "DESI DR1 BGS (~5M galaxies, 5K subsample)",
    "sdss_dr17_mpajhu": "SDSS DR17 MPA-JHU (~800K galaxies, stellar masses)",
}


def list_builtin_datasets() -> list[str]:
    """Return list of built-in dataset identifiers."""
    return sorted(_REGISTRY.keys())


# UUID pattern for Observation ids (WO-67)
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def _load_observation_dataset(observation_id: str) -> ObservationalDataset:
    """WO-67: Load dataset from ObservationData (simulation-derived or custom)."""
    from app.models.observation import ObservationData

    sync_url = settings.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")
    engine = create_engine(sync_url, connect_args={"check_same_thread": False} if "sqlite" in sync_url else {})
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        result = session.execute(
            select(ObservationData).where(ObservationData.observation_id == observation_id).limit(1)
        )
        od = result.scalars().first()
    if od is None:
        raise ValueError(f"Observation dataset '{observation_id}' not found")
    data = json.loads(od.values_json)
    return ObservationalDataset(
        redshift=np.array(data["redshift"], dtype=np.float64),
        observable=np.array(data["observable"], dtype=np.float64),
        statistical_uncertainty=np.array(data["statistical_uncertainty"], dtype=np.float64),
        systematic_covariance=np.array(data["systematic_covariance"], dtype=np.float64),
        observable_type=data.get("observable_type", "distance_modulus"),
        name=data.get("name", "Custom dataset"),
        citation=data.get("citation", ""),
    )


def load_dataset(name: str, **kwargs: object) -> ObservationalDataset:
    """Load dataset by name. AC-DAT-002.1: load_dataset('pantheon') returns 1048 SNe.
    WO-67: Also supports Observation ids (UUID) for simulation-derived datasets."""
    name_lower = name.lower().strip()
    if name_lower in _REGISTRY:
        loader = _REGISTRY[name_lower]
        return loader(**kwargs)
    if _UUID_RE.match(name.strip()):
        return _load_observation_dataset(name.strip())
    raise ValueError(
        f"Unknown dataset: '{name}'. Available: builtin ({', '.join(sorted(_REGISTRY))}) or Observation UUID"
    )


__all__ = ["ObservationalDataset", "load_dataset", "load_pantheon"]
