"""Computes SHA-256 for all prototype artifacts and seals post-run-freeze-manifest.json."""

import hashlib
import json
from pathlib import Path


def hash_file(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_post_run_manifest():
    root = Path(__file__).resolve().parent.parent
    files_to_hash = {}

    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            # Ignore pycache, git, loose audit_logs if any, and pre-existing post-run manifest
            if "__pycache__" in rel:
                continue
            if ".git" in rel:
                continue
            if rel.startswith("runs/") and not (rel.endswith("run_info.json") or rel.endswith("audit_logs.zip")):
                continue
            if rel == "post-run-freeze-manifest.json":
                continue

            files_to_hash[rel] = hash_file(path)

    manifest = {
        "prototype": "mn-022-swarm-consensus-pruning",
        "status": "FROZEN_POST_RUN",
        "total_files": len(files_to_hash),
        "files": files_to_hash,
    }

    out_file = root / "post-run-freeze-manifest.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Post-run freeze manifest sealed: {out_file} ({len(files_to_hash)} files hashed)")
    return manifest


if __name__ == "__main__":
    generate_post_run_manifest()
