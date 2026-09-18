#!/usr/bin/env python3
"""Validate the static MN-007 calibration corpus; no model code."""
from __future__ import annotations

import argparse
from pathlib import Path

from mn007_materialization import DEFINITION_ROOT, validate_materialized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFINITION_ROOT)
    args = parser.parse_args()
    manifest = validate_materialized(args.corpus)
    print(manifest["manifest_core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
