"""Static semantic, oracle, schedule, pair, and public-boundary validators."""
from __future__ import annotations

import random
from collections import Counter
from collections.abc import Mapping
from typing import Any

from .fingerprinting import canonical_json_sha256, canonical_text_sha256
from .generation import _subseeds, answer_class_for_ordinal
from .model import (
    ANSWERS,
    ENTITY_IDS,
    INITIAL_STATE,
    RULE_ID,
    SCHEDULE_CONTIGUOUS,
    SCHEDULE_INTERLEAVED,
    STATES,
    UPDATES_PER_ENTITY,
    CasePair,
    GeneratedCase,
)
from .oracle import OracleError, decide, derive, replay
from .serialization import (
    _authority_core_record,
    authority_record,
    evaluator_record,
    public_record,
    serialize_public_text,
)


class ValidationError(ValueError):
    """Raised when a purported MN-006 case violates a frozen v1 invariant."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _expected_sequence(case: GeneratedCase) -> list[tuple[str, int, str]]:
    core = case.core
    if case.schedule_kind == SCHEDULE_CONTIGUOUS:
        return [
            (entity_id, history_ordinal, core.entity_histories[entity_id][history_ordinal - 1])
            for entity_id in core.entity_permutation
            for history_ordinal in range(1, UPDATES_PER_ENTITY + 1)
        ]
    if case.schedule_kind == SCHEDULE_INTERLEAVED:
        return [
            (entity_id, history_ordinal, core.entity_histories[entity_id][history_ordinal - 1])
            for history_ordinal in range(1, UPDATES_PER_ENTITY + 1)
            for entity_id in core.entity_permutation
        ]
    raise ValidationError("unknown schedule kind")


def _computed_metrics(case: GeneratedCase) -> dict[str, object]:
    positions = {
        entity_id: [event.global_ordinal for event in case.source_events if event.entity_id == entity_id]
        for entity_id in case.core.profile.active_entities
    }
    query_positions = {entity_id: positions[entity_id] for entity_id in case.core.query_entities}
    query_gaps = {
        entity_id: [values[index + 1] - values[index] - 1 for index in range(2)]
        for entity_id, values in query_positions.items()
    }
    all_gaps = [gap for values in query_gaps.values() for gap in values]
    spans = {entity_id: values[-1] - values[0] + 1 for entity_id, values in query_positions.items()}
    return {
        "entity_count": case.core.profile.entity_count,
        "entity_permutation": list(case.core.entity_permutation),
        "minimum_query_gap": min(all_gaps),
        "mean_query_gap": sum(all_gaps) / len(all_gaps),
        "query_entity_permutation_slots": {
            entity_id: case.core.entity_permutation.index(entity_id) + 1
            for entity_id in case.core.query_entities
        },
        "query_event_count": len(case.core.query_entities) * UPDATES_PER_ENTITY,
        "query_event_positions": query_positions,
        "query_gap_vector": query_gaps,
        "query_relevant_spans": spans,
        "schedule_kind": case.schedule_kind,
        "total_event_count": len(case.source_events),
        "non_query_event_count": len(case.source_events) - len(case.core.query_entities) * UPDATES_PER_ENTITY,
        "updates_per_entity": UPDATES_PER_ENTITY,
    }


def validate_public_record(record: Mapping[str, Any]) -> None:
    """Enforce the public schema and reject authority-only key insertion."""
    required = {
        "allowed_answers",
        "case_id",
        "initial_state",
        "profile",
        "public_serialization_version",
        "query",
        "schedule_kind",
        "source_events",
    }
    _require(set(record) == required, "public record has missing or unauthorized fields")
    _require(record["initial_state"] == INITIAL_STATE, "public initial state differs from S0")
    _require(record["allowed_answers"] == list(ANSWERS), "public allowed answers differ from frozen vocabulary")
    query = record["query"]
    _require(isinstance(query, Mapping), "public query must be an object")
    _require(set(query) == {"entities", "question", "rule_id"}, "public query has unauthorized fields")
    _require(query["rule_id"] == RULE_ID, "public rule ID differs from frozen rule")
    _require(isinstance(query["entities"], list) and len(query["entities"]) == 2, "public query must name two entities")
    events = record["source_events"]
    _require(isinstance(events, list), "public source events must be a list")
    for event in events:
        _require(isinstance(event, Mapping), "public source event must be an object")
        _require(
            set(event) == {"assigned_state", "entity_id", "event_id", "global_ordinal"},
            "public source event has authority-only or missing fields",
        )
    forbidden_key_fragments = ("canonical", "derived", "provenance", "history", "seed", "final", "current")

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                lowered = str(key).casefold()
                _require(
                    not any(fragment in lowered for fragment in forbidden_key_fragments),
                    f"public record contains prohibited authority key: {key}",
                )
                _require(str(key) not in {"answer", "target_answer"}, f"public record contains answer-bearing key: {key}")
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(record)


def validate_public_boundary(case: GeneratedCase) -> None:
    record = public_record(case)
    validate_public_record(record)
    rendered = serialize_public_text(case)
    _require("\r" not in rendered, "public rendering must use LF, not CRLF")
    _require(rendered.endswith("\n") and not rendered.endswith("\n\n"), "public rendering must have exactly one final LF")
    _require("equal_state" not in rendered, "public rendering exposes an oracle-derived fact")
    _require("canonical_" not in rendered, "public rendering exposes canonical authority metadata")
    _require(canonical_text_sha256(rendered) == canonical_text_sha256(rendered.replace("\n", "\r\n")), "public text fingerprint is newline-dependent")


def validate_semantics(case: GeneratedCase) -> None:
    core = case.core
    profile = core.profile
    _require(profile.active_entities == ENTITY_IDS[: profile.entity_count], "active entity inventory is not canonical")
    _require(core.answer_class == answer_class_for_ordinal(core.ordinal), "answer class does not follow ordinal alternation")
    _require(core.answer_class in ANSWERS, "invalid target answer class")
    _require(len(core.query_entities) == 2 and len(set(core.query_entities)) == 2, "query arity must be two distinct entities")
    _require(set(core.query_entities).issubset(profile.active_entities), "query entity outside active profile")
    _require(set(core.entity_histories) == set(profile.active_entities), "histories must cover exactly active entities")
    _require(set(core.entity_permutation) == set(profile.active_entities), "permutation must cover exactly active entities")
    _require(len(core.entity_permutation) == profile.entity_count, "permutation has duplicate entity IDs")
    expected_subseeds = _subseeds(core.root_seed, profile, core.ordinal)
    _require(dict(core.subseeds) == expected_subseeds, "stored independent subseeds do not reproduce")
    expected_query = tuple(random.Random(expected_subseeds["query_selection"]).sample(list(profile.active_entities), 2))
    _require(core.query_entities == expected_query, "query selection differs from its dedicated sub-seed")
    expected_permutation = tuple(
        random.Random(expected_subseeds["entity_permutation"]).sample(list(profile.active_entities), profile.entity_count)
    )
    _require(core.entity_permutation == expected_permutation, "entity permutation differs from its dedicated sub-seed")
    for entity_id, history in core.entity_histories.items():
        _require(len(history) == UPDATES_PER_ENTITY, f"{entity_id} does not have exactly three assignments")
        predecessor = INITIAL_STATE
        for state in history:
            _require(state in STATES, f"{entity_id} has invalid state token")
            _require(state != predecessor, f"{entity_id} has a prohibited no-op assignment")
            predecessor = state


def validate_oracle(case: GeneratedCase) -> None:
    try:
        replayed = replay(case.source_events, case.core.profile.active_entities)
        derived = derive(replayed.entity_states, case.core.query_entities, RULE_ID)
        answer = decide(derived, RULE_ID)
    except OracleError as error:
        raise ValidationError(str(error)) from error
    _require(dict(case.canonical_entity_states) == dict(replayed.entity_states), "stored final states differ from replay")
    _require(dict(case.canonical_derived_facts) == derived, "stored derived fact differs from recomputation")
    _require(case.canonical_answer == answer, "stored canonical answer differs from decision table")
    _require(case.canonical_answer == case.core.answer_class, "constructed final query states disagree with target answer")
    _require(case.canonical_answer in ANSWERS, "canonical answer outside frozen vocabulary")
    expected_provenance = replayed.event_provenance
    actual_provenance = {
        event_id: {
            "expected_predecessor_state": value.expected_predecessor_state,
            "history_ordinal": value.history_ordinal,
        }
        for event_id, value in case.event_provenance.items()
    }
    _require(actual_provenance == expected_provenance, "stored event provenance differs from replay")


def validate_schedule(case: GeneratedCase) -> None:
    expected = _expected_sequence(case)
    actual = [(event.entity_id, int(event.event_id.rsplit("-", 1)[1]), event.assigned_state) for event in case.source_events]
    _require(actual == expected, "source order or per-entity history differs from frozen scheduler")
    _require(
        [event.global_ordinal for event in case.source_events] == list(range(1, case.core.profile.total_events + 1)),
        "source global ordinals are not consecutive",
    )
    _require(len(case.source_events) == case.core.profile.total_events, "incorrect total event count")
    expected_metrics = _computed_metrics(case)
    _require(dict(case.interleaving_metrics) == expected_metrics, "stored interleaving metrics differ from recomputation")
    all_gaps = [gap for values in expected_metrics["query_gap_vector"].values() for gap in values]  # type: ignore[union-attr]
    all_spans = list(expected_metrics["query_relevant_spans"].values())  # type: ignore[union-attr]
    if case.schedule_kind == SCHEDULE_CONTIGUOUS:
        _require(all(gap == 0 for gap in all_gaps), "contiguous control has foreign events inside a history")
        _require(all(span == 3 for span in all_spans), "contiguous control relevant span must be three")
    elif case.schedule_kind == SCHEDULE_INTERLEAVED:
        _require(all(gap == case.core.profile.interleaved_gap for gap in all_gaps), "round-robin gap arithmetic differs")
        _require(all(span == case.core.profile.interleaved_span for span in all_spans), "round-robin span arithmetic differs")
    else:
        raise ValidationError("unknown schedule kind")


def validate_fingerprints(case: GeneratedCase) -> None:
    core = _authority_core_record(case)
    record = authority_record(case)
    hashes = record["generation_metadata"]["canonical_hashes"]
    _require(hashes["authority_core_sha256"] == canonical_json_sha256(core), "authority core fingerprint differs")
    _require(hashes["evaluator_json_sha256"] == canonical_json_sha256(evaluator_record(case)), "evaluator fingerprint differs")
    _require(hashes["public_json_sha256"] == canonical_json_sha256(public_record(case)), "public JSON fingerprint differs")
    _require(hashes["public_text_sha256"] == canonical_text_sha256(serialize_public_text(case)), "public text fingerprint differs")


def validate_case(case: GeneratedCase) -> dict[str, bool]:
    """Run every single-case static validator and return a non-evidentiary report."""
    validate_semantics(case)
    validate_oracle(case)
    validate_schedule(case)
    validate_public_boundary(case)
    validate_fingerprints(case)
    return {
        "fingerprints": True,
        "oracle": True,
        "public_boundary": True,
        "schedule": True,
        "semantics": True,
    }


def validate_pair(pair: CasePair) -> dict[str, bool]:
    """Verify that only schedule-dependent properties differ within a pair."""
    contiguous, interleaved = pair.contiguous, pair.interleaved
    validate_case(contiguous)
    validate_case(interleaved)
    _require(contiguous.schedule_kind == SCHEDULE_CONTIGUOUS, "pair contiguous member has wrong schedule kind")
    _require(interleaved.schedule_kind == SCHEDULE_INTERLEAVED, "pair interleaved member has wrong schedule kind")
    _require(contiguous.core == interleaved.core, "pair does not share one canonical core")
    _require(contiguous.core.pair_id == interleaved.core.pair_id, "pair ID differs")
    _require(
        Counter((event.event_id, event.entity_id, event.assigned_state) for event in contiguous.source_events)
        == Counter((event.event_id, event.entity_id, event.assigned_state) for event in interleaved.source_events),
        "paired schedules do not conserve source events",
    )
    _require(contiguous.canonical_entity_states == interleaved.canonical_entity_states, "pair final states differ")
    _require(contiguous.canonical_derived_facts == interleaved.canonical_derived_facts, "pair derived facts differ")
    _require(contiguous.canonical_answer == interleaved.canonical_answer, "pair canonical answers differ")
    _require(contiguous.core.query_entities == interleaved.core.query_entities, "pair query differs")
    return {"contiguous": True, "equivalence": True, "interleaved": True}
