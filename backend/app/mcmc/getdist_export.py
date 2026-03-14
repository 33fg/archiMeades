"""WO-36: GetDist-compatible chain export.

AC-MCC-003.1: Text chains file + paramnames in GetDist format.
Format: weight  like  param1  param2  ...
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# LaTeX labels for common cosmology params
DEFAULT_LABELS: dict[str, str] = {
    "omega_m": r"\Omega_m",
    "omega_b": r"\Omega_b",
    "h0": "H_0",
    "h": "h",
    "i_rel": r"I_{\mathrm{rel}}",
    "sigma8": r"\sigma_8",
    "n_s": "n_s",
}


def _flatten_samples(posterior: dict[str, Any], param_names: list[str]) -> list[list[float]]:
    """Convert posterior dict to list of rows [weight, like, p1, p2, ...]."""
    rows: list[list[float]] = []
    n = 0
    first_key = param_names[0] if param_names else None
    if not first_key or first_key not in posterior:
        return rows

    raw = posterior[first_key]
    if isinstance(raw[0], (list, tuple)):
        # Multi-chain: (chains, samples) -> flatten to (chains * samples,)
        for chain_idx in range(len(raw)):
            chain_len = len(raw[chain_idx])
            for i in range(chain_len):
                row = [1.0, 0.0]  # weight=1, like=0 (placeholder)
                for p in param_names:
                    arr = posterior.get(p)
                    if arr is not None:
                        row.append(float(arr[chain_idx][i]))
                rows.append(row)
    else:
        for i in range(len(raw)):
            row = [1.0, 0.0]
            for p in param_names:
                arr = posterior.get(p)
                if arr is not None:
                    row.append(float(arr[i]))
            rows.append(row)
    return rows


def write_getdist_chains(
    path: Path,
    posterior: dict[str, Any],
    param_names: list[str],
    *,
    thin: int = 1,
) -> None:
    """Write GetDist-format chains file. AC-MCC-003.1.

    Args:
        path: Output .txt path (e.g. chains_lcdm_1.txt)
        posterior: Dict of param -> 1D or 2D array
        param_names: Parameter order
        thin: Thinning factor (1 = no thinning)
    """
    rows = _flatten_samples(posterior, param_names)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as f:
        for i in range(0, len(rows), thin):
            line = " ".join(f"{x:.8e}" for x in rows[i])
            f.write(line + "\n")


def write_paramnames(path: Path, param_names: list[str]) -> None:
    """Write GetDist .paramnames file. AC-MCC-003.1."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for p in param_names:
            label = DEFAULT_LABELS.get(p, p.replace("_", r"\_"))
            f.write(f"{p}\t{label}\n")


def export_getdist(
    base_path: Path,
    posterior: dict[str, Any],
    param_names: list[str],
    *,
    thin: int = 1,
    chain_per_file: bool = True,
) -> list[Path]:
    """Export posterior to GetDist-format files. Returns list of created paths.

    If chain_per_file and multi-chain, writes xxx_1.txt, xxx_2.txt, etc.
    Otherwise writes single xxx.txt.
    """
    created: list[Path] = []
    base = base_path.with_suffix("")

    # Determine chain structure
    first_key = param_names[0] if param_names else None
    if not first_key or first_key not in posterior:
        return created

    raw = posterior[first_key]
    is_multi = isinstance(raw[0], (list, tuple)) if raw else False

    if is_multi and chain_per_file:
        for c in range(len(raw)):
            single_posterior = {p: posterior[p][c] for p in param_names if p in posterior}
            chain_path = base.parent / f"{base.name}_{c + 1}.txt"
            write_getdist_chains(chain_path, single_posterior, param_names, thin=thin)
            created.append(chain_path)
    else:
        chain_path = base.with_suffix(".txt")
        write_getdist_chains(chain_path, posterior, param_names, thin=thin)
        created.append(chain_path)

    param_path = base.with_suffix(".paramnames")
    write_paramnames(param_path, param_names)
    created.append(param_path)

    return created


def export_getdist_to_strings(
    posterior: dict[str, Any],
    param_names: list[str],
    *,
    thin: int = 1,
) -> tuple[str, str]:
    """Export to GetDist format as (chains_txt, paramnames_txt) for API response.

    For multi-chain, chains_txt concatenates all chains (GetDist can load combined).
    """
    rows = _flatten_samples(posterior, param_names)
    lines: list[str] = []
    for i in range(0, len(rows), thin):
        lines.append(" ".join(f"{x:.8e}" for x in rows[i]))
    chains_txt = "\n".join(lines)

    param_lines: list[str] = []
    for p in param_names:
        label = DEFAULT_LABELS.get(p, p.replace("_", r"\_"))
        param_lines.append(f"{p}\t{label}")
    paramnames_txt = "\n".join(param_lines)

    return chains_txt, paramnames_txt
