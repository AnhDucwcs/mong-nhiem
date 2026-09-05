import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-004-state-representation-intervention" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mn004_v3


def source_row() -> dict:
    return mn004_v3.inventory()[0]


def response(finish_reason: str, content: str) -> dict:
    return {"choices": [{"finish_reason": finish_reason, "message": {"content": content}}]}


def valid_record(**overrides: object) -> dict:
    record = {"case_id": "x", "requested_input_tokens": 8192, "evaluation": {"passed": False}, "protocol_valid": True, "infrastructure_status": "complete", "validator_status": "valid", "input_truncated": False}
    record.update(overrides)
    return record


def test_output_limit_is_valid_zero_scored_model_failure() -> None:
    result = mn004_v3.classify_response(source_row(), "an unfinished answer", response("length", "an unfinished answer"), None)
    assert result["failure_class"] == "output_token_limit_reached"
    assert result["output_limit_reached"] is True
    assert result["passed"] is False
    assert mn004_v3.record_is_valid(valid_record())


def test_malformed_output_is_valid_zero_scored_model_failure() -> None:
    result = mn004_v3.classify_response(source_row(), "answer: GREEN", response("stop", "answer: GREEN"), None)
    assert result["failure_class"] == "malformed_response"
    assert result["passed"] is False


def test_input_or_protocol_invalidity_blocks_validity() -> None:
    assert not mn004_v3.record_is_valid(valid_record(input_truncated=True))
    assert not mn004_v3.record_is_valid(valid_record(protocol_valid=False))


def test_infrastructure_failure_is_not_model_output_failure() -> None:
    result = mn004_v3.classify_response(source_row(), "", None, {"type": "request_error"})
    assert result["validity"] == "infrastructure_failure"
    assert result["failure_class"] == "infrastructure_failure"


def test_paired_metrics_keep_valid_zero_rows_in_denominator() -> None:
    value = mn004_v3.load_definition(); rows = []
    for level in (2048, 8192):
        for case_id in value["workload"]["case_ids"]:
            rows.append(valid_record(case_id=case_id, requested_input_tokens=level))
    verdict = mn004_v3.llama_verdict(rows, rows)
    assert verdict["u8"] == 0 and verdict["l8"] == 0
    assert verdict["verdict"] == "unsupported_no_effect_or_insufficient_effect"
