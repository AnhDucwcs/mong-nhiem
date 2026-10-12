"""Verification script to audit all runs for zero loose file bloat and valid zip archives."""
from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def validate_runs() -> bool:
    base_dir = Path(__file__).resolve().parent.parent
    runs_dir = base_dir / "runs"

    if not runs_dir.exists():
        print("No runs directory found.")
        return True

    run_dirs = [d for d in runs_dir.iterdir() if d.is_dir()]
    if not run_dirs:
        print("No run directories found.")
        return True

    all_passed = True
    print(f"=== Validating {len(run_dirs)} Runs for Evidence Integrity ===")

    for rdir in sorted(run_dirs):
        run_name = rdir.name
        zip_file = rdir / "audit_logs.zip"
        info_file = rdir / "run_info.json"
        loose_json = list(rdir.glob("episode_*.json"))
        loose_dir = rdir / "audit_logs"

        # Check loose files
        if loose_json or (loose_dir.exists() and list(loose_dir.glob("*.json"))):
            print(f"FAIL: {run_name} contains loose JSON files! Bloat violation.")
            all_passed = False
            continue

        if not zip_file.exists():
            print(f"FAIL: {run_name} missing audit_logs.zip!")
            all_passed = False
            continue

        if not info_file.exists():
            print(f"FAIL: {run_name} missing run_info.json!")
            all_passed = False
            continue

        # Inspect zip
        try:
            with zipfile.ZipFile(zip_file, "r") as zf:
                file_list = zf.namelist()
                episode_count = len(file_list)
        except Exception as e:
            print(f"FAIL: {run_name} corrupted audit_logs.zip ({e})")
            all_passed = False
            continue

        # Compute SHA
        sha = compute_sha256(zip_file)
        print(f"PASS: {run_name} | Episodes: {episode_count} | SHA-256: {sha[:16]}... | 0 loose files")

    return all_passed


if __name__ == "__main__":
    success = validate_runs()
    exit(0 if success else 1)
