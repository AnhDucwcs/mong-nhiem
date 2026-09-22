"""Executable script to materialize the MN-008 Gate C Phase 1 corpus."""
from __future__ import annotations

import sys
from pathlib import Path

# Add current scripts directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import mn008_materialization as mat


def main() -> int:
    print("Materializing MN-008 Gate C Phase 1 corpus...")
    manifest = mat.materialize_corpus()
    print("Corpus materialized successfully.")
    print(f"Manifest Corpus ID: {manifest['corpus_id']}")
    print(f"Total Cases: {manifest['case_count']}")
    for fname, fhash in manifest["file_hashes"].items():
        print(f"  {fname}: {fhash}")

    print("\nValidating materialized corpus...")
    result = mat.validate_corpus()
    print(f"Validation Status: {result['status']}")
    print(f"Manifest SHA-256: {result['manifest_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
