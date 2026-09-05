#!/usr/bin/env python3
"""Validation and mechanical verdicts for the frozen MN-004 v2 contract."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import mn004

DEFINITION_PATH = mn004.DEFINITION / "experiment-v2.json"


def definition_fingerprint(definition: dict[str, Any] | None = None) -> str:
    """Fingerprint every v2 contract-critical field, including v1 authority pins."""
    definition = definition or mn004.load_json(DEFINITION_PATH)
    return mn004.sha256_bytes(b"experiment-v2.json\0" + mn004.canonical_json(definition))


def definition() -> dict[str, Any]:
    value = mn004.load_json(DEFINITION_PATH)
    if value.get("id") != "mn-004-state-representation-intervention-v2" or value.get("version") != "2.0.0":
        raise mn004.ContractError("unexpected v2 experiment identity")
    return value


def _path(relative: str) -> Path:
    return (mn004.DEFINITION / relative).resolve()


def validate_authority(value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or definition()
    authority = value["authority"]
    for path_key, hash_key in (
        ("gate_a_path", "gate_a_sha256"),
        ("gate_b_v1_path", "gate_b_v1_sha256"),
        ("gate_b_v2_path", "gate_b_v2_sha256"),
        ("v1_definition_path", "v1_definition_sha256"),
        ("v1_inventory_path", "v1_inventory_sha256"),
        ("v1_llama_preflight_path", "v1_llama_preflight_sha256"),
        ("v1_qwen_preflight_path", "v1_qwen_preflight_sha256"),
    ):
        path = _path(authority[path_key])
        if not path.is_file() or mn004.sha256_file(path) != authority[hash_key]:
            raise mn004.ContractError(f"v2 authority mismatch: {path_key}")
    v1 = mn004.validate_definition()
    if mn004.definition_fingerprint(v1) != authority["v1_definition_fingerprint"]:
        raise mn004.ContractError("v2 v1-definition fingerprint mismatch")
    inventory = mn004.load_json(mn004.DEFINITION / authority["v1_inventory_path"])
    if inventory.get("inventory_fingerprint") != authority["v1_inventory_fingerprint"]:
        raise mn004.ContractError("v2 inventory fingerprint mismatch")
    if value["runtime"] != v1["runtime"] or value["models"] != v1["models"]:
        raise mn004.ContractError("v2 runtime/model pin differs from v1 frozen authority")
    return value


def authorized_inventory(value: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    value = validate_authority(value)
    inventory = mn004.load_json(mn004.DEFINITION / value["authority"]["v1_inventory_path"])
    levels, ids = value["workload"]["authorized_levels"], value["workload"]["authorized_case_ids"]
    rows = [row for row in inventory["cases"] if row["requested_input_tokens"] in levels and row["case_id"] in ids]
    expected = {(level, case_id) for level in levels for case_id in ids}
    actual = {(row["requested_input_tokens"], row["case_id"]) for row in rows}
    if actual != expected or len(rows) != 48:
        raise mn004.ContractError("v2 authorized inventory is not exactly 24 immutable rows at 2k and 8k")
    for row in rows:
        case = {"id": row["case_id"], "entity": row["target"], "updates": row["target_updates"], "answer": row["expected_answer"]}
        mn004.validate_pair(case, row["source_events"], row["natural_prompt"], row["ledger_prompt"], mn004.validate_definition())
        if mn004.source_event_hash(row["source_events"]) != row["source_event_hash"]:
            raise mn004.ContractError(f"{row['case_id']}: source event hash mismatch")
        if mn004.target_event_indexes(row["source_events"], row["target"]) != row["target_event_indexes"]:
            raise mn004.ContractError(f"{row['case_id']}: target source indexes mismatch")
    return sorted(rows, key=lambda row: (row["requested_input_tokens"], row["case_id"]))


def preflight_record(preflight: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    match = [record for record in preflight["records"] if record["case_id"] == row["case_id"] and record["requested_input_tokens"] == row["requested_input_tokens"]]
    if len(match) != 1 or match[0]["source_event_hash"] != row["source_event_hash"]:
        raise mn004.ContractError("retained preflight row mismatch")
    return match[0]


def validate_retained_preflight(value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = validate_authority(value)
    rows = authorized_inventory(value)
    answer: dict[str, Any] = {}
    for model_key, filename in (("llama-3.2-3b", value["authority"]["v1_llama_preflight_path"]), ("qwen3-4b", value["authority"]["v1_qwen_preflight_path"])):
        preflight = mn004.load_json(mn004.DEFINITION / filename)
        if preflight.get("definition_fingerprint") != value["authority"]["v1_definition_fingerprint"] or preflight.get("inventory_fingerprint") != value["authority"]["v1_inventory_fingerprint"]:
            raise mn004.ContractError("retained preflight authority mismatch")
        selected = [row for row in rows if model_key == "llama-3.2-3b" or row["requested_input_tokens"] == 8192]
        for row in selected:
            retained = preflight_record(preflight, row)
            for condition, prompt_key in (("natural_language", "natural_prompt"), ("ledger", "ledger_prompt")):
                measured = retained["conditions"][condition]
                if measured["prompt_hash"] != mn004.sha256_text(row[prompt_key]):
                    raise mn004.ContractError("retained preflight prompt hash mismatch")
                if not measured["fits_with_output_allowance"] or measured["actual_prompt_tokens"] + value["runtime"]["output_tokens"] > value["runtime"]["configured_context_size"]:
                    raise mn004.ContractError("contract_not_executable: v2 selected prompt cannot fit")
        answer[model_key] = {"selected_rows": len(selected), "status": "feasible"}
    return answer


def validate_offline() -> dict[str, Any]:
    value = validate_authority()
    rows = authorized_inventory(value)
    preflight = validate_retained_preflight(value)
    return {"definition_fingerprint": definition_fingerprint(value), "authorized_rows": len(rows), "by_level": {str(level): sum(row["requested_input_tokens"] == level for row in rows) for level in value["workload"]["authorized_levels"]}, "preflight": preflight, "status": "valid"}


def _valid(records: list[dict[str, Any]]) -> bool:
    return bool(records) and all(row.get("validator_status") == "valid" and not row.get("truncated") and not row.get("error") for row in records)


def passes(records: list[dict[str, Any]], level: int) -> int:
    return sum(bool(row["evaluation"]["passed"]) for row in records if row["requested_input_tokens"] == level)


def reproduction_verdict(records: list[dict[str, Any]], value: dict[str, Any] | None = None) -> str:
    value = value or definition()
    expected = set(value["workload"]["frozen_reproduction_case_ids"])
    if len(records) != 6 or {row["case_id"] for row in records} != expected or any(row["requested_input_tokens"] != 8192 for row in records) or not _valid(records):
        return "invalid_comparison"
    return "compatible" if passes(records, 8192) == value["llama_rules"]["reproduction_exact_passes"] else "baseline_drift"


def llama_verdict(untreated: list[dict[str, Any]], ledger: list[dict[str, Any]], value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or definition(); primary, reference = value["workload"]["primary_level"], value["workload"]["reference_level"]
    required = {(level, case_id) for level in value["workload"]["authorized_levels"] for case_id in value["workload"]["authorized_case_ids"]}
    keys = lambda rows: {(row["requested_input_tokens"], row["case_id"]) for row in rows}
    if not _valid(untreated) or not _valid(ledger) or keys(untreated) != required or keys(ledger) != required:
        return {"verdict": "invalid_comparison"}
    u8, l8, u2, l2 = passes(untreated, primary), passes(ledger, primary), passes(untreated, reference), passes(ledger, reference)
    primary_ok = l8 >= value["llama_rules"]["primary_ledger_minimum"] and l8 - u8 >= value["llama_rules"]["primary_delta_minimum"]
    reference_ok = l2 >= u2 - value["llama_rules"]["reference_maximum_drop"]
    primary_verdict = "supported_under_bounded_claim" if primary_ok else "unsupported_no_effect_or_insufficient_effect"
    return {"verdict": "llama_reference_regression" if not reference_ok else primary_verdict, "primary_verdict": primary_verdict, "u8": u8, "l8": l8, "delta8": l8-u8, "u2": u2, "l2": l2, "delta2": l2-u2, "reference_ok": reference_ok}


def qwen_verdict(untreated: list[dict[str, Any]], ledger: list[dict[str, Any]] | None, value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or definition(); ids = set(value["workload"]["authorized_case_ids"])
    if len(untreated) != 24 or {row["case_id"] for row in untreated} != ids or any(row["requested_input_tokens"] != 8192 for row in untreated) or not _valid(untreated):
        return {"verdict": "invalid_comparison"}
    u = passes(untreated, 8192)
    if u < value["qwen_rules"]["eligibility_minimum"]:
        return {"verdict": "control_not_qualified", "untreated": u}
    if ledger is None:
        return {"verdict": "eligible_pending_ledger", "untreated": u}
    if len(ledger) != 24 or {row["case_id"] for row in ledger} != ids or not _valid(ledger):
        return {"verdict": "invalid_comparison"}
    l = passes(ledger, 8192)
    return {"verdict": "qwen_no_harm_pass" if l >= u - value["qwen_rules"]["maximum_drop"] else "qwen_regression", "untreated": u, "ledger": l, "delta": l-u}
