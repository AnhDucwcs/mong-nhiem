#!/usr/bin/env python3
"""Validate retained ECC-007 evidence without local inference."""
from __future__ import annotations

import argparse
from pathlib import Path

import ecc007

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
args = parser.parse_args()
summary = ecc007.validate_run(args.run)
print(f"Valid ECC-007 evidence: {args.run} ({summary['total_results']} results)")
