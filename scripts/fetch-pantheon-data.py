#!/usr/bin/env python3
"""Fetch Pantheon data for WO-28. Run from project root."""
import urllib.request
from pathlib import Path

LC_URL = "https://raw.githubusercontent.com/dscolnic/Pantheon/master/lcparam_full_long.txt"
COV_URL = "https://raw.githubusercontent.com/dscolnic/Pantheon/master/sys_full_long.txt"

data_dir = Path(__file__).resolve().parent.parent / "backend" / "data" / "pantheon"
data_dir.mkdir(parents=True, exist_ok=True)

for name, url in [("lcparam_full_long.txt", LC_URL), ("sys_full_long.txt", COV_URL)]:
    path = data_dir / name
    print(f"Fetching {url} ...")
    with urllib.request.urlopen(url, timeout=120) as r:
        path.write_bytes(r.read())
    print(f"  -> {path} ({path.stat().st_size} bytes)")

# Inspect cov format
cov_text = (data_dir / "sys_full_long.txt").read_text()
lines = cov_text.strip().split("\n")
n = int(lines[0])
vals = []
for line in lines[1:]:
    vals.extend(float(x) for x in line.split())
print(f"Cov: n={n}, total values={len(vals)}, expected n*n={n*n}")
