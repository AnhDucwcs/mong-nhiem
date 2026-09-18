from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from mn006 import (
    PROFILE_LEVEL_1,
    PROFILE_LEVEL_2,
    ValidationError,
    decide,
    derive,
    generate_pair,
    parse_answer,
    replay,
    validate_case,
    validate_pair,
)
from mn006.audits import AuditError, answer_proxy_audit, positional_audit
from mn006.fingerprinting import (
    canonical_json_sha256,
    canonical_text_sha256,
)
from mn006.model import EventProvenance, SourceEvent
from mn006.oracle import OracleError
from mn006.serialization import (
    authority_record,
    evaluator_record,
    public_record,
    serialize_public_text,
)
from mn006.validation import validate_public_record


def pair(profile: str = "level_1_light_interleaved", ordinal: int = 0, seed: str = "unit-seed"):
    return generate_pair(profile, ordinal, seed)


def test_same_configuration_reproduces_every_view_and_fingerprint() -> None:
    first = pair("level_2_primary_interleaved", 7, "repeatable")
    second = pair("level_2_primary_interleaved", 7, "repeatable")
    assert first == second
    assert public_record(first.interleaved) == public_record(second.interleaved)
    assert authority_record(first.contiguous) == authority_record(second.contiguous)
    assert canonical_json_sha256(authority_record(first.interleaved)) == canonical_json_sha256(authority_record(second.interleaved))


def test_different_seed_varies_independent_constructed_details() -> None:
    first = pair("level_2_primary_interleaved", 6, "seed-a")
    second = pair("level_2_primary_interleaved", 6, "seed-b")
    assert first.interleaved.core.answer_class == second.interleaved.core.answer_class == "VALID"
    assert first.interleaved.core.entity_permutation != second.interleaved.core.entity_permutation or first.interleaved.core.entity_histories != second.interleaved.core.entity_histories


def test_answer_class_alternates_before_histories_are_constructed() -> None:
    answers = [pair(ordinal=ordinal).interleaved.canonical_answer for ordinal in range(8)]
    assert answers == ["VALID", "INVALID", "VALID", "INVALID", "VALID", "INVALID", "VALID", "INVALID"]
    assert sum(answer == "VALID" for answer in answers) == sum(answer == "INVALID" for answer in answers)


@pytest.mark.parametrize("profile", [PROFILE_LEVEL_1.identifier, PROFILE_LEVEL_2.identifier])
def test_every_history_is_three_assignments_and_target_tuple_matches_answer(profile: str) -> None:
    for ordinal in range(6):
        case = pair(profile, ordinal).interleaved
        validate_case(case)
        for history in case.core.entity_histories.values():
            assert len(history) == 3
            assert history[0] != "S0"
            assert history[1] != history[0]
            assert history[2] != history[1]
        first, second = case.core.query_entities
        assert (case.canonical_entity_states[first] == case.canonical_entity_states[second]) == (case.canonical_answer == "VALID")


def test_replay_rejects_noop_assignment() -> None:
    events = (SourceEvent("E01-1", 1, "E01", "S0"),)
    with pytest.raises(OracleError, match="no-op"):
        replay(events, ("E01",))


def test_validator_rejects_noop_history_even_if_source_was_not_rebuilt() -> None:
    case = pair().interleaved
    entity_id = case.core.profile.active_entities[0]
    histories = dict(case.core.entity_histories)
    histories[entity_id] = ("S0", "S1", "S2")
    bad = replace(case, core=replace(case.core, entity_histories=histories))
    with pytest.raises(ValidationError, match="no-op"):
        validate_case(bad)


@pytest.mark.parametrize(
    ("profile", "expected_gap", "expected_span", "expected_total"),
    [
        (PROFILE_LEVEL_1.identifier, 2, 7, 9),
        (PROFILE_LEVEL_2.identifier, 7, 17, 24),
    ],
)
def test_interleaved_round_robin_schedule_arithmetic(profile: str, expected_gap: int, expected_span: int, expected_total: int) -> None:
    case = pair(profile, 2).interleaved
    metrics = case.interleaving_metrics
    assert metrics["total_event_count"] == expected_total
    assert metrics["minimum_query_gap"] == expected_gap
    assert metrics["mean_query_gap"] == float(expected_gap)
    assert all(gaps == [expected_gap, expected_gap] for gaps in metrics["query_gap_vector"].values())
    assert all(span == expected_span for span in metrics["query_relevant_spans"].values())


def test_contiguous_control_groups_each_history_and_pair_is_equivalent() -> None:
    generated = pair("level_2_primary_interleaved", 3)
    contiguous = generated.contiguous
    assert [event.entity_id for event in contiguous.source_events] == [
        entity_id for entity_id in contiguous.core.entity_permutation for _ in range(3)
    ]
    assert contiguous.interleaving_metrics["minimum_query_gap"] == 0
    assert all(span == 3 for span in contiguous.interleaving_metrics["query_relevant_spans"].values())
    assert validate_pair(generated)["equivalence"]


