from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from mn006.measurement import EXPECTED_INVENTORY_SHA256, build_request_plan
from mn006.response_channel import (
    FIXED_ANSWER_GRAMMAR,
    GRAMMAR_FIELD,
    RESPONSE_CHANNEL_CONTRACT_VERSION,
    ResponseChannelError,
    constrained_payload,
    validate_constrained_payload,
)

ATTEMPT = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
    / "runs"
    / "attempt-0001"
)


def test_frozen_grammar_is_the_two_label_language_only() -> None:
    assert RESPONSE_CHANNEL_CONTRACT_VERSION == "mn006-response-channel-grammar-v1"
    assert FIXED_ANSWER_GRAMMAR == 'root ::= "VALID" | "INVALID"\n'


def test_constraint_changes_only_the_response_language() -> None:
    baseline = {
        "messages": [{"role": "user", "content": "public prompt\n"}],
        "temperature": 0.0,
        "seed": 42,
        "max_tokens": 16,
        "chat_template_kwargs": {},
    }
    candidate = constrained_payload(baseline)
    assert candidate[GRAMMAR_FIELD] == FIXED_ANSWER_GRAMMAR
    validate_constrained_payload(baseline, candidate)
    candidate["max_tokens"] = 17
    with pytest.raises(ResponseChannelError, match="non-grammar"):
        validate_constrained_payload(baseline, candidate)


def test_all_retained_baseline_payloads_map_to_one_identical_grammar() -> None:
    rows = [
        json.loads(line)
        for line in (ATTEMPT / "results.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(rows) == 128
    grammars = set()
    for row in rows:
        baseline = row["raw_request_payload"]
        candidate = constrained_payload(baseline)
        validate_constrained_payload(baseline, candidate)
        assert candidate["messages"] == baseline["messages"]
        grammars.add(candidate[GRAMMAR_FIELD])
    assert grammars == {FIXED_ANSWER_GRAMMAR}


def test_frozen_inventory_and_public_prompt_identity_remain_unchanged() -> None:
    manifest, plan = build_request_plan()
    assert manifest["aggregate_inventory_sha256"] == EXPECTED_INVENTORY_SHA256
    assert len(plan) == 128
    for entry in plan:
        prompt = (
            ROOT
            / "research"
            / "experiments"
            / "prototypes"
            / "mn-006-distributed-state-integration"
            / "definition"
            / "baseline-inventory-v1"
            / entry["public_prompt_path"]
        ).read_bytes()
        retained = next(
            row
            for row in [
                json.loads(line)
                for line in (ATTEMPT / "results.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            if row["case_id"] == entry["case_id"]
        )
        assert retained["raw_request_payload"]["messages"][0]["content"].encode("utf-8") == prompt
