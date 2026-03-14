"""WO-36: Tests for GetDist export."""

import tempfile
from pathlib import Path

import pytest

from app.mcmc.getdist_export import (
    export_getdist,
    export_getdist_to_strings,
    write_getdist_chains,
    write_paramnames,
)


class TestGetDistExport:
    """AC-MCC-003.1: GetDist-compatible chains and paramnames."""

    def test_export_to_strings_single_chain(self) -> None:
        """Single-chain posterior exports to chains_txt and paramnames_txt."""
        posterior = {"omega_m": [0.31, 0.32, 0.33], "h0": [70.0, 70.1, 70.2]}
        chains_txt, paramnames_txt = export_getdist_to_strings(
            posterior, ["omega_m", "h0"]
        )
        lines = chains_txt.strip().split("\n")
        assert len(lines) == 3
        assert "1.00000000e+00" in lines[0]
        assert "3.10000000e-01" in lines[0]
        assert "omega_m" in paramnames_txt
        assert "h0" in paramnames_txt

    def test_export_to_strings_with_thin(self) -> None:
        """Thinning reduces row count."""
        posterior = {"omega_m": [0.1, 0.2, 0.3, 0.4, 0.5], "h0": [68, 69, 70, 71, 72]}
        chains_txt, _ = export_getdist_to_strings(
            posterior, ["omega_m", "h0"], thin=2
        )
        lines = chains_txt.strip().split("\n")
        assert len(lines) == 3  # 0, 2, 4

    def test_write_getdist_chains(self) -> None:
        """write_getdist_chains creates valid file."""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "chains.txt"
            posterior = {"omega_m": [0.3], "h0": [70.0]}
            write_getdist_chains(path, posterior, ["omega_m", "h0"])
            content = path.read_text()
            assert "1.00000000e+00" in content
            assert "0.00000000e+00" in content
            assert "3.00000000e-01" in content

    def test_write_paramnames(self) -> None:
        """write_paramnames creates valid paramnames file."""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.paramnames"
            write_paramnames(path, ["omega_m", "h0"])
            content = path.read_text()
            assert "omega_m" in content
            assert "h0" in content

    def test_export_getdist_files(self) -> None:
        """export_getdist creates chain and paramnames files."""
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "chains"
            posterior = {"omega_m": [0.31, 0.32], "h0": [70.0, 70.1]}
            created = export_getdist(base.with_suffix(".txt"), posterior, ["omega_m", "h0"])
            assert len(created) == 2
            assert any("paramnames" in str(p) for p in created)
            assert any(".txt" in str(p) for p in created)
