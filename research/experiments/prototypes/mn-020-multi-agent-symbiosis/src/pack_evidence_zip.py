"""Standard Library Zip Evidence Packaging Engine for MN-020.

Compresses loose episode audit logs into a single audit_logs.zip archive,
computes cryptographic SHA-256 manifest fingerprints, and provides zero-extraction
direct JSON inspection.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class EvidenceZipPacker:
    """Standard Library Zip Packaging Engine for Benchmark Audit Telemetry."""

    @staticmethod
    def pack_audit_logs(
        run_dir: Path | str,
        remove_loose_files: bool = True,
    ) -> Dict[str, Any]:
        """Compress all *.json logs in run_dir/audit_logs into run_dir/audit_logs.zip.
        
        Returns:
            Dict containing archive path, file count, raw size, compressed size,
            compression ratio, and SHA-256 cryptographic fingerprint.
        """
        run_path = Path(run_dir)
        audit_dir = run_path / "audit_logs"
        if not audit_dir.exists() or not audit_dir.is_dir():
            raise FileNotFoundError(f"Audit directory not found at: {audit_dir}")

        json_files = sorted(audit_dir.glob("*.json"))
        if not json_files:
            raise ValueError(f"No JSON audit files found in: {audit_dir}")

        archive_path = run_path / "audit_logs.zip"
        raw_bytes_total = 0

        with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_out:
            for file_path in json_files:
                file_bytes = file_path.read_bytes()
                raw_bytes_total += len(file_bytes)
                # Store relative to audit_logs/
                arcname = f"audit_logs/{file_path.name}"
                zip_out.writestr(arcname, file_bytes)

        compressed_bytes = archive_path.stat().st_size
        sha256_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()

        # Remove loose JSON directory if requested
        if remove_loose_files:
            shutil.rmtree(audit_dir)

        compression_ratio = 1.0 - (compressed_bytes / max(raw_bytes_total, 1))

        return {
            "archive_path": str(archive_path),
            "file_count": len(json_files),
            "raw_bytes": raw_bytes_total,
            "compressed_bytes": compressed_bytes,
            "compression_ratio": round(compression_ratio, 4),
            "sha256": sha256_hash,
        }

    @staticmethod
    def inspect_archive_file(
        archive_path: Path | str,
        internal_filename: str,
    ) -> Dict[str, Any]:
        """Read a single JSON file directly from audit_logs.zip without extraction."""
        path = Path(archive_path)
        if not path.exists():
            raise FileNotFoundError(f"Archive not found: {path}")

        with zipfile.ZipFile(path, mode="r") as zip_in:
            # Handle with or without audit_logs/ prefix
            target = internal_filename
            if not target.startswith("audit_logs/") and f"audit_logs/{target}" in zip_in.namelist():
                target = f"audit_logs/{target}"
            data = zip_in.read(target)
            return json.loads(data.decode("utf-8"))

    @staticmethod
    def list_archived_files(archive_path: Path | str) -> List[str]:
        """List all filenames inside audit_logs.zip."""
        path = Path(archive_path)
        with zipfile.ZipFile(path, mode="r") as zip_in:
            return sorted(zip_in.namelist())
