"""Historic Audit Logs Compression Engine for Mộng Nhiễm.

Recursively packs loose telemetry logs (*.json, *.jsonl) in prototype audit_logs
directories into standardized audit_logs.zip archives, verifies cryptographic
integrity (testzip + SHA-256), eliminates loose file bloat, and synchronizes
post-run freeze manifests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Tuple


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hex digest of a file in streaming chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def find_audit_log_directories(base_dir: Path) -> List[Path]:
    """Find all audit_logs directories containing loose files."""
    audit_dirs = []
    for root, dirs, files in os.walk(base_dir):
        if os.path.basename(root) == "audit_logs":
            loose = [f for f in files if not f.endswith(".zip")]
            if loose:
                audit_dirs.append(Path(root))
    return sorted(audit_dirs)


def pack_audit_directory(
    audit_dir: Path,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Pack an audit_logs directory into its parent run_dir/audit_logs.zip."""
    run_dir = audit_dir.parent
    loose_files = sorted(
        [f for f in audit_dir.iterdir() if f.is_file() and not f.name.endswith(".zip")]
    )
    if not loose_files:
        if not dry_run and not any(audit_dir.iterdir()):
            audit_dir.rmdir()
        return {}

    raw_bytes = sum(f.stat().st_size for f in loose_files)
    archive_path = run_dir / "audit_logs.zip"
    temp_archive = run_dir / "audit_logs.zip.tmp"

    if dry_run:
        return {
            "run_dir": run_dir,
            "archive_path": archive_path,
            "file_count": len(loose_files),
            "raw_bytes": raw_bytes,
            "zip_bytes": int(raw_bytes * 0.15),  # Estimated
            "sha256": "DRY_RUN",
        }

    # Write archive
    with zipfile.ZipFile(temp_archive, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_out:
        for file_path in loose_files:
            file_bytes = file_path.read_bytes()
            arcname = f"audit_logs/{file_path.name}"
            zip_out.writestr(arcname, file_bytes)

    # Verify archive integrity
    with zipfile.ZipFile(temp_archive, mode="r") as zip_in:
        corrupted = zip_in.testzip()
        if corrupted is not None:
            temp_archive.unlink(missing_ok=True)
            raise RuntimeError(f"Corrupted file in created archive: {corrupted}")
        in_names = zip_in.namelist()
        if len(in_names) != len(loose_files):
            temp_archive.unlink(missing_ok=True)
            raise RuntimeError(
                f"File count mismatch: expected {len(loose_files)}, got {len(in_names)}"
            )

    # Atomic replace
    if archive_path.exists():
        archive_path.unlink()
    temp_archive.rename(archive_path)

    zip_bytes = archive_path.stat().st_size
    sha256_hash = compute_sha256(archive_path)

    # Safely remove loose files and audit_logs folder
    shutil.rmtree(audit_dir)

    return {
        "run_dir": run_dir,
        "archive_path": archive_path,
        "file_count": len(loose_files),
        "raw_bytes": raw_bytes,
        "zip_bytes": zip_bytes,
        "sha256": sha256_hash,
    }


def synchronize_manifests(
    packed_results: List[Dict[str, Any]],
    repo_root: Path,
    dry_run: bool = False,
) -> int:
    """Update post-run freeze manifests to reference audit_logs.zip instead of loose files."""
    # Map normalized relative archive paths to sha256
    archive_hashes: Dict[str, str] = {}
    for res in packed_results:
        if not res or "archive_path" not in res:
            continue
        arch_p = res["archive_path"]
        sha = res["sha256"]
        rel_root = arch_p.relative_to(repo_root).as_posix()
        archive_hashes[rel_root] = sha

    updated_manifests = 0
    prototypes_dir = repo_root / "research" / "experiments" / "prototypes"

    for root, dirs, files in os.walk(prototypes_dir):
        if "post-run-freeze-manifest.json" in files:
            manifest_file = Path(root) / "post-run-freeze-manifest.json"
            try:
                manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            # Determine key container
            key_container = None
            if "files" in manifest_data and isinstance(manifest_data["files"], dict):
                key_container = manifest_data["files"]
            elif "file_hashes" in manifest_data and isinstance(manifest_data["file_hashes"], dict):
                key_container = manifest_data["file_hashes"]

            if not key_container:
                continue

            # Check if any keys reference audit_logs
            audit_keys = [k for k in key_container if "/audit_logs/" in k or k.startswith("audit_logs/")]
            if not audit_keys:
                continue

            proto_dir = manifest_file.parent
            # If manifest is inside definition/, prototype root is definition.parent
            if proto_dir.name == "definition":
                proto_root = proto_dir.parent
            else:
                proto_root = proto_dir

            # Group keys by target archive
            # Target archive is <dir_before_audit_logs>/audit_logs.zip
            new_entries: Dict[str, str] = {}
            for k in audit_keys:
                # E.g. "runs/mn017.../audit_logs/mn017-case-0001.json" -> "runs/mn017.../audit_logs.zip"
                parts = k.split("/audit_logs/")
                prefix = parts[0]
                archive_key = f"{prefix}/audit_logs.zip"

                # Find matching sha256 from candidate paths
                cand1 = (repo_root / archive_key).resolve()
                cand2 = (proto_root / archive_key).resolve()
                if cand1.exists():
                    sha = compute_sha256(cand1)
                    new_entries[archive_key] = sha
                elif cand2.exists():
                    sha = compute_sha256(cand2)
                    new_entries[archive_key] = sha
                elif dry_run:
                    new_entries[archive_key] = "DRY_RUN_HASH"
                else:
                    raise FileNotFoundError(f"Could not locate archive for manifest key: {archive_key}")

            # Delete old loose keys
            for k in audit_keys:
                del key_container[k]

            # Insert new archive keys
            for k, sha in new_entries.items():
                key_container[k] = sha

            # Re-sort keys alphabetically
            sorted_dict = {k: key_container[k] for k in sorted(key_container.keys())}
            if "files" in manifest_data:
                manifest_data["files"] = sorted_dict
            else:
                manifest_data["file_hashes"] = sorted_dict

            if not dry_run:
                manifest_file.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")
            updated_manifests += 1

    return updated_manifests


def main():
    parser = argparse.ArgumentParser(description="Pack historic audit logs into standard zip archives.")
    parser.add_argument("--dry-run", action="store_true", help="Inspect without modifying filesystem")
    parser.add_argument("--repo-root", default=".", help="Root directory of repository")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    base_dir = repo_root / "research" / "experiments" / "prototypes"

    audit_dirs = find_audit_log_directories(base_dir)
    print(f"Found {len(audit_dirs)} audit_logs directories to compress.")

    packed_results = []
    total_files = 0
    total_raw_bytes = 0
    total_zip_bytes = 0

    for i, ad in enumerate(audit_dirs, 1):
        rel_path = ad.relative_to(repo_root)
        res = pack_audit_directory(ad, dry_run=args.dry_run)
        if not res:
            continue
        packed_results.append(res)
        total_files += res["file_count"]
        total_raw_bytes += res["raw_bytes"]
        total_zip_bytes += res["zip_bytes"]
        if (i % 10 == 0) or (i == len(audit_dirs)):
            print(f"  [{i:2d}/{len(audit_dirs)}] Processed {rel_path} ({res['file_count']} files)")

    updated_manifests = synchronize_manifests(packed_results, repo_root, dry_run=args.dry_run)

    raw_mb = total_raw_bytes / (1024 * 1024)
    zip_mb = total_zip_bytes / (1024 * 1024)
    savings_pct = (1.0 - (total_zip_bytes / max(total_raw_bytes, 1))) * 100

    print("\n" + "=" * 60)
    print("HISTORIC AUDIT LOGS COMPRESSION SUMMARY")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTED'}")
    print(f"Total Archives Created: {len(packed_results)}")
    print(f"Total Loose Files Eliminated: {total_files}")
    print(f"Raw Telemetry Volume: {raw_mb:.2f} MB")
    print(f"Compressed Volume:    {zip_mb:.2f} MB")
    print(f"Storage Savings:      {savings_pct:.1f}%")
    print(f"Manifests Synchronized: {updated_manifests}")
    print("=" * 60)


if __name__ == "__main__":
    main()
