"""DESI DR1 BGS (Bright Galaxy Sample) loader.

~5M bright galaxies in DR1, z < 0.6. Data from data.desi.lbl.gov.
Loads from local FITS path. See scripts/data-sources-catalog.md for download URLs.
"""

from pathlib import Path

import numpy as np

from app.datasets.observational_dataset import ObservationalDataset

DESI_BGS_CITATION = (
    "DESI Collaboration et al. 2025, Data Release 1 of the Dark Energy Spectroscopic "
    "Instrument, arXiv. See data.desi.lbl.gov/doc/acknowledgments/"
)

# Small sample URL for testing (~9.6 MB)
BGS_BRIGHT_SGC_SAMPLE_URL = (
    "https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/LSScats/v1.5/"
    "BGS_BRIGHT-21.5_SGC_clustering.dat.fits"
)


def _read_fits(path: Path | list[Path], max_rows: int | None = 5000):
    """Read DESI LSS FITS and return redshift, weight arrays. path can be single file or list to concatenate."""
    try:
        from astropy.io import fits
    except ImportError as e:
        raise ImportError(
            "astropy is required for DESI FITS. Install with: pip install astropy"
        ) from e

    paths = [path] if isinstance(path, Path) else path
    z_list, w_list = [], []
    for p in paths:
        with fits.open(p) as hdul:
            data = hdul[1].data
        z_col = "Z" if "Z" in data.columns.names else "REDSHIFT"
        w_col = "WEIGHT" if "WEIGHT" in data.columns.names else None
        z_list.append(np.asarray(data[z_col], dtype=np.float64))
        w_list.append(np.asarray(data[w_col], dtype=np.float64) if w_col else np.ones(len(z_list[-1])))
    z = np.concatenate(z_list)
    w = np.concatenate(w_list)
    if max_rows and len(z) > max_rows:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(z), max_rows, replace=False)
        z = z[idx]
        w = w[idx]
    return z, w


def load_desi_dr1_bgs(
    path: str | Path | list[str | Path] | None = None,
    use_cache: bool = True,
    max_rows: int | None = 5000,
) -> ObservationalDataset:
    """Load DESI DR1 BGS catalog.

    Args:
        path: Local path to FITS file (e.g. BGS_*_clustering.dat.fits).
              If None, uses cached sample in data/desi_dr1_bgs/.
        use_cache: If True and path is None, use cached file if present.
        max_rows: Subsample to this many galaxies (None = use all).

    Returns:
        ObservationalDataset with observable_type='galaxy_catalog'.
        observable = weight (for mass/completeness weighting).
    """
    if path is None:
        data_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "desi_dr1_bgs"
        data_dir.mkdir(parents=True, exist_ok=True)
        sample = data_dir / "BGS_BRIGHT-21.5_SGC_clustering.dat.fits"
        ngc = data_dir / "BGS_ANY_NGC_clustering.dat.fits"
        sgc = data_dir / "BGS_ANY_SGC_clustering.dat.fits"
        if sample.exists():
            paths = [sample]
        elif ngc.exists() and sgc.exists():
            paths = [ngc, sgc]  # full catalog
        elif ngc.exists():
            paths = [ngc]
        elif sgc.exists():
            paths = [sgc]
        else:
            raise FileNotFoundError(
                "DESI BGS file not found. Run: python scripts/download_galaxy_samples.py --desi [--full]"
            )
    else:
        paths = [Path(path)] if isinstance(path, (str, Path)) else [Path(p) for p in path]
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"DESI BGS path not found: {p}")

    z, w = _read_fits(paths, max_rows=max_rows)
    n = len(z)
    # observable = weight; stat_unc = small placeholder (galaxies are discrete)
    stat_unc = np.full(n, 0.01, dtype=np.float64)
    cov = np.eye(n, dtype=np.float64) * 0.01**2
    return ObservationalDataset(
        redshift=z,
        observable=w,
        statistical_uncertainty=stat_unc,
        systematic_covariance=cov,
        observable_type="galaxy_catalog",
        name="desi_dr1_bgs",
        citation=DESI_BGS_CITATION,
    )
