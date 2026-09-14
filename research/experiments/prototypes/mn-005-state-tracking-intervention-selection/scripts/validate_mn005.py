#!/usr/bin/env python3
"""Offline validation for the frozen MN-005 Gate C implementation and retained attempts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import mn005


def validate_static() -> dict[str, object]:
    definition, cases, _ecc = mn005.load_definition()
    if mn005.CONTROL_ARTIFACT.count("\n") != 3 or "KAPPA" not in mn005.CONTROL_ARTIFACT:
        raise mn005.ContractError("invalid active-control grammar")
    sample = {"context": "Context event log:\nState update: Unit Example 1 changed to RED.", "arm_a": "Context event log:\nState update: Unit Example 1 changed to RED.\n\nQuestion:\nWhat is the current state of Unit Example 1? Return only the state."}
    content, slot, _rendered = mn005.stage_b_prompt(sample, {"entity": "Unit Example 1"}, b"entity=Unit Example 1 | state=RED")
    if "<artifact>\nentity=Unit Example 1 | state=RED\n</artifact>" not in content or slot != b"entity=Unit Example 1 | state=RED":
        raise mn005.ContractError("Stage B literal envelope validation failed")
    if "final" in mn005.RECONSTRUCTION_INSTRUCTION.casefold() and "Do not include" not in mn005.RECONSTRUCTION_INSTRUCTION:
        raise mn005.ContractError("reconstruction instruction contains an unprohibited final-state field")
    if len(cases) != 6 or [case["id"] for case in cases] != list(mn005.CASE_IDS):
        raise mn005.ContractError("frozen case selection mismatch")
    return {"definition_fingerprint": mn005.definition_fingerprint(definition), "cases": [case["id"] for case in cases], "status": "valid"}


def validate_attempt(path: Path) -> dict[str, object]:
    metadata = mn005.load_json(path / "metadata.json"); summary = mn005.load_json(path / "summary.json")
    records = [json.loads(line) for line in (path / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    definition, _cases, _ecc = mn005.load_definition()
    if metadata["definition_fingerprint"] != mn005.definition_fingerprint(definition) or metadata["attempt_id"] != path.name:
        raise mn005.ContractError("attempt authority mismatch")
    if summary["attempt_status"] == "canonical_valid":
        if len(records) != 18 or summary["efficacy_classification"] not in {"supported", "unsupported", "inconclusive"}:
            raise mn005.ContractError("canonical attempt coverage/classification mismatch")
        for record in records:
            if record["arm"] in {"B", "C"} and not record["artifact"]["literal_equal"]:
                raise mn005.ContractError("retained literal transport proof failed")
    elif summary["attempt_status"] != "experiment_invalid":
        raise mn005.ContractError("unknown attempt status")
    return {"attempt_id": path.name, "attempt_status": summary["attempt_status"], "records": len(records)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--attempt", type=Path, action="append")
    args = parser.parse_args(); output = {"static": validate_static(), "attempts": [validate_attempt(path) for path in args.attempt or []]}; print(json.dumps(output, indent=2))


if __name__ == "__main__": main()
