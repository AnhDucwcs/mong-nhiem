#!/usr/bin/env python3
"""Validate v0.3 results using the persisted output contract (``output.text``)."""
from __future__ import annotations

import json
from pathlib import Path

import mcb_v030
import validate_mcb_v030 as base


def validate_run(run: Path) -> dict:
    metadata, summary = base.load(run / "metadata.json"), base.load(run / "summary.json")
    base.require_valid(metadata, "metadata.schema.json", f"{run.name}/metadata")
    base.require_valid(summary, "summary.schema.json", f"{run.name}/summary")
    records = [json.loads(line) for line in (run / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    cases = {case["id"]: case for case in mcb_v030.load_cases()}
    if len(records) != 100 or {record["case_id"] for record in records} != set(cases):
        raise RuntimeError(f"{run.name}: exact frozen case coverage is required")
    for record in records:
        base.require_valid(record, "result.schema.json", f"{run.name}/{record['case_id']}")
        passed, _, _ = mcb_v030.evaluate(cases[record["case_id"]], record["output"].get("text", ""))
        if record["evaluation"]["score"] != int(passed):
            raise RuntimeError(f"{run.name}/{record['case_id']}: stored score differs from v0.3 evaluator")
    score = sum(record["evaluation"]["score"] for record in records) / 100
    if summary["overall"]["score"] != score:
        raise RuntimeError(f"{run.name}: summary score is not reproducible")
    return summary


if __name__ == "__main__":
    base.validate_definitions()
    runs = base.selected_runs()
    summaries = {model: validate_run(path) for model, path in runs.items()}
    base.write_report(runs, summaries)
    print(f"Validated {len(runs)} MCB {mcb_v030.VERSION} runs")
