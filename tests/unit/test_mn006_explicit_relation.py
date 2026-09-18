from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from mn006 import explicit_relation
from mn006.explicit_relation_execution import validate_run_directory
from mn006.fingerprinting import canonical_json_bytes
from mn006.label_selection import GRAMMAR_AB, parse_label
from mn006.label_selection_execution import validate_d1_run_directory
from mn006.measurement import validate_attempt_directory
from mn006.output_selection_execution import validate_s0_run_directory
from mn006.output_selection_s1_execution import validate_s1_run_directory

BASE = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration"
PLAN = BASE / "definition" / "explicit-relation-direct-rule-v1" / "plan.json"
REVIEW = BASE / "recurring-fixed-label-causal-review.md"
RUNS = BASE / "runs"


def _outputs(values: tuple[str, str]) -> dict[str, str]:
    cases = explicit_relation.build_plan()
    return {case.record_id: value for case, value in zip(cases, values, strict=True)}


def _records(values: tuple[str, str], *, status: str = "complete") -> list[dict[str, object]]:
    return [
        {
            "infrastructure_status": status,
            "raw_output": value,
            "record_id": case.record_id,
            "request_ordinal": case.request_ordinal,
        }
        for case, value in zip(explicit_relation.build_plan(), values, strict=True)
    ]


def test_frozen_identity_authority_bytes_and_review_prerequisite() -> None:
    assert explicit_relation.CONTRACT_VERSION == "mn006-explicit-relation-direct-rule-v1"
    assert explicit_relation.RUN_ID == "explicit-relation-direct-rule-run-0001"
    assert explicit_relation.EXPECTED_PLAN_SHA256 == "dc40c15a896f5f0413783818c39593b8a9c34eeea3ef4ce284e1b311112bc80a"
    assert hashlib.sha256(PLAN.read_bytes()).hexdigest() == explicit_relation.EXPECTED_PLAN_SHA256
    assert PLAN.read_bytes() == canonical_json_bytes(explicit_relation.validate_frozen_plan())
    assert hashlib.sha256(REVIEW.read_bytes()).hexdigest() == explicit_relation.EXPECTED_CAUSAL_REVIEW_SHA256


def test_two_record_matrix_order_prompts_and_grammar_are_exact() -> None:
    cases = explicit_relation.build_plan()
    assert len(cases) == 2
    assert [case.request_ordinal for case in cases] == [1, 2]
    assert [case.relation for case in cases] == ["different", "equal"]
    assert [case.canonical_answer for case in cases] == ["B", "A"]
    assert [case.grammar for case in cases] == [GRAMMAR_AB, GRAMMAR_AB]
    assert cases[0].public_prompt == (
        "Relation: different\n"
        "Output A if the relation is equal.\n"
        "Output B if the relation is different.\n"
        "Output exactly one label: A or B.\n"
    )
    assert cases[1].public_prompt == cases[0].public_prompt.replace("Relation: different", "Relation: equal", 1)


def test_prompts_remove_state_comparison_and_do_not_collapse_into_s0_copying() -> None:
    forbidden = (
        "Target label",
        "correct label",
        "E01 STATE",
        "E02 STATE",
        "All entities begin",
        "use this mapping",
        "example",
        "demonstration",
    )
    for case in explicit_relation.build_plan():
        assert all(token.lower() not in case.public_prompt.lower() for token in forbidden)
        assert case.public_prompt.count("Relation:") == 1
        assert case.public_prompt.endswith("\n") and "\r\n" not in case.public_prompt


def test_strict_parser_is_reused_without_relaxation() -> None:
    cases = explicit_relation.build_plan()
    assert explicit_relation.score(cases[0], " B \n") == {
        "correct": True,
        "malformed": False,
        "parsed_answer": "B",
    }
    for value in ("a", "b", "A.", "Answer: A", "A B", "VALID", ""):
        assert parse_label(value) is None


def test_classifier_precedence_and_complete_semantic_patterns() -> None:
    assert explicit_relation.classify(_outputs(("A.", "A"))) == "explicit_relation_malformed_or_invalid"
    assert explicit_relation.classify(_outputs(("B", "A"))) == "explicit_relation_direct_rule_supported"
    assert explicit_relation.classify(_outputs(("A", "A"))) == "fixed_label_preference_persisted"
    assert explicit_relation.classify(_outputs(("B", "B"))) == "explicit_relation_inconclusive"
    assert explicit_relation.classify(_outputs(("A", "B"))) == "explicit_relation_inconclusive"


def test_classifier_rejects_missing_or_unknown_authority_cells() -> None:
    cases = explicit_relation.build_plan()
    with pytest.raises(explicit_relation.ExplicitRelationError, match="two-record plan"):
        explicit_relation.classify({cases[0].record_id: "B"})
    with pytest.raises(explicit_relation.ExplicitRelationError, match="two-record plan"):
        explicit_relation.classify({**_outputs(("B", "A")), "unknown": "A"})


def test_infrastructure_invalidity_precedes_semantic_classification() -> None:
    assert explicit_relation.summarize_records(_records(("B", "A"))[:-1]) == {
        "classification": None,
        "outcome": "infrastructure_invalid",
    }
    assert explicit_relation.summarize_records(_records(("B", "A"), status="failed")) == {
        "classification": None,
        "outcome": "infrastructure_invalid",
    }
    assert explicit_relation.summarize_records(_records(("B", "A"))) == {
        "classification": "explicit_relation_direct_rule_supported",
        "outcome": "protocol_valid",
    }


def test_prerequisite_evidence_and_canonical_run_are_valid() -> None:
    assert validate_s0_run_directory(RUNS / "output-selection-s0-run-0001")["classification"] == "direct_copy_supported"
    assert validate_s1_run_directory(RUNS / "output-selection-s1-run-0001")["classification"] == "fixed_label_preference_recurred"
    assert validate_d1_run_directory(RUNS / "label-selection-d1-run-0001")["classification"] == "fixed_label_preference_supported"
    assert validate_attempt_directory(RUNS / "attempt-0001", attempt_id="attempt-0001")["outcome"] == "protocol_valid"
    assert validate_attempt_directory(RUNS / "attempt-0002", attempt_id="attempt-0002")["outcome"] == "protocol_valid"
    assert validate_run_directory(RUNS / explicit_relation.RUN_ID)["classification"] == "fixed_label_preference_persisted"
    assert not (RUNS / "attempt-0003").exists()
    assert (SCRIPTS / "run_mn006_explicit_relation_direct_rule.py").is_file()


def test_plan_prerequisites_freeze_s0_s1_and_keep_d1_as_context_only() -> None:
    authority = json.loads(PLAN.read_bytes())
    assert authority["prerequisites"]["s0"] == {
        "classification": "direct_copy_supported",
        "outcome": "protocol_valid",
        "run_id": "output-selection-s0-run-0001",
    }
    assert authority["prerequisites"]["s1"] == {
        "classification": "fixed_label_preference_recurred",
        "outcome": "protocol_valid",
        "run_id": "output-selection-s1-run-0001",
    }
    assert authority["retained_context"]["d1"]["execution_prerequisite"] is False
