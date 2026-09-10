"""Frozen v3 authority, validity taxonomy, and mechanical verdicts."""
from __future__ import annotations

from typing import Any

import mn004
import mn004_v2

DEFINITION = mn004.DEFINITION / "experiment-v3.json"


def load_definition() -> dict[str, Any]:
    value = mn004.load_json(DEFINITION)
    if value.get("id") != "mn-004-state-representation-intervention-v3" or value.get("version") != "3.0.0":
        raise mn004.ContractError("unexpected v3 identity")
    return value


def fingerprint(value: dict[str, Any] | None = None) -> str:
    return mn004.sha256_bytes(b"experiment-v3.json\0" + mn004.canonical_json(value or load_definition()))


def validate_authority(value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or load_definition(); a = value["authority"]
    paths = {"gate_a_sha256": mn004.ROOT / "gate-a-hypothesis.md", "gate_b_v1_sha256": mn004.ROOT / "gate-b-measurement-contract.md", "gate_b_v2_sha256": mn004.ROOT / "gate-b-v2-measurement-contract.md", "gate_b_v3_sha256": mn004.ROOT / "gate-b-v3-measurement-contract.md", "v2_definition_sha256": mn004.DEFINITION / "experiment-v2.json", "v1_inventory_sha256": mn004.DEFINITION / "source-inventory.json", "v1_llama_preflight_sha256": mn004.DEFINITION / "preflight-llama-3.2-3b.json", "v1_qwen_preflight_sha256": mn004.DEFINITION / "preflight-qwen3-4b.json"}
    for key, path in paths.items():
        if mn004.sha256_file(path) != a[key]: raise mn004.ContractError(f"v3 authority mismatch: {key}")
    if value["models"] != mn004_v2.definition()["models"] or value["runtime"] != mn004_v2.definition()["runtime"]: raise mn004.ContractError("v3 changed frozen runtime/model")
    return value


def inventory(value: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    value = validate_authority(value); rows = mn004_v2.authorized_inventory()
    allowed = set(value["workload"]["case_ids"]); levels = set(value["workload"]["authorized_levels"])
    rows = [row for row in rows if row["case_id"] in allowed and row["requested_input_tokens"] in levels]
    if len(rows) != 48 or {(r["case_id"], r["requested_input_tokens"]) for r in rows} != {(case, level) for case in allowed for level in levels}: raise mn004.ContractError("v3 immutable inventory mismatch")
    return rows


def validate_offline() -> dict[str, Any]:
    value = validate_authority(); rows = inventory(value); preflight = mn004_v2.validate_retained_preflight()
    return {"v3_definition_fingerprint": fingerprint(value), "authorized_rows": len(rows), "preflight": preflight, "status": "valid"}


def classify_response(row: dict[str, Any], raw: str, response: dict[str, Any] | None, infrastructure_error: dict[str, Any] | None) -> dict[str, Any]:
    """Classify only an already verified frozen request; no protocol failure is model evidence."""
    if infrastructure_error:
        return {"validity": "infrastructure_failure", "failure_class": "infrastructure_failure", "diagnostic": None, "input_truncated": False, "output_limit_reached": False, "passed": False, "normalized": ""}
    output_limit = bool(response and response.get("choices") and response["choices"][0].get("finish_reason") == "length")
    failure, diagnostic, normalized = mn004.classify_output(row["target"], row["expected_answer"], row["source_events"], raw)
    if output_limit: failure, diagnostic = "output_token_limit_reached", None
    passed, _ = mn004.evaluate(row["target"], row["expected_answer"], raw)
    return {"validity": "valid", "failure_class": failure, "diagnostic": diagnostic, "input_truncated": False, "output_limit_reached": output_limit, "passed": bool(passed and not output_limit), "normalized": normalized}


def record_is_valid(row: dict[str, Any]) -> bool:
    return row.get("protocol_valid") is True and row.get("infrastructure_status") == "complete" and row.get("validator_status") == "valid" and row.get("input_truncated") is False


def passes(rows: list[dict[str, Any]], level: int) -> int:
    return sum(bool(row["evaluation"]["passed"]) for row in rows if row["requested_input_tokens"] == level)


def reproduction_verdict(rows: list[dict[str, Any]], value: dict[str, Any] | None = None) -> str:
    value = value or load_definition(); ids = set(value["workload"]["frozen_case_ids"])
    if len(rows) != 6 or {row["case_id"] for row in rows} != ids or any(row["requested_input_tokens"] != 8192 for row in rows) or not all(record_is_valid(row) for row in rows): return "invalid_comparison"
    return "compatible" if passes(rows, 8192) == value["rules"]["reproduction_passes"] else "baseline_drift"


def llama_verdict(untreated: list[dict[str, Any]], ledger: list[dict[str, Any]], value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or load_definition(); required = {(case, level) for case in value["workload"]["case_ids"] for level in value["workload"]["authorized_levels"]}; keys = lambda rows: {(r["case_id"], r["requested_input_tokens"]) for r in rows}
    if keys(untreated) != required or keys(ledger) != required or not all(record_is_valid(r) for r in untreated + ledger): return {"verdict": "invalid_comparison"}
    u8,l8,u2,l2 = passes(untreated,8192),passes(ledger,8192),passes(untreated,2048),passes(ledger,2048); primary = l8 >= value["rules"]["ledger_minimum"] and l8-u8 >= value["rules"]["primary_delta_minimum"]; reference = l2 >= u2-value["rules"]["llama_reference_max_drop"]
    return {"verdict": "llama_reference_regression" if not reference else "supported_under_bounded_claim" if primary else "unsupported_no_effect_or_insufficient_effect", "u8":u8,"l8":l8,"delta8":l8-u8,"u2":u2,"l2":l2,"delta2":l2-u2,"reference_ok":reference}


def qwen_verdict(untreated: list[dict[str, Any]], ledger: list[dict[str, Any]] | None, value: dict[str, Any] | None = None) -> dict[str, Any]:
    value=value or load_definition(); ids=set(value["workload"]["case_ids"])
    if len(untreated)!=24 or {r["case_id"] for r in untreated}!=ids or not all(record_is_valid(r) for r in untreated): return {"verdict":"invalid_comparison"}
    u=passes(untreated,8192)
    if u<value["rules"]["qwen_eligibility"]: return {"verdict":"control_not_qualified","untreated":u}
    if ledger is None:return {"verdict":"eligible_pending_ledger","untreated":u}
    if len(ledger)!=24 or not all(record_is_valid(r) for r in ledger):return {"verdict":"invalid_comparison"}
    l=passes(ledger,8192);return {"verdict":"qwen_no_harm_pass" if l>=u-value["rules"]["qwen_max_drop"] else "qwen_regression","untreated":u,"ledger":l,"delta":l-u}
