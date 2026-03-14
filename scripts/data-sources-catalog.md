# Galaxy Data Sources Catalog

Reference for observational galaxy catalogs used in the Gravitational Physics platform.

## DESI DR1 BGS (Bright Galaxy Sample)

| Property | Value |
|----------|-------|
| **Name** | DESI Data Release 1 – Bright Galaxy Sample |
| **Description** | ~5M bright galaxies in DR1, z < 0.6 |
| **Redshift range** | z < 0.6 |
| **Source** | data.desi.lbl.gov |
| **Formats** | FITS, LSS catalogs |
| **Data type** | Photometric / spectroscopic (BGS) |

### Access

- **Base URL**: https://data.desi.lbl.gov/public/dr1/
- **LSS clustering catalogs**: https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/LSScats/v1.5/
- **BGS clustering files** (recommended for cosmology):
  - `BGS_ANY_NGC_clustering.dat.fits` (~477 MB) – North Galactic Cap
  - `BGS_ANY_SGC_clustering.dat.fits` (~168 MB) – South Galactic Cap
  - Smaller subsets: `BGS_BRIGHT-21.5_NGC_clustering.dat.fits` (~25 MB), `BGS_BRIGHT-21.5_SGC_clustering.dat.fits` (~9.6 MB)

### Download

- **Web**: Browse and download individual files at the URLs above
- **Globus**: For large-scale transfers, use [DESI Globus](https://data.desi.lbl.gov/doc/access/)
- **Subset script**: `desi_get_dr_subset --dr dr1 --ra 56.0 --dec -9.0 --radius 0.1 --base-dir ./tiny_dr1` (note: small samples can still be ~40 GB)

### Citation

DESI Collaboration et al. (2025), Data Release 1 of the Dark Energy Spectroscopic Instrument. See [data.desi.lbl.gov/doc/acknowledgments/](https://data.desi.lbl.gov/doc/acknowledgments/).

---

## SDSS DR17 (MPA-JHU Stellar Masses)

| Property | Value |
|----------|-------|
| **Name** | SDSS Data Release 17 – MPA-JHU Galaxy Catalog |
| **Description** | ~800K galaxies with stellar mass estimates, z < 0.6 |
| **Redshift range** | z < 0.6 |
| **Source** | data.sdss.org |
| **Formats** | FITS, specObj |
| **Data type** | Spectroscopic with MPA-JHU stellar masses |

### Access

- **Base URL**: https://data.sdss.org/
- **MPA-JHU stellar masses**: https://www.sdss4.org/dr17/spectro/galaxy_mpajhu/
- **FITS files** (line-matched to specObj):
  - `galSpecInfo` (364 MB) – basic spectrum info
  - `galSpecExtra` (339 MB) – stellar mass and ancillary parameters
  - `galSpecLine` (1.7 GB) – line measurements
  - `galSpecIndx` (1.9 GB) – Lick indices

### Download

- **SAS**: Science Archive Server – https://data.sdss.org/sas/
- **SkyServer SQL**: https://skyserver.sdss.org/dr17/SearchTools/sql – query galaxies with redshift and join to MPA-JHU tables
- **rsync / wget**: Bulk download via SAS paths

### Notes

- MPA-JHU measurements are based on DR8 galaxy spectra (run2d=26)
- Unreliable measurements flagged with `RELIABLE=0`
- Catalog deprecated in favor of Wisconsin/Portsmouth/Granada analyses but provided in DR17 for comparison

### Citation

Brinchmann et al. (2004), Kauffmann et al. (2003), Tremonti et al. (2004). SDSS DR17: https://www.sdss4.org/dr17/

---

## Mass Weights

Both catalogs support **mass-weighted** analyses:

- **DESI BGS**: Use `WEIGHT` columns in LSS catalogs for fiber collision and completeness weights
- **SDSS MPA-JHU**: Use `MEDIAN_MASS` (log10 stellar mass in M☉) for mass weighting

## Download & storage

See **`scripts/DATA_DOWNLOAD_AND_STORAGE.md`** for:
- Full download commands and URLs
- Storage layout (`data/desi_dr1_bgs/`, `data/sdss_dr17/`)
- Disk requirements (~3.4 GB total)

## Integration

Loaders are available in `backend/app/datasets/loaders/`:

- `desi_dr1_bgs.py` – loads from local FITS path
- `sdss_dr17.py` – loads from local FITS path (galSpecExtra + optional specObj for redshifts)

**Quick start**: Run `python scripts/download_galaxy_samples.py --desi` for sample (~9.6 MB) or `--desi --full` for full catalog (~645 MB). See `scripts/DATA_DOWNLOAD_AND_STORAGE.md` for storage layout.

**Note**: Galaxy catalogs use `observable_type='galaxy_catalog'`. The Explore page plots redshift vs observable (weight or log stellar mass). MCMC/likelihood currently supports `distance_modulus` only; galaxy catalog support can be added in a future update.
