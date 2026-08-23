#!/usr/bin/env python3
"""Validate the frozen six-run MCB v0.3.0 qualification evidence."""
from __future__ import annotations

import json
from pathlib import Path

import mcb
import mcb_v030
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" / "v0.3.0"
EVIDENCE = ROOT / "reports" / "mcb-v0.3.0-validation.json"
LIMITS = {"instruction_following": 0.80, "structured_output": 0.90, "context_retrieval": 0.80, "state_tracking": 0.70, "causal_reasoning": 0.70}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_schema(value: object, schema: str, label: str) -> None:
    errors = list(Draft202012Validator(load(SCHEMAS / schema)).iter_errors(value))
    if errors:
        raise RuntimeError(f"{label}: {errors[0].message}")


def selected_runs() -> dict[str, Path]:
    """Resolve only the run IDs frozen in committed qualification evidence."""
    evidence = load(EVIDENCE)
    if evidence.get("benchmark_version") != mcb_v030.VERSION or evidence.get("definition_fingerprint") != mcb_v030.definition_fingerprint():
        raise RuntimeError("qualification evidence does not match frozen v0.3 definitions")
    selected = {model: mcb.RUNS / run_id for model, run_id in evidence["selected_runs"].items()}
    if set(selected) != set(mcb.MODELS_REQUIRED):
        raise RuntimeError("qualification evidence must name exactly the six required models")
    for model, run in selected.items():
        if not run.is_dir():
            raise RuntimeError(f"selected evidence run is missing: {run.name}")
        metadata, summary = load(run / "metadata.json"), load(run / "summary.json")
        if metadata.get("model", {}).get("file") != model or metadata.get("benchmark", {}).get("version") != mcb_v030.VERSION or metadata.get("definition_fingerprint") != mcb_v030.definition_fingerprint() or summary.get("run_status") != "valid":
            raise RuntimeError(f"selected evidence run is not valid v0.3 evidence: {run.name}")
    return selected


def failure_reasons(suites: dict, overall: float) -> list[str]:
    reasons = [] if overall >= 0.80 else [f"overall {overall:.2f} < 0.80"]
    return reasons + [f"{suite} {suites[suite]['score']:.2f} < {LIMITS[suite]:.2f}" for suite in mcb_v030.SUITES if suites[suite]["score"] < LIMITS[suite]]


def validate_run(run: Path) -> None:
    metadata, summary = load(run / "metadata.json"), load(run / "summary.json")
    require_schema(metadata, "metadata.schema.json", f"{run.name}/metadata")
    require_schema(summary, "summary.schema.json", f"{run.name}/summary")
    cases = {case["id"]: case for case in mcb_v030.load_cases()}
    records = [json.loads(line) for line in (run / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    if len(records) != 100 or {record["case_id"] for record in records} != set(cases):
        raise RuntimeError(f"{run.name}: incomplete case coverage")
    grouped = {suite: [] for suite in mcb_v030.SUITES}
    for record in records:
        require_schema(record, "result.schema.json", f"{run.name}/{record['case_id']}")
        passed, _, _ = mcb_v030.evaluate(cases[record["case_id"]], record["output"]["text"])
        if record["evaluation"] != {"passed": passed, "score": float(passed)}:
            raise RuntimeError(f"{run.name}/{record['case_id']}: stored case score is incorrect")
        grouped[cases[record["case_id"]]["suite"]].append(record)
    suites = {suite: {"cases": len(rows), "passed": sum(row["evaluation"]["passed"] for row in rows), "score": sum(row["evaluation"]["score"] for row in rows) / len(rows)} for suite, rows in grouped.items()}
    overall = {"cases": 100, "passed": sum(value["passed"] for value in suites.values()), "score": sum(value["passed"] for value in suites.values()) / 100}
    qualification = {"passed": not failure_reasons(suites, overall["score"]), "failure_reasons": failure_reasons(suites, overall["score"])}
    if summary["suites"] != suites or summary["overall"] != overall or summary["qualification"] != qualification:
        raise RuntimeError(f"{run.name}: stored summary is not reproducible")


if __name__ == "__main__":
    mcb_v030.validate_definitions()
    for run in selected_runs().values():
        validate_run(run)
    print(f"Validated 6 frozen MCB {mcb_v030.VERSION} runs; fingerprint {mcb_v030.definition_fingerprint()}")
