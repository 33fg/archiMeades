# Galaxy Data: Download and Storage Guide

How to download and store the full DESI DR1 BGS and SDSS DR17 catalogs.

## Storage Layout

All data lives under `data/` at the project root:

```
data/
├── desi_dr1_bgs/           # DESI BGS catalogs
│   ├── BGS_ANY_NGC_clustering.dat.fits   (~477 MB)
│   └── BGS_ANY_SGC_clustering.dat.fits   (~168 MB)
└── sdss_dr17/             # SDSS MPA-JHU catalogs
    ├── galSpecExtra-dr8.fits              (~340 MB)
    └── specObj-dr8.fits                    (~2.4 GB, for redshifts)
```

**Total disk required**: ~3.4 GB

---

## DESI DR1 BGS (Full ~5M galaxies)

### Files to download

| File | Size | Description |
|------|------|-------------|
| BGS_ANY_NGC_clustering.dat.fits | ~477 MB | North Galactic Cap |
| BGS_ANY_SGC_clustering.dat.fits | ~168 MB | South Galactic Cap |

### Download options

**Option 1: Script (recommended)**
```bash
python scripts/download_galaxy_samples.py --desi --full
```

**Option 2: wget**
```bash
mkdir -p data/desi_dr1_bgs
cd data/desi_dr1_bgs
wget https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/LSScats/v1.5/BGS_ANY_NGC_clustering.dat.fits
wget https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/LSScats/v1.5/BGS_ANY_SGC_clustering.dat.fits
```

**Option 3: Globus** (for large-scale or institutional transfers)
- DESI Globus: https://data.desi.lbl.gov/doc/access/
- Transfer to your machine or cluster

---

## SDSS DR17 MPA-JHU (Full ~800K galaxies)

### Files to download

| File | Size | Description |
|------|------|-------------|
| galSpecExtra-dr8.fits | ~340 MB | Stellar masses (line-matched to specObj) |
| specObj-dr8.fits | ~2.4 GB | Redshifts and spectrum metadata |

Both are required: galSpecExtra has masses, specObj has redshifts. They are line-by-line matched.

### Download options

**Option 1: Script (recommended)**
```bash
python scripts/download_galaxy_samples.py --sdss --full
```

**Option 2: wget**
```bash
mkdir -p data/sdss_dr17
cd data/sdss_dr17
wget https://data.sdss.org/sas/dr8/sdss/spectro/redux/galSpecExtra-dr8.fits
wget https://data.sdss.org/sas/dr8/sdss/spectro/redux/specObj-dr8.fits
```

**Option 3: rsync** (resumable)
```bash
mkdir -p data/sdss_dr17
rsync -avz --progress rsync://data.sdss.org/sas/dr8/sdss/spectro/redux/galSpecExtra-dr8.fits data/sdss_dr17/
rsync -avz --progress rsync://data.sdss.org/sas/dr8/sdss/spectro/redux/specObj-dr8.fits data/sdss_dr17/
```

---

## Loader behavior with full data

The loaders (`desi_dr1_bgs.py`, `sdss_dr17.py`) subsample by default (5K galaxies) because:

1. **Memory**: The current `ObservationalDataset` uses an n×n covariance matrix. For 5M points that would be ~200 TB of RAM.
2. **Explore/MCMC**: The Explore plot and MCMC pipeline are designed for ~1K–10K points.

To use **full data** you have two paths:

### Path A: Subsample on load (current)
- `max_rows=5000` (default) – good for Explore, quick tests
- `max_rows=50000` – larger sample, ~2.5 GB cov matrix
- `max_rows=None` – **not supported** for full 5M; would require architecture change

### Path B: Full-data architecture (future)
To support full catalogs without subsampling:
- Use **streaming** or **chunked** reads (astropy FITS can read by row range)
- Store only **diagonal** or **sparse** covariance (galaxy catalogs typically use weights, not full cov)
- Add **binned** or **histogram** observables (e.g. dN/dz) instead of per-galaxy arrays

---

## Environment / config

Optional: set a custom data root via environment variable:

```bash
export GRAVITATIONAL_DATA_ROOT=/path/to/large/disk/data
```

The loaders use `data/` relative to the project root by default. For very large storage, point this to a dedicated volume.

---

## Checksums (optional verification)

After download, verify file integrity if checksums are published:

- DESI: See https://data.desi.lbl.gov/doc/access/
- SDSS: See https://data.sdss.org/sas/dr8/sdss/spectro/redux/sdss_spectro_redux.sha1sum
