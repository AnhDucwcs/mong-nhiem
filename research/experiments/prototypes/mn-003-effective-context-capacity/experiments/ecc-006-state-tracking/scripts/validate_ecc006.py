#!/usr/bin/env python3
"""Validate retained ECC-006 evidence without inference."""
from __future__ import annotations

import argparse
from pathlib import Path

import ecc006

parser=argparse.ArgumentParser(); parser.add_argument("run", nargs="*", type=Path); args=parser.parse_args()
definition,cases=ecc006.load_definition(); print(f"Validated {definition['id']}: {len(cases)} cases, fingerprint {ecc006.definition_fingerprint()}")
for run in args.run or sorted(path for path in ecc006.RUNS.iterdir() if (path / "metadata.json").is_file()): print(f"Validated {run.name}: {ecc006.validate_run(run)['run_status']}")
