from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from mn006 import direct_state_vector as vector
from mn006.explicit_relation_execution import validate_run_directory
from mn006.label_selection_execution import validate_d1_run_directory
from mn006.measurement import validate_attempt_directory
from mn006.oracle import replay
from mn006.output_selection_execution import validate_s0_run_directory
from mn006.output_selection_s1_execution import validate_s1_run_directory

BASE = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration"
PLAN = BASE / "definition" / "direct-state-vector-qualification-v1" / "plan.json"
RUNS = BASE / "runs"


def _outputs(*, wrong_ordinal: int | None = None, malformed_ordinal: int | None = None) -> dict[str, str]:
    output: dict[str, str] = {}
    for case in vector.build_plan():
        if case.request_ordinal == malformed_ordinal:
            output[case.record_id] = "S0, S1"
        elif case.request_ordinal == wrong_ordinal:
            output[case.record_id] = vector.vector_text(("S2", "S2")) if case.expected_vector != ("S2", "S2") else "S0,S0"
        else:
            output[case.record_id] = vector.vector_text(case.expected_vector)
    return output


def _records(*, status: str = "complete") -> list[dict[str, object]]:
    return [
        {
            "infrastructure_status": status,
            "raw_output": vector.vector_text(case.expected_vector),
            "record_id": case.record_id,
            "request_ordinal": case.request_ordinal,
        }
        for case in vector.build_plan()
    ]


def test_frozen_authority_identity_and_physical_bytes() -> None:
    assert vector.CONTRACT_VERSION == "mn006-direct-state-vector-interface-v1"
    assert vector.QUALIFICATION_CONTRACT_VERSION == "mn006-direct-state-vector-qualification-v1"
    assert vector.RUN_ID == "direct-state-vector-qualification-run-0001"
    assert vector.EXPECTED_PLAN_SHA256 == "5a487200b0dd72275d37482bc0c3c5cd09feed483419223005519b5034064bbc"
    assert hashlib.sha256(PLAN.read_bytes()).hexdigest() == vector.EXPECTED_PLAN_SHA256
    assert PLAN.read_bytes() == vector.canonical_json_bytes(vector.validate_frozen_plan())


def test_three_by_three_ordered_vector_coverage_is_exact_in_both_layers() -> None:
    q0 = vector.build_q0_plan()
    q1 = vector.build_q1_plan()
    expected = (
        ("S0", "S0"), ("S0", "S1"), ("S0", "S2"),
        ("S1", "S0"), ("S1", "S1"), ("S1", "S2"),
        ("S2", "S0"), ("S2", "S1"), ("S2", "S2"),
    )
    assert vector.STATE_VOCABULARY == ("S0", "S1", "S2")
    assert vector.VECTOR_ORDER == expected
    assert [case.expected_vector for case in q0] == list(expected)
    assert [case.expected_vector for case in q1] == list(expected)
    assert [case.request_ordinal for case in q0] == list(range(1, 10))
    assert [case.request_ordinal for case in q1] == list(range(10, 19))
    assert {("S0", "S0"), ("S1", "S1"), ("S2", "S2")} <= set(expected)
    assert {("S0", "S1"), ("S1", "S0"), ("S0", "S2"), ("S2", "S0"), ("S1", "S2"), ("S2", "S1")} <= set(expected)


def test_bare_vector_grammar_and_parser_are_exact() -> None:
    assert vector.DIRECT_STATE_VECTOR_GRAMMAR == 'root ::= state "," state\nstate ::= "S0" | "S1" | "S2"\n'
    assert vector.DIRECT_STATE_VECTOR_GRAMMAR.endswith("\n")
    for cell in vector.VECTOR_ORDER:
        assert vector.parse_vector(vector.vector_text(cell)) == cell
    for raw in ("S0", "S0, S1", "S0,S1,", "E01=S0,E02=S1", "s0,S1", "S0,S3", "S0,S1 explanation", "VALID,INVALID", ""):
        assert vector.parse_vector(raw) is None


def test_q0_exposes_values_and_position_not_serialized_answer_bytes() -> None:
    for case in vector.build_q0_plan():
        assert case.source is None
        assert vector.vector_text(case.expected_vector) not in case.public_prompt
        assert "First query state:" in case.public_prompt
        assert "Second query state:" in case.public_prompt
        assert case.public_prompt.endswith("\n") and "\r\n" not in case.public_prompt
        assert all(token not in case.public_prompt for token in ("VALID", "INVALID", "equal", "different", "A", "B"))


