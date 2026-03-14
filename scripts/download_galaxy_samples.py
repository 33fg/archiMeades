#!/usr/bin/env python3
"""Download galaxy catalog data for DESI DR1 BGS and SDSS DR17.

Run from project root. Creates data/desi_dr1_bgs/ and data/sdss_dr17/.

Modes:
  --desi          DESI BGS sample (~9.6 MB) - default
  --desi --full   DESI BGS full catalog (~645 MB: NGC + SGC)
  --sdss          SDSS MPA-JHU full (~2.7 GB: galSpecExtra + specObj)

See scripts/DATA_DOWNLOAD_AND_STORAGE.md for details.
"""

from pathlib import Path
from urllib.request import urlretrieve

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = Path(__file__).resolve().parent.parent / "data"

DESI_DIR = DATA_ROOT / "desi_dr1_bgs"
SDSS_DIR = DATA_ROOT / "sdss_dr17"

# DESI URLs
DESI_SAMPLE_URL = (
    "https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/LSScats/v1.5/"
    "BGS_BRIGHT-21.5_SGC_clustering.dat.fits"
)
DESI_BASE = "https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/LSScats/v1.5/"
DESI_FULL_FILES = [
    "BGS_ANY_NGC_clustering.dat.fits",   # ~477 MB
    "BGS_ANY_SGC_clustering.dat.fits",  # ~168 MB
]

# SDSS URLs (SAS)
SDSS_BASE = "https://data.sdss.org/sas/dr8/sdss/spectro/redux/"
SDSS_FILES = [
    "galSpecExtra-dr8.fits",   # ~340 MB
    "specObj-dr8.fits",        # ~2.4 GB
]


def _progress_hook(block_num: int, block_size: int, total_size: int):
    if total_size <= 0:
        return
    downloaded = block_num * block_size
    pct = min(100, 100 * downloaded / total_size)
    mb = downloaded / (1024 * 1024)
    total_mb = total_size / (1024 * 1024)
    print(f"\r  {pct:.1f}% ({mb:.1f} / {total_mb:.1f} MB)", end="", flush=True)


def download_file(url: str, dest: Path, force: bool = False, resume: bool = False, max_retries: int = 5) -> Path:
    import shutil
    import subprocess
    import time
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force and not resume:
        print(f"  Already cached: {dest.name}")
        return dest
    print(f"  Downloading {dest.name} ...")
    curl = shutil.which("curl")
    if curl:
        resume = ["-C", "-"] if dest.exists() else []
        # Use HTTP/1.1 to avoid HTTP/2 stream errors on slow connections
        for attempt in range(max_retries):
            rc = subprocess.run(
                [curl, "-L", "--http1.1", "-o", str(dest), *resume, url],
                capture_output=False,
            )
            if rc.returncode == 0:
                break
            if attempt < max_retries - 1:
                wait = 10 * (attempt + 1)
                print(f"\n  Retry in {wait}s (attempt {attempt + 2}/{max_retries})...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"curl failed for {dest.name} after {max_retries} attempts")
    else:
        urlretrieve(url, dest, reporthook=_progress_hook)
    print()
    return dest


def download_desi(force: bool = False, full: bool = False, resume: bool = False) -> list[Path]:
    """Download DESI BGS. full=True gets NGC+SGC (~645 MB)."""
    DESI_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    if full:
        for fname in DESI_FULL_FILES:
            url = DESI_BASE + fname
            dest = DESI_DIR / fname
            paths.append(download_file(url, dest, force, resume))
    else:
        dest = DESI_DIR / "BGS_BRIGHT-21.5_SGC_clustering.dat.fits"
        paths.append(download_file(DESI_SAMPLE_URL, dest, force, resume))
    return paths


def download_sdss(force: bool = False, resume: bool = False) -> list[Path]:
    """Download SDSS MPA-JHU full (~2.7 GB: galSpecExtra + specObj)."""
    SDSS_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for fname in SDSS_FILES:
        url = SDSS_BASE + fname
        dest = SDSS_DIR / fname
        paths.append(download_file(url, dest, force, resume))
    return paths


def main():
    import argparse
    p = argparse.ArgumentParser(
        description="Download galaxy catalog data",
        epilog="See scripts/DATA_DOWNLOAD_AND_STORAGE.md for storage layout."
    )
    p.add_argument("--desi", action="store_true", help="Download DESI BGS")
    p.add_argument("--sdss", action="store_true", help="Download SDSS MPA-JHU full")
    p.add_argument("--full", action="store_true", help="DESI: full NGC+SGC (~645 MB). SDSS: always full.")
    p.add_argument("--force", action="store_true", help="Re-download even if cached")
    p.add_argument("--resume", action="store_true", help="Resume incomplete downloads (don't skip existing files)")
    args = p.parse_args()
    if not args.desi and not args.sdss:
        args.desi = True
    if args.desi:
        print("DESI DR1 BGS:")
        download_desi(force=args.force, full=args.full, resume=args.resume)
    if args.sdss:
        print("SDSS DR17 MPA-JHU:")
        download_sdss(force=args.force, resume=args.resume)
    print("Done. Data in:", DATA_ROOT)


if __name__ == "__main__":
    main()
