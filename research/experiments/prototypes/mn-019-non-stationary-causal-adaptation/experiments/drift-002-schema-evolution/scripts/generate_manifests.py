"""Cryptographic Manifest Generator for Stage 2.

Generates pre-run-freeze-manifest.json and post-run-freeze-manifest.json with SHA-256 hashes.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Dict


def hash_file(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    def_dir = os.path.join(base_dir, "definition")
    os.makedirs(def_dir, exist_ok=True)

    pre_run_files = [
        "charter.md",
        "gate-b-contract.md",
        os.path.join("definition", "cases.json"),
        os.path.join("definition", "experiment.json"),
        os.path.join("configs", "models.json"),
        os.path.join("schemas", "case-result.schema.json"),
        os.path.join("schemas", "run-summary.schema.json"),
        os.path.join("src", "__init__.py"),
        os.path.join("src", "causal_event_logger.py"),
        os.path.join("src", "schema_evolution_engine.py"),
        os.path.join("src", "microworld_engine.py"),
        os.path.join("src", "discrepancy_monitor.py"),
        os.path.join("src", "dynamic_affordance.py"),
        os.path.join("src", "autodream_engine.py"),
        os.path.join("src", "hierarchical_planner.py"),
        os.path.join("src", "memento_stack.py"),
        os.path.join("src", "orchestrator.py"),
    ]

    pre_hashes: Dict[str, str] = {}
    for rel in pre_run_files:
        full_p = os.path.join(base_dir, rel)
        if os.path.isfile(full_p):
            pre_hashes[rel] = hash_file(full_p)

    pre_manifest = {
        "manifest_version": "1.0.0",
        "milestone": "mn-019-drift-002-schema-evolution",
        "stage": "pre_run_freeze",
        "file_hashes": pre_hashes,
    }

    with open(os.path.join(def_dir, "pre-run-freeze-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(pre_manifest, f, indent=2)

    post_run_files = list(pre_run_files) + [
        "gate-d-disposition-review.md",
        "README.md",
        os.path.join("reports", "drift-002-results.md"),
    ]

    post_hashes: Dict[str, str] = {}
    for rel in post_run_files:
        full_p = os.path.join(base_dir, rel)
        if os.path.isfile(full_p):
            post_hashes[rel] = hash_file(full_p)

    post_manifest = {
        "manifest_version": "1.0.0",
        "milestone": "mn-019-drift-002-schema-evolution",
        "stage": "post_run_freeze",
        "file_hashes": post_hashes,
    }

    with open(os.path.join(def_dir, "post-run-freeze-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(post_manifest, f, indent=2)

    print("Successfully generated pre-run and post-run freeze manifests for Stage 2.")


if __name__ == "__main__":
    main()