def test_q1_replays_contiguous_qualification_sources_without_v1_adapter() -> None:
    for case in vector.build_q1_plan():
        source = case.source
        assert source is not None
        assert len(source.source_events) == 24
        assert all(event.entity_id == source.entity_permutation[(event.global_ordinal - 1) // 3] for event in source.source_events)
        replayed = replay(source.source_events, vector.ENTITY_IDS)
        assert tuple(replayed.entity_states[entity] for entity in source.query_entities) == case.expected_vector
        assert vector.vector_text(case.expected_vector) not in case.public_prompt
        assert "For " in case.public_prompt and "in this order." in case.public_prompt
        assert all(token not in case.public_prompt.casefold() for token in ("equal", "different", "valid", "invalid", "mapping", "canonical"))
        assert "E01 STATE =" in case.public_prompt or "E02 STATE =" in case.public_prompt


def test_q1_no_leakage_audit_has_balanced_frequency_and_mixed_query_source_order() -> None:
    audit = vector.q1_no_leakage_audit()
    assert audit["answer_vector_not_serialized_in_prompt"] is True
    assert audit["authority_metadata_not_rendered"] is True
    assert audit["state_frequency_signature"] == [[("S0", 8), ("S1", 8), ("S2", 8)]]
    assert audit["state_frequency_uniquely_identifies_vector"] is False
    assert audit["first_query_before_second_count"] == 3
    assert audit["second_query_before_first_count"] == 6
    assert audit["query_order_matches_event_order"] is False
    assert audit["unmarked_latest_assignment_recovery_is_legitimate"] is True


def test_exact_qualification_requires_all_eighteen_cells() -> None:
    qualified = vector.classify_results(_outputs())
    assert qualified["classification"] == "direct_state_vector_interface_qualified"
    assert qualified["qualification_status"] == "exact_qualification_success"
    assert qualified["layers"]["Q0"] == {"correct": 9, "expected": 9, "malformed": 0}
    assert qualified["layers"]["Q1"] == {"correct": 9, "expected": 9, "malformed": 0}
    failed = vector.classify_results(_outputs(wrong_ordinal=18))
    assert failed["classification"] == "direct_state_vector_interface_blocked"
    assert failed["qualification_status"] == "exact_qualification_failure"
    malformed = vector.classify_results(_outputs(malformed_ordinal=1))
    assert malformed["classification"] == "direct_state_vector_interface_blocked"
    assert malformed["qualification_status"] == "malformed_or_serialization_invalid"


def test_infrastructure_invalidity_remains_outside_semantic_qualification() -> None:
    assert vector.summarize_records(_records()[:-1]) == {
        "classification": None,
        "outcome": "infrastructure_invalid",
        "qualification_status": "infrastructure_invalid",
    }
    assert vector.summarize_records(_records(status="failed")) == {
        "classification": None,
        "outcome": "infrastructure_invalid",
        "qualification_status": "infrastructure_invalid",
    }


def test_plan_validation_rejects_wrong_order_or_noncanonical_layer_size() -> None:
    cases = vector.build_plan()
    with pytest.raises(vector.DirectStateVectorError, match="request order"):
        vector.validate_plan((cases[1], cases[0], *cases[2:]))
    with pytest.raises(vector.DirectStateVectorError, match="eighteen"):
        vector.validate_plan(cases[:-1])


def test_retained_evidence_is_valid_and_no_new_qualification_run_or_executor_exists() -> None:
    assert validate_s0_run_directory(RUNS / "output-selection-s0-run-0001")["classification"] == "direct_copy_supported"
    assert validate_s1_run_directory(RUNS / "output-selection-s1-run-0001")["classification"] == "fixed_label_preference_recurred"
    assert validate_d1_run_directory(RUNS / "label-selection-d1-run-0001")["classification"] == "fixed_label_preference_supported"
    assert validate_attempt_directory(RUNS / "attempt-0001", attempt_id="attempt-0001")["outcome"] == "protocol_valid"
    assert validate_attempt_directory(RUNS / "attempt-0002", attempt_id="attempt-0002")["outcome"] == "protocol_valid"
    assert validate_run_directory(RUNS / "explicit-relation-direct-rule-run-0001")["classification"] == "fixed_label_preference_persisted"
    assert not (RUNS / vector.RUN_ID).exists()
    assert not (RUNS / "attempt-0003").exists()
    assert not (SCRIPTS / "run_mn006_direct_state_vector_qualification.py").exists()