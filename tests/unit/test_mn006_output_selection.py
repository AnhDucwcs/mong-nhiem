from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

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

from mn006 import output_selection as minimality
from mn006.fingerprinting import canonical_json_bytes
from mn006.label_selection import GRAMMAR_AB, GRAMMAR_BA, parse_label
from mn006.label_selection_execution import validate_d1_run_directory
from mn006.output_selection_execution import validate_s0_run_directory
from mn006.output_selection_s1_execution import validate_s1_run_directory

DEFINITION = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
    / "definition"
    / "output-selection-minimality-v1"
)
RUNS = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration" / "runs"


def test_frozen_contract_and_canonical_static_plan() -> None:
    plan_path = DEFINITION / "plan.json"
    audit_path = DEFINITION / "static-audit.json"
    assert minimality.CONTRACT_VERSION == "mn006-output-selection-minimality-v1"
    assert minimality.EXPECTED_PLAN_SHA256 == "8180ea423a05eeb2930b84cee6102fd94595e13856f1a91e1afe4d599bb8e827"
    assert minimality.plan_fingerprint() == minimality.EXPECTED_PLAN_SHA256
    assert plan_path.read_bytes() == canonical_json_bytes(minimality.validate_frozen_plan())
    audit = json.loads(audit_path.read_bytes())
    assert audit["diagnostic_plan_sha256"] == minimality.EXPECTED_PLAN_SHA256
    assert audit["logprob_capability_audit"]["decision"] == "deferred"


def test_s0_matrix_prompt_grammar_and_order_are_exact() -> None:
    cases = minimality.build_s0_plan()
    assert len(cases) == 4
    assert [case.request_ordinal for case in cases] == [1, 2, 3, 4]
    assert [case.target_label for case in cases] == ["A", "B", "B", "A"]
    assert [case.grammar_order for case in cases] == ["A_then_B", "B_then_A", "A_then_B", "B_then_A"]
    assert [case.grammar for case in cases] == [GRAMMAR_AB, GRAMMAR_BA, GRAMMAR_AB, GRAMMAR_BA]
    assert all(case.query_states is None and case.equal_state is None for case in cases)
    assert cases[0].public_prompt == "Target label: A\nOutput exactly the target label.\nAllowed labels: A or B.\n"
    assert cases[1].public_prompt == "Target label: B\nOutput exactly the target label.\nAllowed labels: A or B.\n"
    for target in ("A", "B"):
        paired = [case for case in cases if case.target_label == target]
        assert {case.grammar_order for case in paired} == {"A_then_B", "B_then_A"}
        assert all(case.canonical_answer == target for case in paired)
        assert all(case.public_prompt.endswith("\n") and "\r\n" not in case.public_prompt for case in paired)


def test_s0_parser_reuses_the_frozen_strict_ab_boundary() -> None:
    assert minimality.score(minimality.build_s0_plan()[0], " A \n") == {
        "correct": True,
        "malformed": False,
        "parsed_answer": "A",
    }
    assert parse_label("B") == "B"
    for value in ("a", "b", "A.", "Answer: A", "A B", "VALID", ""):
        assert parse_label(value) is None


def test_s0_classification_precedence_and_fixtures() -> None:
    cases = minimality.build_s0_plan()
    correct = {case.record_id: case.canonical_answer for case in cases}
    assert minimality.classify_s0(correct) == "direct_copy_supported"
    all_a = {case.record_id: "A" for case in cases}
    assert minimality.classify_s0(all_a) == "fixed_label_preference_persisted"
    order_sensitive = {case.record_id: ("A" if case.grammar_order == "A_then_B" else "B") for case in cases}
    assert minimality.classify_s0(order_sensitive) == "grammar_order_asymmetry_observed"
    malformed = dict(correct)
    malformed[cases[0].record_id] = "A."
    assert minimality.classify_s0(malformed) == "direct_copy_malformed_or_invalid"
    mixed = {case.record_id: ("B" if case.target_label == "A" else "A") for case in cases}
    assert minimality.classify_s0(mixed) == "direct_copy_inconclusive"


def test_s1_is_strictly_blocked_unless_s0_passes() -> None:
    for outcome in (
        "grammar_order_asymmetry_observed",
        "fixed_label_preference_persisted",
        "direct_copy_inconclusive",
        "direct_copy_malformed_or_invalid",
    ):
        assert minimality.s1_eligible(outcome) is False
        with pytest.raises(minimality.OutputSelectionError, match="blocked"):
            minimality.require_s1_eligibility(outcome)
    assert minimality.s1_eligible("direct_copy_supported") is True


def test_s1_direct_relation_rule_is_small_balanced_and_has_no_grammar_factor() -> None:
    cases = minimality.build_s1_plan()
    assert len(cases) == 4
    assert [case.request_ordinal for case in cases] == [1, 2, 3, 4]
    assert [case.query_states for case in cases] == [("S1", "S2"), ("S1", "S1"), ("S2", "S2"), ("S2", "S1")]
    assert [case.canonical_answer for case in cases] == ["B", "A", "A", "B"]
    assert sum(bool(case.equal_state) for case in cases) == 2
    assert {case.grammar_order for case in cases} == {"A_then_B"}
    assert all(case.grammar == GRAMMAR_AB for case in cases)
    assert all(case.target_label is None for case in cases)
    assert all("Target label" not in case.public_prompt for case in cases)
    assert all("mapping" not in case.public_prompt.lower() for case in cases)
    assert cases[0].public_prompt == (
        "E01 STATE = S1\nE02 STATE = S2\nOutput A if the states are equal.\n"
        "Output B if the states are different.\nOutput exactly one label: A or B.\n"
    )


def test_s1_classification_and_eligibility_enforcement() -> None:
    cases = minimality.build_s1_plan()
    correct = {case.record_id: case.canonical_answer for case in cases}
    assert minimality.classify_s1(correct, s0_classification="direct_copy_supported") == "direct_relation_supported"
    assert minimality.classify_s1({case.record_id: "A" for case in cases}, s0_classification="direct_copy_supported") == "fixed_label_preference_recurred"
    malformed = dict(correct)
    malformed[cases[0].record_id] = "A."
    assert minimality.classify_s1(malformed, s0_classification="direct_copy_supported") == "direct_relation_malformed_or_invalid"
    mixed = {case.record_id: ("A" if case.request_ordinal in (1, 2, 4) else "B") for case in cases}
    assert minimality.classify_s1(mixed, s0_classification="direct_copy_supported") == "direct_relation_inconclusive"
    with pytest.raises(minimality.OutputSelectionError, match="blocked"):
        minimality.classify_s1(correct, s0_classification="fixed_label_preference_persisted")


def test_prior_d1_s0_and_s1_evidence_are_intact_and_no_unauthorized_future_runs_exist() -> None:
    d1_dir = RUNS / "label-selection-d1-run-0001"
    integrity = json.loads((d1_dir / "integrity.json").read_bytes())
    for relative, expected in integrity["artifact_sha256"].items():
        assert hashlib.sha256((d1_dir / relative).read_bytes()).hexdigest() == expected
    assert validate_d1_run_directory(d1_dir)["classification"] == "fixed_label_preference_supported"
    s0_dir = RUNS / minimality.S0_RUN_ID
    assert validate_s0_run_directory(s0_dir)["classification"] == "direct_copy_supported"
    s1_dir = RUNS / minimality.S1_RUN_ID
    assert validate_s1_run_directory(s1_dir)["classification"] == "fixed_label_preference_recurred"
    assert not (RUNS / "attempt-0003").exists()
