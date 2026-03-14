#!/usr/bin/env python3
"""Run likelihood and scan tests, write results to file."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "backend/tests/test_likelihood.py", "backend/tests/test_scans.py", "-v"],
    capture_output=True,
    text=True,
    timeout=120,
    cwd="/Users/jbarseneau/Archimedes",
)

with open("/Users/jbarseneau/Archimedes/scripts/pytest_result.txt", "w") as f:
    f.write("STDOUT:\n")
    f.write(result.stdout)
    f.write("\nSTDERR:\n")
    f.write(result.stderr)
    f.write(f"\nReturn code: {result.returncode}\n")

sys.exit(result.returncode)
