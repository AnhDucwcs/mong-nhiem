#!/usr/bin/env python3
"""Run frozen MCB v0.3.0; it never regenerates benchmark definitions."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import mcb
import mcb_v020
import mcb_v030

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "mcb-v0.3.0.json"


def runtime(server: Path) -> dict:
    raw = mcb.cmd([str(server), "--version"])
    match = re.search(r"version:\s*(.*?)\s*\(build\s+(\d+),\s*commit\s+([0-9a-f]+)", raw, re.IGNORECASE)
    return {"version": match.group(1) if match else None, "build": match.group(2) if match else None, "commit": match.group(3) if match else None, "raw_output": raw}


def configure_execution() -> None:
    """Reuse v0.2 process transport only; definition/config contracts are v0.3."""
    mcb_v020.BENCHMARK = mcb_v030.BENCHMARK
    mcb_v020.CASES = mcb_v030.CASES
    mcb_v020.CONFIG = CONFIG
    mcb_v020.VERSION = mcb_v030.VERSION
    mcb_v020.validate = mcb_v030.validate_definitions
    mcb_v020.evaluate = lambda case, text: mcb_v030.evaluate(case, text)[:2]


def run_one(model: Path, server: Path, port: int) -> Path:
    configure_execution()
    temporary = mcb_v020.run_model(model, server, port)
    run = temporary.with_name(temporary.name.replace("mcb-v020", "mcb-v030"))
    temporary.rename(run)
    metadata = json.loads((run / "metadata.json").read_text(encoding="utf-8"))
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    metadata.update({"run_id": run.name, "definition_fingerprint": mcb_v030.definition_fingerprint(), "runtime": runtime(server), "hardware": mcb.hw()})
    metadata["inference"]["benchmark_version"] = mcb_v030.VERSION
    summary["run_id"] = run.name
    (run / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (run / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return run


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-all", action="store_true")
    parser.add_argument("--models-dir", type=Path, default=mcb.MODELS)
    parser.add_argument("--llama-server", type=Path, default=mcb.BIN / "llama-server.exe")
    args = parser.parse_args()
    if args.run_all:
        for index, name in enumerate(mcb.MODELS_REQUIRED):
            print(run_one(args.models_dir / name, args.llama_server, 18300 + index))
