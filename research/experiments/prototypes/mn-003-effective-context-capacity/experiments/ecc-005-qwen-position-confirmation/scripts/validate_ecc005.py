#!/usr/bin/env python3
"""Validate retained ECC-005 Qwen confirmation evidence offline."""
from __future__ import annotations

import argparse
from pathlib import Path

import ecc005


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", nargs="*", type=Path)
    args = parser.parse_args()
    definition, cases = ecc005.load_definition()
    print(
        f"Validated {definition['id']}: {len(cases)} fresh cases, "
        f"fingerprint {ecc005.definition_fingerprint()}"
    )
    runs = args.run or sorted(path for path in ecc005.RUNS.iterdir() if (path / "metadata.json").is_file())
    for run in runs:
        print(f"Validated {run.name}: {ecc005.validate_run(run)['run_status']}")


if __name__ == "__main__":
    main()
