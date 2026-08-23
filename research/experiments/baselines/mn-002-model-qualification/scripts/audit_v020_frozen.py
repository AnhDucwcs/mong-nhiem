#!/usr/bin/env python3
"""Audit every v0.2 failure with the frozen v0.3 evaluator."""
from __future__ import annotations

import json
from pathlib import Path

import mcb
import mcb_v030

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "mcb-v0.2.0-audit.json"

def main() -> None:
    cases = {case["id"]: case for case in mcb_v030.load_cases()}
    latest = {}
    for directory in sorted(mcb.RUNS.glob("*mcb-v020*")):
        if (directory / "metadata.json").is_file() and (directory / "summary.json").is_file():
            metadata, summary = mcb.load(directory / "metadata.json"), mcb.load(directory / "summary.json")
            if metadata["benchmark"]["version"] == "0.2.0" and summary["run_status"] == "valid": latest[metadata["model"]["file"]] = directory
    audit = []
    for model, directory in latest.items():
        for line in (directory / "results.jsonl").read_text(encoding="utf-8").splitlines():
            old = json.loads(line)
            if old["evaluation"]["passed"]: continue
            case = cases[old["case_id"]]
            passed, _canonical, normalized = mcb_v030.evaluate(case, old["output"]["text"])
            audit.append({"model": model, "run_id": directory.name, "benchmark_version": "0.2.0", "suite": case["suite"], "case_id": case["id"], "rendered_request": old["request"], "expected_canonical_answer": case["expected"].get("value", case["expected"].get("schema")), "accepted_answers": case["expected"]["accepted_values"], "raw_response": old["output"]["text"], "normalized_response": normalized, "old_score": old["evaluation"]["score"], "proposed_corrected_score": float(passed), "classification": "OUTPUT_EQUIVALENCE_DEFECT" if passed else "VALID_MODEL_FAILURE", "justification": "Matches an explicitly declared accepted answer after conservative normalization." if passed else "Does not match any explicit accepted answer; no fuzzy or substring match is used."})
    OUT.write_text(json.dumps({"source_version": "0.2.0", "target_evaluator": "0.3.0", "records": audit}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(audit)} audited failed records")

if __name__ == "__main__": main()
