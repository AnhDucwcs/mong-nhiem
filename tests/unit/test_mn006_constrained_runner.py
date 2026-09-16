from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import run_mn006_baseline as baseline
import run_mn006_constrained_baseline as constrained
from mn006.measurement import (
    EXPECTED_INVENTORY_SHA256,
    build_request_plan,
    validate_attempt_directory,
)
from mn006.response_channel import (
    FIXED_ANSWER_GRAMMAR,
    GRAMMAR_FIELD,
    validate_constrained_payload,
)

ATTEMPT_0001 = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
    / "runs"
    / "attempt-0001"
)
INVENTORY = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
    / "definition"
    / "baseline-inventory-v1"
)


def _retained_rows() -> dict[str, dict[str, object]]:
    return {
        row["case_id"]: row
        for row in (
            json.loads(line)
            for line in (ATTEMPT_0001 / "results.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }


def test_attempt_0002_contract_records_frozen_identity() -> None:
    assert constrained.ATTEMPT_ID == "attempt-0002"
    assert constrained.ATTEMPT_CONTRACT == {
        "attempt_id": "attempt-0002",
        "evaluator_version": "mn006-evaluator-v1",
        "expected_inventory_sha256": EXPECTED_INVENTORY_SHA256,
        "expected_model_subject": "llama-3.2-3b",
        "parser_version": "mn006-answer-parser-v1",
        "response_channel_contract_version": "mn006-response-channel-grammar-v1",
        "response_grammar": 'root ::= "VALID" | "INVALID"\n',
        "runtime_contract_version": "mn006-baseline-runtime-v1",
    }


def test_all_payloads_change_only_grammar_and_reuse_public_bytes() -> None:
    manifest, plan = build_request_plan()
    retained = _retained_rows()
    assert manifest["aggregate_inventory_sha256"] == EXPECTED_INVENTORY_SHA256
    assert len(plan) == len(retained) == 128
    for entry in plan:
        prompt_bytes = (INVENTORY / entry["public_prompt_path"]).read_bytes()
        baseline_payload = baseline.build_request_payload(prompt_bytes)
        future_payload = constrained.build_request_payload(prompt_bytes)
        assert retained[entry["case_id"]]["raw_request_payload"] == baseline_payload
        validate_constrained_payload(baseline_payload, future_payload)
        assert future_payload["messages"] == baseline_payload["messages"]
        assert future_payload["messages"][0]["content"].encode("utf-8") == prompt_bytes
        assert future_payload[GRAMMAR_FIELD] == FIXED_ANSWER_GRAMMAR


def test_order_runtime_and_historical_evidence_remain_frozen() -> None:
    _manifest, plan = build_request_plan()
    assert [entry["request_ordinal"] for entry in plan] == list(range(1, 129))
    assert [entry["profile"] for entry in plan[:64]] == [
        "level_1_light_interleaved"
    ] * 64
    assert [entry["profile"] for entry in plan[64:]] == [
        "level_2_primary_interleaved"
    ] * 64
    for offset in range(0, 128, 2):
        first, second = plan[offset : offset + 2]
        expected = (
            ("contiguous_control", "interleaved")
            if first["underlying_case_ordinal"] % 2 == 0
            else ("interleaved", "contiguous_control")
        )
        assert (first["schedule_kind"], second["schedule_kind"]) == expected
    assert baseline.INFERENCE["output_tokens"] == 16
    assert baseline.INFERENCE["temperature"] == 0.0
    assert "--grammar" not in baseline.server_command(
        Path("llama-server"), Path("model.gguf")
    )
    assert validate_attempt_directory(ATTEMPT_0001)["outcome"] == "protocol_valid"


def test_grammar_has_no_case_specific_state_or_answer_selection() -> None:
    grammar = FIXED_ANSWER_GRAMMAR
    assert grammar.split('"')[1::2] == ["VALID", "INVALID"]
    assert not any(
        token in grammar
        for token in ("E01", "E08", "S0", "S1", "S2", "equal_state", "mn006-v1")
    )
