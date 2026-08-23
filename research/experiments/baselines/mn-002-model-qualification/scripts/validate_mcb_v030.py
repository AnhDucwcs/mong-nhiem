#!/usr/bin/env python3
"""Validate frozen MCB v0.3.0 artefacts and write its deterministic report."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

import mcb
import mcb_v030


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" / "v0.3.0"
REPORT = ROOT / "reports" / "model-qualification-v0.3.0.md"
VALIDATION = ROOT / "reports" / "mcb-v0.3.0-validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(load(SCHEMAS / name))


def require_valid(instance: object, schema: str, label: str) -> None:
    errors = sorted(validator(schema).iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        raise RuntimeError(f"{label}: {errors[0].message}")


def selected_runs() -> dict[str, Path]:
    """Choose the newest valid metadata-matched run per required model.

    Directory names are deliberately ignored. This protects v0.3 selection from
    legacy orchestrator IDs and prevents an older attempt superseding a newer run.
    """
    fingerprint = mcb_v030.definition_fingerprint()
    candidates: dict[str, list[tuple[str, Path]]] = {}
    for directory in sorted(mcb.RUNS.iterdir(), key=lambda item: item.name):
        metadata_path = directory / "metadata.json"
        summary_path = directory / "summary.json"
        if not (directory.is_dir() and metadata_path.is_file() and summary_path.is_file()):
            continue
        metadata, summary = load(metadata_path), load(summary_path)
        if (metadata.get("benchmark", {}).get("version") == mcb_v030.VERSION
                and metadata.get("definition_fingerprint") == fingerprint
                and metadata.get("inference", {}).get("benchmark_version") == mcb_v030.VERSION
                and summary.get("run_status") == "valid"):
            candidates.setdefault(metadata["model"]["file"], []).append((metadata["created_at"], directory))
    selected = {model: max(options)[1] for model, options in candidates.items()}
    if set(selected) != set(mcb.MODELS_REQUIRED):
        missing = set(mcb.MODELS_REQUIRED) - set(selected)
        extra = set(selected) - set(mcb.MODELS_REQUIRED)
        raise RuntimeError(f"expected exactly six required candidates; missing={missing}, extra={extra}")
    return selected


def validate_run(run: Path) -> dict:
    metadata, summary = load(run / "metadata.json"), load(run / "summary.json")
    require_valid(metadata, "metadata.schema.json", f"{run.name}/metadata")
    require_valid(summary, "summary.schema.json", f"{run.name}/summary")
    records = [json.loads(line) for line in (run / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    cases = {case["id"]: case for case in mcb_v030.load_cases()}
    if len(records) != 100 or {record["case_id"] for record in records} != set(cases):
        raise RuntimeError(f"{run.name}: exact frozen case coverage is required")
    for record in records:
        require_valid(record, "result.schema.json", f"{run.name}/{record['case_id']}")
        passed, _, _ = mcb_v030.evaluate(cases[record["case_id"]], record["output"].get("content", ""))
        if record["evaluation"]["score"] != int(passed):
            raise RuntimeError(f"{run.name}/{record['case_id']}: stored score differs from v0.3 evaluator")
    score = sum(record["evaluation"]["score"] for record in records) / 100
    if summary["overall"]["score"] != score:
        raise RuntimeError(f"{run.name}: summary score is not reproducible")
    return summary


def validate_definitions() -> None:
    mcb_v030.validate_definitions()
    for case in mcb_v030.load_cases():
        require_valid(case, "case.schema.json", case["id"])


def write_report(selected: dict[str, Path], summaries: dict[str, dict]) -> None:
    lines = [
        "# MN-002 Model Qualification — MCB v0.3.0",
        "",
        f"Frozen definition fingerprint: `{mcb_v030.definition_fingerprint()}`.",
        "",
        "The v0.3 evaluator performs exact comparison against each case's declared accepted values, after only Unicode/case/whitespace and terminal-punctuation normalization. Structured output remains strict JSON-object validation. No fuzzy, substring, or model-judged scoring is used.",
        "",
        "| Model | Instruction | Structured | Retrieval | State | Causal | Overall | Qualification |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for model in mcb.MODELS_REQUIRED:
        summary = summaries[model]
        values = [f"{summary['suites'][suite]['score']:.2f}" for suite in mcb_v030.SUITES]
        values += [f"{summary['overall']['score']:.2f}", "PASS" if summary["qualification"]["passed"] else "FAIL"]
        lines.append("| " + " | ".join([model, *values]) + " |")
    lines += [
        "",
        "Selection rule: newest run per required model whose metadata has benchmark `0.3.0`, the fingerprint above, a v0.3 inference label, and `run_status=valid`; directory names are not inputs to selection.",
        "",
        "The raw run IDs retain a legacy `mcb-v020` orchestrator label. This is recorded as an integration naming defect; benchmark version and frozen fingerprint are the authoritative identifiers and were validated before reporting.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {
        "benchmark_version": mcb_v030.VERSION,
        "definition_fingerprint": mcb_v030.definition_fingerprint(),
        "selected_runs": {model: path.name for model, path in selected.items()},
        "status": "valid",
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def repair_metadata() -> int:
    """Correct only the inherited version label for already completed v0.3 runs."""
    repaired = 0
    for directory in mcb.RUNS.iterdir():
        path = directory / "metadata.json"
        if not path.is_file():
            continue
        metadata = load(path)
        if (metadata.get("benchmark", {}).get("version") == mcb_v030.VERSION
                and metadata.get("definition_fingerprint") == mcb_v030.definition_fingerprint()
                and metadata.get("inference", {}).get("benchmark_version") == "0.2.0"):
            metadata["inference"]["benchmark_version"] = mcb_v030.VERSION
            metadata["integration_notes"] = [
                "Run directory and run_id preserve the inherited mcb-v020 orchestration label.",
                "The inherited inference benchmark_version label was corrected to 0.3.0 after execution; definitions and recorded outputs were not changed.",
            ]
            path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
            repaired += 1
    return repaired


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair-metadata", action="store_true")
    args = parser.parse_args()
    if args.repair_metadata:
        print(f"Repaired {repair_metadata()} inherited metadata labels")
    validate_definitions()
    runs = selected_runs()
    summaries = {model: validate_run(path) for model, path in runs.items()}
    write_report(runs, summaries)
    print(f"Validated {len(runs)} MCB {mcb_v030.VERSION} runs")
