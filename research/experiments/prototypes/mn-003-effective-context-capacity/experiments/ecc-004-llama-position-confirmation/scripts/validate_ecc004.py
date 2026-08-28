#!/usr/bin/env python3
"""Offline validation for retained ECC-004 evidence."""
from __future__ import annotations

import argparse
from pathlib import Path

import ecc004


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", nargs="*", type=Path)
    args = parser.parse_args()
    definition, cases = ecc004.load_definition()
    print(f"Validated {definition['id']} {definition['version']}: {len(cases)} fresh cases, fingerprint {ecc004.definition_fingerprint()}")
    retained = sorted(path for path in ecc004.RUNS.iterdir() if (path / "metadata.json").is_file()) if ecc004.RUNS.is_dir() else []
    for run in args.run or retained:
        summary = ecc004.validate_run(run)
        print(f"Validated {run.name}: {summary['run_status']}, {summary['total_results']} results")


if __name__ == "__main__":
    main()
