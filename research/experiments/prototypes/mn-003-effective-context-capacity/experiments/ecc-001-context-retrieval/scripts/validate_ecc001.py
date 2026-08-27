#!/usr/bin/env python3
"""Offline validation for retained ECC-001 evidence."""
from __future__ import annotations

import argparse
from pathlib import Path

import ecc001


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", nargs="*", type=Path)
    args = parser.parse_args()
    definition, cases = ecc001.load_definition()
    print(
        f"Validated {definition['id']} {definition['version']}: "
        f"{len(cases)} cases, fingerprint {ecc001.definition_fingerprint()}"
    )
    retained_runs = (
        sorted(path for path in ecc001.RUNS.iterdir() if (path / "metadata.json").is_file())
        if ecc001.RUNS.is_dir()
        else []
    )
    runs = args.run or retained_runs
    for run in runs:
        summary = ecc001.validate_run(run)
        print(f"Validated {run.name}: {summary['run_status']}, {summary['total_results']} results")


if __name__ == "__main__":
    main()
