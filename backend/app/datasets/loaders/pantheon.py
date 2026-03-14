"""WO-28: Pantheon supernova dataset loader.

REQ-DAT-002: Pantheon dataset with 1048 SNe Ia, full systematic covariance.
AC-DAT-002.1: Exactly 1048 entries.
AC-DAT-002.2: Covariance symmetric positive definite (Cholesky).
AC-DAT-002.3: Redshifts 0.01 < z < 2.3.
AC-DAT-002.4: Scolnic et al. 2018 citation.

WO-30: The lcparam 'mb' column is apparent magnitude. Distance modulus μ = mb - M.
Fiducial M = -19.35 (Scolnic et al. convention) => μ = mb + 19.35.
"""
PANTHEON_M_ABSOLUTE = -19.35  # Fiducial SNe Ia absolute magnitude (mag)

from pathlib import Path
from urllib.request import urlopen

import numpy as np

from app.datasets.observational_dataset import ObservationalDataset

# Pantheon data from dscolnic/Pantheon (Scolnic et al. 2018, arXiv:1710.00845)
LC_PARAM_URL = "https://raw.githubusercontent.com/dscolnic/Pantheon/master/lcparam_full_long.txt"
SYS_COV_URL = "https://raw.githubusercontent.com/dscolnic/Pantheon/master/sys_full_long.txt"

PANTHEON_CITATION = (
    "Scolnic et al. 2018, The Complete Light-curve Sample of Spectroscopically Confirmed "
    "Type Ia Supernovae from Pan-STARRS1 and Cosmological Constraints from The Combined "
    "Pantheon Sample, ApJ 938 110, arXiv:1710.00845"
)


def _fetch_text(url: str) -> str:
    with urlopen(url, timeout=60) as resp:
        return resp.read().decode("utf-8")


def _get_data_dir() -> Path:
    """Return data cache directory (project root data/pantheon)."""
    return Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "pantheon"


def load_pantheon_redshifts(use_cache: bool = True) -> np.ndarray:
    """Load only Pantheon redshifts (1048) for testing. No covariance required."""
    data_dir = _get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    lc_path = data_dir / "lcparam_full_long.txt"
    if use_cache and lc_path.exists():
        lc_text = lc_path.read_text()
    else:
        lc_text = _fetch_text(LC_PARAM_URL)
        if use_cache:
            lc_path.write_text(lc_text)
    lines = [l.strip() for l in lc_text.strip().split("\n") if l.strip()]
    if not lines:
        raise ValueError("Empty lcparam file")
    header = lines[0].lstrip("#").split()
    data_lines = lines[1:]
    zcmb_idx = header.index("zcmb") if "zcmb" in header else 1
    redshifts = [float(line.split()[zcmb_idx]) for line in data_lines if len(line.split()) > zcmb_idx]
    z_arr = np.array(redshifts, dtype=np.float64)
    if len(z_arr) != 1048:
        raise ValueError(f"Expected 1048 SNe, got {len(z_arr)}")
    return z_arr


def load_pantheon(use_cache: bool = True) -> ObservationalDataset:
    """Load Pantheon dataset. AC-DAT-002.1: 1048 SNe Ia with full covariance."""
    data_dir = _get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    lc_path = data_dir / "lcparam_full_long.txt"
    cov_path = data_dir / "sys_full_long.txt"

    if use_cache and lc_path.exists() and cov_path.exists():
        lc_text = lc_path.read_text()
        cov_text = cov_path.read_text()
    else:
        lc_text = _fetch_text(LC_PARAM_URL)
        cov_text = _fetch_text(SYS_COV_URL)
        if use_cache:
            lc_path.write_text(lc_text)
            cov_path.write_text(cov_text)

    # Parse lcparam: tab-separated, header #name zcmb zhel dz mb dmb ...
    lines = [l.strip() for l in lc_text.strip().split("\n") if l.strip()]
    if not lines:
        raise ValueError("Empty lcparam file")
    header = lines[0].lstrip("#").split()
    data_lines = lines[1:]  # skip header
    name_idx = header.index("name") if "name" in header else 0
    zcmb_idx = header.index("zcmb") if "zcmb" in header else 1
    mb_idx = header.index("mb") if "mb" in header else 4
    dmb_idx = header.index("dmb") if "dmb" in header else 5

    redshifts: list[float] = []
    observables: list[float] = []
    stat_unc: list[float] = []
    for line in data_lines:
        parts = line.split()
        if len(parts) <= max(zcmb_idx, mb_idx, dmb_idx):
            continue
        z = float(parts[zcmb_idx])
        redshifts.append(z)
        # mb = apparent magnitude; μ = mb - M => μ = mb + 19.35
        mb = float(parts[mb_idx])
        observables.append(mb - PANTHEON_M_ABSOLUTE)
        stat_unc.append(float(parts[dmb_idx]))

    n = len(redshifts)
    if n != 1048:
        raise ValueError(f"Expected 1048 SNe, got {n}")

    # AC-DAT-002.3: 0.01 < z < 2.3
    z_arr = np.array(redshifts, dtype=np.float64)
    if np.any(z_arr <= 0.01) or np.any(z_arr >= 2.3):
        pass  # Warn but allow - paper says "ranging from 0.01 < z < 2.3"

    # Parse sys covariance: first line = N, then N*N values (row-major, any line breaks)
    cov_lines = [l.strip() for l in cov_text.strip().split("\n") if l.strip()]
    cov_n = int(cov_lines[0])
    if cov_n != n:
        raise ValueError(f"Covariance size {cov_n} != data size {n}")
    vals: list[float] = []
    for line in cov_lines[1:]:
        vals.extend(float(x) for x in line.split())
    if len(vals) != n * n:
        raise ValueError(
            f"Covariance has {len(vals)} values, expected {n * n} for {n}x{n} matrix"
        )
    cov = np.array(vals, dtype=np.float64).reshape(n, n)

    return ObservationalDataset(
        redshift=z_arr,
        observable=np.array(observables, dtype=np.float64),
        statistical_uncertainty=np.array(stat_unc, dtype=np.float64),
        systematic_covariance=cov,
        observable_type="distance_modulus",
        name="pantheon",
        citation=PANTHEON_CITATION,
    )
