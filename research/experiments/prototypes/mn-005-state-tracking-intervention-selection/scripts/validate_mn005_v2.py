#!/usr/bin/env python3
"""Offline validation for MN-005 Gate C v2 implementation and retained attempts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import mn005_v2 as mn005


def validate_static() -> dict[str, object]:
    definition, cases, _ecc = mn005.load_definition()
    if definition["budgets"] != {"arm_a": 16, "stage_a": 80, "stage_b": 16}:
        raise mn005.ContractError("Gate B v2 budgets differ from authority")
    if definition["sizing"]["arm_b_tokens"] != 71 or definition["sizing"]["arm_c_tokens"] != mn005.EXPECTED_ARM_C_ARTIFACT_TOKENS:
        raise mn005.ContractError("Gate B v2 sizing authority mismatch")
    if [case["id"] for case in cases] != list(mn005.CASE_IDS):
        raise mn005.ContractError("frozen v2 case selection mismatch")
    return {"definition_fingerprint": mn005.definition_fingerprint(definition), "cases": [case["id"] for case in cases], "status": "valid"}


def validate_attempt(path: Path) -> dict[str, object]:
    metadata = mn005.load_json(path / "metadata.json")
    summary = mn005.load_json(path / "summary.json")
    records = [json.loads(line) for line in (path / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    definition, _cases, _ecc = mn005.load_definition()
    if metadata.get("contract_version") != "gate_b_v2" or metadata.get("definition_fingerprint") != mn005.definition_fingerprint(definition):
        raise mn005.ContractError("Gate C v2 attempt authority mismatch")
    if metadata.get("gate_b_v2_sha256") != definition["authority"]["gate_b_v2_sha256"]:
        raise mn005.ContractError("Gate C v2 authority hash mismatch")
    if summary["attempt_status"] == "canonical_valid":
        if len(records) != 18 or summary["efficacy_classification"] not in {"supported", "unsupported", "inconclusive"}:
            raise mn005.ContractError("canonical v2 attempt coverage/classification mismatch")
        for record in records:
            for stage in ("stage_b",) if record["arm"] == "A" else ("stage_a", "stage_b"):
                evidence = record[stage].get("raw_evidence_path")
                if not evidence or not (mn005.ROOT / evidence).is_file():
                    raise mn005.ContractError("missing persisted response evidence")
            if record["arm"] in {"B", "C"} and not record["artifact"]["literal_equal"]:
                raise mn005.ContractError("retained literal transport proof failed")
    elif summary["attempt_status"] != "experiment_invalid":
        raise mn005.ContractError("unknown Gate C v2 attempt status")
    return {"attempt_id": path.name, "attempt_status": summary["attempt_status"], "records": len(records)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", type=Path, action="append")
    args = parser.parse_args()
    print(json.dumps({"static": validate_static(), "attempts": [validate_attempt(path) for path in args.attempt or []]}, indent=2))


if __name__ == "__main__":
    main()
