"""Utility to pack episode audit logs into a compressed zip archive and eliminate loose JSON bloat."""
from __future__ import annotations

import hashlib
import os
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def pack_audit_logs(run_dir: Path) -> str:
    """Packages all loose episode JSON files under run_dir/audit_logs/ into run_dir/audit_logs.zip.
    
    Deletes the raw JSON files to enforce the Zero Loose File Bloat Protocol.
    Returns the SHA-256 fingerprint of the created audit_logs.zip.
    """
    audit_dir = run_dir / "audit_logs"
    zip_path = run_dir / "audit_logs.zip"

    json_files = list(audit_dir.glob("*.json")) if audit_dir.exists() else []

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for jf in sorted(json_files):
            zf.write(jf, arcname=jf.name)

    # Clean up loose JSON files and directory
    if audit_dir.exists():
        shutil.rmtree(audit_dir)

    sha = compute_sha256(zip_path)
    return sha
