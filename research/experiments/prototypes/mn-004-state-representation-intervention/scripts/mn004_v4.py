"""Frozen v4 authority, operational taxonomy, and fail-fast helpers."""
from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import mn004
import mn004_v2
import mn004_v3

DEFINITION = mn004.DEFINITION / "experiment-v4.json"
POSTMORTEM = mn004.ROOT / "reports" / "mn-004-v3-infrastructure-postmortem.md"


def definition() -> dict[str, Any]:
    value = mn004.load_json(DEFINITION)
    if value.get("id") != "mn-004-state-representation-intervention-v4" or value.get("version") != "4.0.0":
        raise mn004.ContractError("unexpected v4 identity")
    return value


def fingerprint(value: dict[str, Any] | None = None) -> str:
    return mn004.sha256_bytes(b"experiment-v4.json\0" + mn004.canonical_json(value or definition()))


def validate_authority(value: dict[str, Any] | None = None) -> dict[str, Any]:
    value = value or definition()
    authority = value["authority"]
    paths = {
        "gate_a_sha256": mn004.ROOT / "gate-a-hypothesis.md",
        "gate_b_v3_sha256": mn004.ROOT / "gate-b-v3-measurement-contract.md",
        "gate_b_v4_sha256": mn004.ROOT / "gate-b-v4-runtime-feasibility-contract.md",
        "v3_postmortem_sha256": POSTMORTEM,
        "v3_definition_sha256": mn004.DEFINITION / "experiment-v3.json",
        "v1_inventory_sha256": mn004.DEFINITION / "source-inventory.json",
        "v1_llama_preflight_sha256": mn004.DEFINITION / "preflight-llama-3.2-3b.json",
    }
    for key, path in paths.items():
        if not path.is_file() or mn004.sha256_file(path) != authority[key]:
            raise mn004.ContractError(f"v4 authority mismatch: {key}")
    v3 = mn004_v3.validate_authority()
    frozen_model = {"key": "llama-3.2-3b", **v3["models"]["llama-3.2-3b"]}
    if value["model"] != frozen_model or value["runtime"] != v3["runtime"]:
        raise mn004.ContractError("v4 changed frozen model/runtime")
    return value


def inventory(value: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    value = validate_authority(value)
    rows = [row for row in mn004_v3.inventory() if row["requested_input_tokens"] == value["workload"]["authorized_level"]]
    expected_ids = value["workload"]["authorized_case_ids"]
    if len(rows) != 24 or [row["case_id"] for row in rows] != expected_ids:
        raise mn004.ContractError("v4 must use exactly the immutable 24-row 8k inventory in retained order")
    return rows


def preflight_pair(row: dict[str, Any], condition: str) -> dict[str, Any]:
    preflight = mn004.load_json(mn004.DEFINITION / "preflight-llama-3.2-3b.json")
    record = mn004_v2.preflight_record(preflight, row)
    pair = record["conditions"][condition]
    if not pair["fits_with_output_allowance"]:
        raise mn004.ContractError("v4 token feasibility mismatch")
    return pair


def validate_offline() -> dict[str, Any]:
    value = validate_authority()
    rows = inventory(value)
    preflight = [preflight_pair(row, condition) for row in rows for condition in ("natural_language", "ledger")]
    if any(pair["actual_prompt_tokens"] + value["runtime"]["output_tokens"] > value["runtime"]["configured_context_size"] for pair in preflight):
        raise mn004.ContractError("v4 retained preflight is not executable")
    return {"v4_definition_fingerprint": fingerprint(value), "authorized_rows": len(rows), "conditions_checked": len(preflight), "status": "valid"}


def run_directories(stage: str) -> list[Path]:
    return sorted(path for path in mn004.RUNS.glob("v4-*") if (path / "metadata.json").is_file() and mn004.load_json(path / "metadata.json").get("stage") == stage)


def latest_summary(stage: str) -> dict[str, Any] | None:
    runs = run_directories(stage)
    return mn004.load_json(runs[-1] / "summary.json") if runs and (runs[-1] / "summary.json").is_file() else None


def stage_allowed(stage: str) -> bool:
    stage_a = latest_summary("stage_a_untreated")
    stage_b = latest_summary("stage_b_ledger")
    c1 = latest_summary("stage_c1_failed_case")
    if stage == "stage_a_untreated":
        return stage_a is None
    if stage == "stage_b_ledger":
        return stage_a is not None and stage_a["operational_outcome"] == "stage_completed" and stage_b is None
    if stage == "stage_c1_failed_case":
        return stage_b is not None and stage_b["operational_outcome"] == "ledger_runtime_failure_reproduced" and c1 is None
    if stage == "stage_c2_predecessor_then_failed_case":
        return c1 is not None and c1["operational_outcome"] == "stage_completed" and c1.get("predecessor_case_id") is not None
    raise mn004.ContractError(f"unknown v4 stage: {stage}")


def execute_fail_fast(rows: list[dict[str, Any]], request: Callable[[int, dict[str, Any]], dict[str, Any]]) -> list[dict[str, Any]]:
    """Run sequentially; a protocol or infrastructure failure is terminal."""
    records: list[dict[str, Any]] = []
    for ordinal, row in enumerate(rows, start=1):
        record = request(ordinal, row)
        records.append(record)
        if record["completion_status"] in {"infrastructure_failure", "protocol_invalid"}:
            break
    return records


def first_failure(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((record for record in records if record["completion_status"] in {"infrastructure_failure", "protocol_invalid"}), None)


def has_resource_signature(record: dict[str, Any] | None) -> bool:
    if not record:
        return False
    evidence = json.dumps(record.get("failure_attachment", {}), ensure_ascii=False).casefold()
    return any(token in evidence for token in ("cuda error", "out of memory", "mul_mat failed", "ggml_cuda", "server_process_exited", "connection reset"))


def phase_outcome(stage: str, records: list[dict[str, Any]], expected: int, contaminated: bool = False) -> str:
    if contaminated:
        return "environment_contaminated"
    failure = first_failure(records)
    if failure and failure["completion_status"] == "protocol_invalid":
        return "protocol_invalid"
    if stage == "stage_a_untreated":
        return "untreated_environment_failure" if failure else "stage_completed" if len(records) == expected else "diagnostic_inconclusive"
    if stage == "stage_b_ledger":
        if not failure and len(records) == expected:
            return "ledger_persistent_phase_completed"
        return "ledger_runtime_failure_reproduced" if has_resource_signature(failure) else "diagnostic_inconclusive"
    if stage in {"stage_c1_failed_case", "stage_c2_predecessor_then_failed_case"}:
        if failure and has_resource_signature(failure):
            return "ledger_runtime_failure_reproduced"
        return "stage_completed" if not failure and len(records) == expected else "diagnostic_inconclusive"
    raise mn004.ContractError(f"unknown v4 stage: {stage}")


def selected_diagnostic_rows() -> tuple[dict[str, Any], dict[str, Any] | None]:
    runs = run_directories("stage_b_ledger")
    if not runs:
        raise mn004.ContractError("Stage C requires retained Stage B evidence")
    rows = [json.loads(line) for line in (runs[-1] / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    failed_index = next((index for index, row in enumerate(rows) if row["completion_status"] == "infrastructure_failure"), None)
    if failed_index is None:
        raise mn004.ContractError("Stage C requires a Stage B infrastructure failure")
    selected = {row["case_id"]: row for row in inventory()}
    failed = selected[rows[failed_index]["case_id"]]
    predecessor = selected[rows[failed_index - 1]["case_id"]] if failed_index else None
    return failed, predecessor