def test_oracle_has_only_replay_derive_decide_semantics() -> None:
    states = replay(
        (
            SourceEvent("E01-1", 1, "E01", "S1"),
            SourceEvent("E02-1", 2, "E02", "S2"),
            SourceEvent("E01-2", 3, "E01", "S2"),
        ),
        ("E01", "E02"),
    ).entity_states
    assert states == {"E01": "S2", "E02": "S2"}
    assert derive(states, ("E01", "E02")) == {"equal_state": True}
    assert decide({"equal_state": True}) == "VALID"
    assert decide({"equal_state": False}) == "INVALID"


@pytest.mark.parametrize("raw", ["VALID", " INVALID ", "\tVALID\r\n"])
def test_answer_parser_accepts_only_exact_labels_after_ascii_trim(raw: str) -> None:
    assert parse_answer(raw) in {"VALID", "INVALID"}


@pytest.mark.parametrize("raw", ["valid", "VALID.", "Answer: VALID", "VALID INVALID", "VALID\u00a0"])
def test_answer_parser_rejects_case_changes_explanations_extra_tokens_and_nonascii_whitespace(raw: str) -> None:
    assert parse_answer(raw) is None


def test_public_evaluator_authority_records_are_separated() -> None:
    case = pair().interleaved
    public = public_record(case)
    evaluator = evaluator_record(case)
    authority = authority_record(case)
    validate_public_record(public)
    assert "canonical_answer" not in public
    assert "seed" not in public
    assert "canonical_answer" in evaluator
    assert "entity_histories" in authority
    assert "canonical_derived_facts" in authority
    assert "equal_state" not in serialize_public_text(case)


def test_public_validator_rejects_authority_field_insertion() -> None:
    record = public_record(pair().interleaved)
    record["canonical_answer"] = "VALID"
    with pytest.raises(ValidationError, match="unauthorized"):
        validate_public_record(record)


def test_canonical_fingerprints_ignore_host_newline_convention() -> None:
    case = pair().interleaved
    text = serialize_public_text(case)
    assert canonical_text_sha256(text) == canonical_text_sha256(text.replace("\n", "\r\n"))
    assert canonical_json_sha256({"b": 1, "a": ["x"]}) == canonical_json_sha256({"a": ["x"], "b": 1})
    validate_case(case)


def test_answer_proxy_and_periodicity_audits_pass_for_bounded_test_batches() -> None:
    for profile in (PROFILE_LEVEL_1.identifier, PROFILE_LEVEL_2.identifier):
        batch = [pair(profile, ordinal, "audit-seed") for ordinal in range(48)]
        proxy = answer_proxy_audit(batch)
        position = positional_audit(batch, require_full_slot_coverage=True)
        assert proxy["answer_counts"] == {"VALID": 24, "INVALID": 24}
        assert proxy["answer_x_schedule_kind"]["contiguous_control"] == proxy["answer_x_schedule_kind"]["interleaved"]
        assert position["entity_count"] in {3, 8}


def test_audits_reject_missing_pair_and_obvious_label_proxy() -> None:
    one_member = pair().interleaved
    with pytest.raises(AuditError, match="missing a matched schedule"):
        answer_proxy_audit([one_member])
    valid = pair(ordinal=0)
    invalid = pair(ordinal=1)
    forced_core = replace(invalid.interleaved.core, query_entities=valid.interleaved.core.query_entities)
    forced = replace(invalid.interleaved, core=forced_core)
    with pytest.raises(AuditError, match="missing a matched schedule"):
        positional_audit([valid, forced])


def test_validator_rejects_deleted_event_and_internal_order_change() -> None:
    case = pair("level_1_light_interleaved", 4).interleaved
    deleted = replace(case, source_events=case.source_events[:-1])
    with pytest.raises(ValidationError):
        validate_case(deleted)
    events = list(case.source_events)
    first = next(index for index, event in enumerate(events) if event.event_id == "E01-1")
    second = next(index for index, event in enumerate(events) if event.event_id == "E01-2")
    events[first], events[second] = events[second], events[first]
    reordered = tuple(
        replace(event, global_ordinal=index) for index, event in enumerate(events, start=1)
    )
    with pytest.raises(ValidationError):
        validate_case(replace(case, source_events=reordered))


def test_validator_rejects_changed_answer_provenance_and_metrics() -> None:
    case = pair("level_2_primary_interleaved", 5).interleaved
    wrong_answer = replace(case, canonical_answer="VALID")
    with pytest.raises(ValidationError, match="canonical answer"):
        validate_case(wrong_answer)
    event_id = case.source_events[0].event_id
    provenance = dict(case.event_provenance)
    provenance[event_id] = EventProvenance(event_id, 3, "S2")
    with pytest.raises(ValidationError, match="provenance"):
        validate_case(replace(case, event_provenance=provenance))
    metrics = dict(case.interleaving_metrics)
    metrics["minimum_query_gap"] = 99
    with pytest.raises(ValidationError, match="metrics"):
        validate_case(replace(case, interleaving_metrics=metrics))


def test_pair_validator_rejects_source_event_duplication() -> None:
    generated = pair("level_1_light_interleaved", 6)
    duplicated_events = list(generated.interleaved.source_events)
    duplicated_events[-1] = duplicated_events[-2]
    corrupted = replace(generated.interleaved, source_events=tuple(duplicated_events))
    with pytest.raises(ValidationError):
        validate_pair(replace(generated, interleaved=corrupted))
