"""Frozen v5 efficacy authority, selection, and mechanical verdicts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import mn004
import mn004_v2
import mn004_v3

DEFINITION = mn004.DEFINITION / "experiment-v5.json"
PHASES = ("llama_8k_reproduction", "llama_untreated", "llama_ledger", "qwen_8k_untreated", "qwen_8k_ledger")


def load_definition() -> dict[str, Any]:
    value = mn004.load_json(DEFINITION)
    if value.get("id") != "mn-004-state-representation-intervention-v5" or value.get("version") != "5.0.0":
        raise mn004.ContractError("unexpected v5 identity")
    return value


def fingerprint(value: dict[str, Any] | None = None) -> str:
    return mn004.sha256_bytes(b"experiment-v5.json\0" + mn004.canonical_json(value or load_definition()))


def validate_authority(value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or load_definition(); authority = value["authority"]
    paths = {
        "gate_a_sha256": mn004.ROOT / "gate-a-hypothesis.md",
        "gate_b_v1_sha256": mn004.ROOT / "gate-b-measurement-contract.md",
        "gate_b_v2_sha256": mn004.ROOT / "gate-b-v2-measurement-contract.md",
        "gate_b_v3_sha256": mn004.ROOT / "gate-b-v3-measurement-contract.md",
        "gate_b_v4_sha256": mn004.ROOT / "gate-b-v4-runtime-feasibility-contract.md",
        "gate_b_v5_sha256": mn004.ROOT / "gate-b-v5-final-efficacy-contract.md",
        "v3_postmortem_sha256": mn004.ROOT / "reports" / "mn-004-v3-infrastructure-postmortem.md",
        "v3_definition_sha256": mn004.DEFINITION / "experiment-v3.json",
        "v4_definition_sha256": mn004.DEFINITION / "experiment-v4.json",
        "v1_inventory_sha256": mn004.DEFINITION / "source-inventory.json",
        "v1_llama_preflight_sha256": mn004.DEFINITION / "preflight-llama-3.2-3b.json",
        "v1_qwen_preflight_sha256": mn004.DEFINITION / "preflight-qwen3-4b.json",
    }
    for key, path in paths.items():
        if mn004.sha256_file(path) != authority[key]:
            raise mn004.ContractError(f"v5 authority mismatch: {key}")
    inventory = mn004.load_json(mn004.DEFINITION / "source-inventory.json")
    if inventory.get("inventory_fingerprint") != authority["v1_inventory_fingerprint"]:
        raise mn004.ContractError("v5 immutable inventory fingerprint mismatch")
    prior = mn004_v3.validate_authority()
    if value["models"] != prior["models"] or value["runtime"] != prior["runtime"]:
        raise mn004.ContractError("v5 changed frozen model/runtime")
    return value


def inventory(value: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    value = validate_authority(value); source = mn004_v2.authorized_inventory(); workload = value["workload"]
    case_ids, levels = workload["case_ids"], workload["authorized_levels"]
    order = {(level, case): position for position, (level, case) in enumerate((level, case) for level in levels for case in case_ids)}
    selected = [row for row in source if row["case_id"] in case_ids and row["requested_input_tokens"] in levels]
    if len(selected) != 48 or {(row["requested_input_tokens"], row["case_id"]) for row in selected} != set(order):
        raise mn004.ContractError("v5 selected inventory is not the immutable 2k/8k pair")
    return sorted(selected, key=lambda row: order[(row["requested_input_tokens"], row["case_id"])])


def phase_rows(phase: str, value: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    value = value or load_definition(); rows = inventory(value)
    if phase == "llama_8k_reproduction":
        frozen = set(value["workload"]["frozen_case_ids"])
        return [row for row in rows if row["requested_input_tokens"] == 8192 and row["case_id"] in frozen]
    if phase in {"llama_untreated", "llama_ledger"}: return rows
    if phase in {"qwen_8k_untreated", "qwen_8k_ledger"}: return [row for row in rows if row["requested_input_tokens"] == 8192]
    raise mn004.ContractError(f"unknown v5 phase: {phase}")


def condition_for(phase: str) -> str:
    return "ledger" if phase.endswith("ledger") else "natural_language"


def model_for(phase: str) -> str:
    return "qwen3-4b" if phase.startswith("qwen") else "llama-3.2-3b"


def preflight_pair(row: dict[str, Any], model_key: str, condition: str, value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or load_definition(); preflight = mn004.load_json(mn004.DEFINITION / f"preflight-{model_key}.json")
    record = mn004_v2.preflight_record(preflight, row); pair = record["conditions"][condition]
    if not pair["fits_with_output_allowance"] or pair["actual_prompt_tokens"] + value["runtime"]["output_tokens"] > value["runtime"]["configured_context_size"]:
        raise mn004.ContractError("v5 retained token feasibility mismatch")
    return pair


def validate_offline() -> dict[str, Any]:
    value = validate_authority(); rows = inventory(value)
    checked = []
    for model in ("llama-3.2-3b", "qwen3-4b"):
        levels = {2048, 8192} if model == "llama-3.2-3b" else {8192}
        for row in rows:
            if row["requested_input_tokens"] in levels:
                for condition in ("natural_language", "ledger"):
                    pair = preflight_pair(row, model, condition, value); checked.append(pair["actual_prompt_tokens"])
    renderer_definition = mn004.load_json(mn004.DEFINITION / "experiment.json")
    for row in rows:
        mn004.validate_pair({"id": row["case_id"], "entity": row["target"], "updates": row["target_updates"]}, row["source_events"], row["natural_prompt"], row["ledger_prompt"], renderer_definition)
    return {"v5_definition_fingerprint": fingerprint(value), "authorized_rows": len(rows), "preflight_pairs_checked": len(checked), "status": "valid"}


def run_directories(phase: str) -> list[Path]:
    return sorted(path for path in mn004.RUNS.glob("v5-*") if (path / "metadata.json").is_file() and mn004.load_json(path / "metadata.json").get("phase") == phase and mn004.load_json(path / "metadata.json").get("v5_definition_fingerprint") == fingerprint())


def latest_summary(phase: str) -> dict[str, Any] | None:
    runs = run_directories(phase)
    return mn004.load_json(runs[-1] / "summary.json") if runs and (runs[-1] / "summary.json").is_file() else None


def _prestart_block(summary: dict[str, Any] | None) -> bool:
    return bool(summary and summary.get("outcome") == "environment_contaminated" and summary.get("observed_results") == 0 and summary.get("server_lifecycle", {}).get("started") is False)


def phase_allowed(phase: str) -> bool:
    reproduction, untreated, ledger, qwen_u, qwen_l = (latest_summary(name) for name in PHASES)
    if phase == "llama_8k_reproduction": return reproduction is None or _prestart_block(reproduction)
    if phase == "llama_untreated": return reproduction is not None and reproduction.get("outcome") == "compatible" and untreated is None
    if phase == "llama_ledger": return untreated is not None and untreated.get("outcome") == "phase_completed" and ledger is None
    if phase == "qwen_8k_untreated":
        verdict = llama_verdict_from_runs()
        return ledger is not None and verdict.get("verdict") in {"supported_under_bounded_claim", "unsupported_no_effect_or_insufficient_effect", "llama_reference_regression"} and qwen_u is None
    if phase == "qwen_8k_ledger":
        verdict = qwen_verdict_from_runs()
        return qwen_u is not None and verdict.get("verdict") == "eligible_pending_ledger" and qwen_l is None
    raise mn004.ContractError(f"unknown v5 phase: {phase}")


def read_records(phase: str) -> list[dict[str, Any]]:
    runs = run_directories(phase)
    if not runs: return []
    return [json.loads(line) for line in (runs[-1] / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]


def record_is_valid(row: dict[str, Any]) -> bool:
    return mn004_v3.record_is_valid(row)


def _valid_set(rows: list[dict[str, Any]], expected: set[tuple[str, int]]) -> bool:
    return {(row.get("case_id"), row.get("requested_input_tokens")) for row in rows} == expected and all(record_is_valid(row) for row in rows)


def reproduction_verdict(rows: list[dict[str, Any]], value: dict[str, Any] | None = None) -> str:
    value = value or load_definition(); expected = {(case, 8192) for case in value["workload"]["frozen_case_ids"]}
    if not _valid_set(rows, expected): return "invalid_comparison"
    return "compatible" if sum(bool(row["evaluation"]["passed"]) for row in rows) == value["rules"]["reproduction_passes"] else "baseline_drift"


def llama_verdict(untreated: list[dict[str, Any]], ledger: list[dict[str, Any]], value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or load_definition(); expected = {(case, level) for level in value["workload"]["authorized_levels"] for case in value["workload"]["case_ids"]}
    if not _valid_set(untreated, expected) or not _valid_set(ledger, expected): return {"verdict": "invalid_comparison"}
    count = lambda rows, level: sum(bool(row["evaluation"]["passed"]) for row in rows if row["requested_input_tokens"] == level)
    u2, l2, u8, l8 = count(untreated, 2048), count(ledger, 2048), count(untreated, 8192), count(ledger, 8192)
    reference_ok = l2 >= u2 - value["rules"]["llama_reference_max_drop"]
    primary_ok = l8 >= value["rules"]["ledger_minimum"] and l8 - u8 >= value["rules"]["primary_delta_minimum"]
    verdict = "llama_reference_regression" if not reference_ok else "supported_under_bounded_claim" if primary_ok else "unsupported_no_effect_or_insufficient_effect"
    return {"verdict": verdict, "u2": u2, "l2": l2, "delta2": l2-u2, "u8": u8, "l8": l8, "delta8": l8-u8, "reference_ok": reference_ok, "primary_ok": primary_ok}


def llama_verdict_from_runs() -> dict[str, Any]:
    return llama_verdict(read_records("llama_untreated"), read_records("llama_ledger"))


def qwen_verdict(untreated: list[dict[str, Any]], ledger: list[dict[str, Any]] | None, value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or load_definition(); expected = {(case, 8192) for case in value["workload"]["case_ids"]}
    if not _valid_set(untreated, expected): return {"verdict": "invalid_comparison"}
    u = sum(bool(row["evaluation"]["passed"]) for row in untreated)
    if u < value["rules"]["qwen_eligibility"]: return {"verdict": "control_not_qualified", "untreated": u}
    if ledger is None: return {"verdict": "eligible_pending_ledger", "untreated": u}
    if not _valid_set(ledger, expected): return {"verdict": "invalid_comparison"}
    l = sum(bool(row["evaluation"]["passed"]) for row in ledger)
    return {"verdict": "qwen_no_harm_pass" if l >= u-value["rules"]["qwen_max_drop"] else "qwen_regression", "untreated": u, "ledger": l, "delta": l-u}


def qwen_verdict_from_runs() -> dict[str, Any]:
    rows = read_records("qwen_8k_ledger")
    return qwen_verdict(read_records("qwen_8k_untreated"), rows if rows else None)


def execute_fail_fast(rows: list[dict[str, Any]], request: Any) -> list[dict[str, Any]]:
    records = []
    for ordinal, row in enumerate(rows, start=1):
        record = request(ordinal, row); records.append(record)
        if record["completion_status"] in {"infrastructure_failure", "protocol_invalid"}: break
    return records
