"""SDSS DR17 MPA-JHU galaxy catalog loader.

~800K galaxies with stellar masses, z < 0.6. Data from data.sdss.org.
Loads from local FITS path. See scripts/data-sources-catalog.md for download URLs.
"""

from pathlib import Path

import numpy as np

from app.datasets.observational_dataset import ObservationalDataset

SDSS_MPAJHU_CITATION = (
    "Brinchmann et al. 2004, Kauffmann et al. 2003, Tremonti et al. 2004. "
    "SDSS DR17 MPA-JHU stellar masses. https://www.sdss4.org/dr17/"
)


def _read_fits(
    path: Path,
    specobj_path: Path | None = None,
    max_rows: int | None = 5000,
) -> tuple[np.ndarray, np.ndarray]:
    """Read SDSS/MPA-JHU FITS and return redshift, log10(stellar mass).

    galSpecExtra is line-by-line matched to specObj; redshift comes from specObj.
    If path has both Z and mass columns (merged file), specobj_path is ignored.
    """
    try:
        from astropy.io import fits
    except ImportError as e:
        raise ImportError(
            "astropy is required for SDSS FITS. Install with: pip install astropy"
        ) from e

    with fits.open(path) as hdul:
        data = hdul[1].data
    names = [c.upper() for c in data.columns.names]
    mass_col = "LGM_TOT_P50" if "LGM_TOT_P50" in names else "MEDIAN_MASS" if "MEDIAN_MASS" in names else next(
        (c for c in names if "MASS" in c or "LOGMASS" in c), None
    )
    z_col = "Z" if "Z" in names else next((c for c in names if "REDSHIFT" in c), None)

    if z_col:
        z = np.asarray(data[z_col], dtype=np.float64)
    elif specobj_path and specobj_path.exists():
        with fits.open(specobj_path) as h:
            z = np.asarray(h[1].data["Z"], dtype=np.float64)
        if len(z) != len(data):
            raise ValueError("specObj and galSpecExtra row count mismatch")
    else:
        raise ValueError("No redshift column and no specObj path provided")

    mass = np.asarray(data[mass_col], dtype=np.float64) if mass_col else np.ones_like(z)
    valid = np.isfinite(z) & (z > 0) & (z < 2)
    if mass_col:
        valid &= np.isfinite(mass) & (mass > 0)
    z = z[valid]
    mass = mass[valid]
    if max_rows and len(z) > max_rows:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(z), max_rows, replace=False)
        z = z[idx]
        mass = mass[idx]
    return z, mass


def load_sdss_dr17(
    path: str | Path | None = None,
    specobj_path: str | Path | None = None,
    use_cache: bool = True,
    max_rows: int | None = 5000,
) -> ObservationalDataset:
    """Load SDSS DR17 MPA-JHU galaxy catalog.

    Args:
        path: Local path to galSpecExtra FITS (or merged file with Z+mass).
        specobj_path: If path is galSpecExtra only, path to specObj for redshifts.
        use_cache: If True and path is None, use cached file if present.
        max_rows: Subsample to this many galaxies (None = use all).

    Returns:
        ObservationalDataset with observable_type='galaxy_catalog'.
        observable = log10(stellar mass / M_sun).
    """
    if path is None:
        data_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "sdss_dr17"
        data_dir.mkdir(parents=True, exist_ok=True)
        # SAS uses galSpecExtra-dr8.fits; also check galSpecExtra.fits
        fpath = data_dir / "galSpecExtra-dr8.fits"
        if not fpath.exists():
            fpath = data_dir / "galSpecExtra.fits"
        spath = data_dir / "specObj-dr8.fits"
        if not fpath.exists():
            raise FileNotFoundError(
                f"SDSS MPA-JHU file not found. Run: python scripts/download_galaxy_samples.py --sdss\n"
                "  Downloads galSpecExtra-dr8.fits and specObj-dr8.fits to data/sdss_dr17/"
            )
        path = fpath
        specobj_path = spath if spath.exists() else None
    else:
        path = Path(path)
        specobj_path = Path(specobj_path) if specobj_path else None
    if not path.exists():
        raise FileNotFoundError(f"SDSS path not found: {path}")

    z, mass = _read_fits(path, specobj_path=specobj_path, max_rows=max_rows)
    n = len(z)
    stat_unc = np.full(n, 0.1, dtype=np.float64)  # ~0.1 dex typical for stellar mass
    cov = np.eye(n, dtype=np.float64) * 0.1**2
    return ObservationalDataset(
        redshift=z,
        observable=mass,
        statistical_uncertainty=stat_unc,
        systematic_covariance=cov,
        observable_type="galaxy_catalog",
        name="sdss_dr17_mpajhu",
        citation=SDSS_MPAJHU_CITATION,
    )
