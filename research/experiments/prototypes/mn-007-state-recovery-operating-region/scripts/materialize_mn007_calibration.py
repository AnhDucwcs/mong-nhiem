#!/usr/bin/env python3
"""Materialize and validate the static MN-007 calibration corpus; no model code."""
from __future__ import annotations

import argparse
from pathlib import Path

from mn007_materialization import DEFINITION_ROOT, write_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFINITION_ROOT)
    args = parser.parse_args()
    manifest = write_artifacts(args.output)
    print(manifest["manifest_core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
