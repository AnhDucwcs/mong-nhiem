import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-004-state-representation-intervention" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mn004_v3
import mn004_v5


def record(case: str, level: int, passed: bool = False, *, valid: bool = True, status: str = "complete") -> dict:
    return {"case_id": case, "requested_input_tokens": level, "completion_status": status, "protocol_valid": valid, "infrastructure_status": "complete" if status == "complete" else "failed", "validator_status": "valid" if valid and status == "complete" else "invalid", "input_truncated": not valid, "evaluation": {"passed": passed, "score": float(passed)}}


def complete_rows(passes: dict[tuple[str, int], bool] | None = None) -> list[dict]:
    return [record(row["case_id"], row["requested_input_tokens"], bool((passes or {}).get((row["case_id"], row["requested_input_tokens"])))) for row in mn004_v5.inventory()]


def test_definition_fingerprint_is_deterministic() -> None:
    assert mn004_v5.fingerprint() == mn004_v5.fingerprint(mn004_v5.load_definition())


def test_authorized_inventory_is_exactly_2k_and_8k() -> None:
    rows = mn004_v5.inventory()
    assert len(rows) == 48 and [row["requested_input_tokens"] for row in rows[:24]] == [2048] * 24 and [row["requested_input_tokens"] for row in rows[24:]] == [8192] * 24


def test_reproduction_zero_permits_untreated() -> None:
    rows = [record(row["case_id"], 8192) for row in mn004_v5.phase_rows("llama_8k_reproduction")]
    assert mn004_v5.reproduction_verdict(rows) == "compatible"


def test_reproduction_nonzero_is_baseline_drift() -> None:
    rows = [record(row["case_id"], 8192, passed=index == 0) for index, row in enumerate(mn004_v5.phase_rows("llama_8k_reproduction"))]
    assert mn004_v5.reproduction_verdict(rows) == "baseline_drift"


def test_malformed_response_is_valid_zero() -> None:
    row = mn004_v5.inventory()[0]
    value = mn004_v3.classify_response(row, "not a state", {"choices": [{"finish_reason": "stop"}]}, None)
    assert value["validity"] == "valid" and not value["passed"] and value["failure_class"] == "malformed_response"


def test_output_limit_is_valid_zero() -> None:
    row = mn004_v5.inventory()[0]
    value = mn004_v3.classify_response(row, row["expected_answer"], {"choices": [{"finish_reason": "length"}]}, None)
    assert value["validity"] == "valid" and not value["passed"] and value["output_limit_reached"] and value["failure_class"] == "output_token_limit_reached"


def test_input_truncation_is_invalid() -> None:
    assert not mn004_v5.record_is_valid(record("a", 8192, valid=False))


def test_infrastructure_failure_stops_immediately() -> None:
    attempted: list[int] = []
    records = mn004_v5.execute_fail_fast([{}, {}, {}], lambda ordinal, _row: attempted.append(ordinal) or {"completion_status": "infrastructure_failure" if ordinal == 2 else "complete"})
    assert attempted == [1, 2] and len(records) == 2


def test_protocol_failure_stops_immediately() -> None:
    records = mn004_v5.execute_fail_fast([{}, {}], lambda _ordinal, _row: {"completion_status": "protocol_invalid"})
    assert len(records) == 1


def test_later_model_output_failure_does_not_stop_phase() -> None:
    records = mn004_v5.execute_fail_fast([{}, {}], lambda _ordinal, _row: {"completion_status": "complete", "failure_class": "output_token_limit_reached"})
    assert len(records) == 2


def test_primary_threshold_passes_exactly_at_boundary() -> None:
    rows = mn004_v5.inventory(); u = complete_rows(); chosen = {(row["case_id"], 8192) for row in rows[24:36]}; l = complete_rows({key: True for key in chosen})
    result = mn004_v5.llama_verdict(u, l)
    assert result["l8"] == 12 and result["delta8"] == 12 and result["verdict"] == "supported_under_bounded_claim"


def test_primary_delta_threshold_missing_fails_support() -> None:
    rows = mn004_v5.inventory(); u_keys = {(row["case_id"], 8192) for row in rows[24:30]}; l_keys = {(row["case_id"], 8192) for row in rows[24:36]}; result = mn004_v5.llama_verdict(complete_rows({key: True for key in u_keys}), complete_rows({key: True for key in l_keys}))
    assert result["l8"] == 12 and result["delta8"] == 6 and result["verdict"] == "unsupported_no_effect_or_insufficient_effect"


def test_primary_pass_count_missing_fails_support() -> None:
    l_keys = {(row["case_id"], 8192) for row in mn004_v5.inventory()[24:35]}
    assert mn004_v5.llama_verdict(complete_rows(), complete_rows({key: True for key in l_keys}))["verdict"] == "unsupported_no_effect_or_insufficient_effect"


def test_2k_decline_above_two_is_reference_regression() -> None:
    u_keys = {(row["case_id"], 2048) for row in mn004_v5.inventory()[:6]}; result = mn004_v5.llama_verdict(complete_rows({key: True for key in u_keys}), complete_rows())
    assert result["verdict"] == "llama_reference_regression"


def test_qwen_untreated_below_eligibility_blocks_ledger() -> None:
    rows = [record(row["case_id"], 8192, passed=index < 19) for index, row in enumerate(mn004_v5.phase_rows("qwen_8k_untreated"))]
    assert mn004_v5.qwen_verdict(rows, None)["verdict"] == "control_not_qualified"


def test_qwen_drop_above_two_is_regression() -> None:
    rows = mn004_v5.phase_rows("qwen_8k_untreated"); untreated = [record(row["case_id"],8192,True) for row in rows]; ledger = [record(row["case_id"],8192,index < 21) for index,row in enumerate(rows)]
    assert mn004_v5.qwen_verdict(untreated, ledger)["verdict"] == "qwen_regression"


def test_qwen_is_not_an_improvement_subject() -> None:
    rows = mn004_v5.phase_rows("qwen_8k_untreated"); untreated = [record(row["case_id"],8192,True) for row in rows]; ledger = [record(row["case_id"],8192,True) for row in rows]
    assert mn004_v5.qwen_verdict(untreated, ledger)["verdict"] == "qwen_no_harm_pass"


def test_reproduction_phase_has_only_frozen_8k_rows() -> None:
    rows = mn004_v5.phase_rows("llama_8k_reproduction")
    assert len(rows) == 6 and {row["origin"] for row in rows} == {"frozen"} and {row["requested_input_tokens"] for row in rows} == {8192}


def test_qwen_has_only_8k_rows() -> None:
    assert {row["requested_input_tokens"] for row in mn004_v5.phase_rows("qwen_8k_untreated")} == {8192}


def test_legacy_runs_cannot_supply_v5_records(tmp_path: Path, monkeypatch) -> None:
    legacy = tmp_path / "v4-legacy"; legacy.mkdir(); (legacy / "metadata.json").write_text('{"phase":"llama_untreated"}', encoding="utf-8")
    monkeypatch.setattr(mn004_v5.mn004, "RUNS", tmp_path)
    assert mn004_v5.run_directories("llama_untreated") == []
