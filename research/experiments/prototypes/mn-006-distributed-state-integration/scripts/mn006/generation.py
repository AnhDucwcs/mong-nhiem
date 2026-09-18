"""Bounded generation-by-construction for the frozen MN-006 v1 contract."""
from __future__ import annotations

import hashlib
import random
from collections.abc import Sequence

from .model import (
    INITIAL_STATE,
    PROFILE_LEVEL_1,
    PROFILE_LEVEL_2,
    PROFILES,
    RULE_ID,
    SCHEDULE_CONTIGUOUS,
    SCHEDULE_INTERLEAVED,
    STATES,
    UPDATES_PER_ENTITY,
    CaseCore,
    CasePair,
    EventProvenance,
    GeneratedCase,
    Profile,
    SourceEvent,
)
from .oracle import decide, derive, replay


class GenerationError(ValueError):
    """Raised for invalid configuration or a deterministic construction defect."""


def derive_subseed(
    base_seed: str | int,
    profile_id: str,
    purpose: str,
    ordinal: int | None,
) -> int:
    """Derive a stable, independently named PRNG seed without global PRNG state."""
    ordinal_text = "shared" if ordinal is None else str(ordinal)
    material = f"mn006-v1\0{base_seed}\0{profile_id}\0{ordinal_text}\0{purpose}"
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:8], "big")


def answer_class_for_ordinal(ordinal: int) -> str:
    """The frozen sorted ordinal sequence is VALID, INVALID, VALID, INVALID, ..."""
    if ordinal < 0:
        raise GenerationError("case ordinal must be non-negative")
    return "VALID" if ordinal % 2 == 0 else "INVALID"


def _profile(profile: str | Profile) -> Profile:
    if isinstance(profile, Profile):
        if profile.identifier not in PROFILES or PROFILES[profile.identifier] != profile:
            raise GenerationError("profile is not a frozen MN-006 v1 profile")
        return profile
    try:
        return PROFILES[profile]
    except KeyError as error:
        raise GenerationError(f"unknown MN-006 profile: {profile}") from error


def _history_ending_at(final_state: str, seed: int) -> tuple[str, str, str]:
    """Construct exactly three non-no-op assignments backwards from final_state."""
    if final_state not in STATES:
        raise GenerationError("final state is outside the frozen vocabulary")
    rng = random.Random(seed)
    second = rng.choice(tuple(state for state in STATES if state != final_state))
    first = rng.choice(tuple(state for state in STATES if state != INITIAL_STATE and state != second))
    history = (first, second, final_state)
    predecessor = INITIAL_STATE
    for state in history:
        if state == predecessor:
            raise GenerationError("history construction produced a no-op")
        predecessor = state
    return history


def _target_state_tuple(answer_class: str, rotation_seed: int, ordinal: int) -> tuple[str, str]:
    """Rotate admissible state tuples inside each answer class without rejection."""
    valid = tuple((state, state) for state in STATES)
    invalid = tuple((left, right) for left in STATES for right in STATES if left != right)
    candidates = valid if answer_class == "VALID" else invalid
    rotation = rotation_seed % len(candidates)
    return candidates[(ordinal // 2 + rotation) % len(candidates)]


def _subseeds(base_seed: str | int, profile: Profile, ordinal: int) -> dict[str, int]:
    return {
        "answer_class": derive_subseed(base_seed, profile.identifier, "answer-class", ordinal),
        "entity_permutation": derive_subseed(base_seed, profile.identifier, "entity-permutation", ordinal),
        "final_state_tuple_rotation": derive_subseed(base_seed, profile.identifier, "final-state-tuple", None),
        "non_query_histories": derive_subseed(base_seed, profile.identifier, "non-query-histories", ordinal),
        "query_histories": derive_subseed(base_seed, profile.identifier, "query-histories", ordinal),
        "query_selection": derive_subseed(base_seed, profile.identifier, "query-selection", ordinal),
    }


def _history_seed(base_seed: str | int, profile: Profile, ordinal: int, entity_id: str, role: str) -> int:
    return derive_subseed(base_seed, profile.identifier, f"{role}-history:{entity_id}", ordinal)


def _select_query_entities(profile: Profile, query_seed: int) -> tuple[str, str]:
    """Use only the dedicated query-selection seed, before answer tuple selection."""
    selection = random.Random(query_seed).sample(list(profile.active_entities), 2)
    return selection[0], selection[1]


def _build_core(profile: Profile, ordinal: int, base_seed: str | int) -> CaseCore:
    answer_class = answer_class_for_ordinal(ordinal)
    subseeds = _subseeds(base_seed, profile, ordinal)
    query_entities = _select_query_entities(profile, subseeds["query_selection"])
    target_tuple = _target_state_tuple(answer_class, subseeds["final_state_tuple_rotation"], ordinal)
    target_states = dict(zip(query_entities, target_tuple, strict=True))

    histories: dict[str, tuple[str, str, str]] = {}
    for entity_id in profile.active_entities:
        if entity_id in target_states:
            final_state = target_states[entity_id]
            history_seed = _history_seed(base_seed, profile, ordinal, entity_id, "query")
        else:
            final_seed = derive_subseed(base_seed, profile.identifier, f"non-query-final:{entity_id}", ordinal)
            final_state = random.Random(final_seed).choice(STATES)
            history_seed = _history_seed(base_seed, profile, ordinal, entity_id, "non-query")
        histories[entity_id] = _history_ending_at(final_state, history_seed)

    permutation = tuple(random.Random(subseeds["entity_permutation"]).sample(list(profile.active_entities), profile.entity_count))
    pair_id = f"mn006-v1-{profile.identifier}-{ordinal:06d}"
    return CaseCore(
        profile=profile,
        ordinal=ordinal,
        root_seed=str(base_seed),
        answer_class=answer_class,
        query_entities=query_entities,
        entity_histories=histories,
        entity_permutation=permutation,
        subseeds=subseeds,
        pair_id=pair_id,
    )


def _event_sequence(core: CaseCore, schedule_kind: str) -> Sequence[tuple[str, int, str]]:
    if schedule_kind == SCHEDULE_CONTIGUOUS:
        return tuple(
            (entity_id, history_ordinal, core.entity_histories[entity_id][history_ordinal - 1])
            for entity_id in core.entity_permutation
            for history_ordinal in range(1, UPDATES_PER_ENTITY + 1)
        )
    if schedule_kind == SCHEDULE_INTERLEAVED:
        return tuple(
            (entity_id, history_ordinal, core.entity_histories[entity_id][history_ordinal - 1])
            for history_ordinal in range(1, UPDATES_PER_ENTITY + 1)
            for entity_id in core.entity_permutation
        )
    raise GenerationError(f"unknown schedule kind: {schedule_kind}")


def _events_and_provenance(core: CaseCore, schedule_kind: str) -> tuple[tuple[SourceEvent, ...], dict[str, EventProvenance]]:
    events: list[SourceEvent] = []
    provenance: dict[str, EventProvenance] = {}
    for global_ordinal, (entity_id, history_ordinal, state) in enumerate(_event_sequence(core, schedule_kind), start=1):
        event_id = f"{entity_id}-{history_ordinal}"
        predecessor = INITIAL_STATE if history_ordinal == 1 else core.entity_histories[entity_id][history_ordinal - 2]
        events.append(SourceEvent(event_id, global_ordinal, entity_id, state))
        provenance[event_id] = EventProvenance(event_id, history_ordinal, predecessor)
    return tuple(events), provenance


def _metrics(core: CaseCore, events: Sequence[SourceEvent], schedule_kind: str) -> dict[str, object]:
    positions = {
        entity_id: [event.global_ordinal for event in events if event.entity_id == entity_id]
        for entity_id in core.profile.active_entities
    }
    query_positions = {entity_id: positions[entity_id] for entity_id in core.query_entities}
    query_gaps = {
        entity_id: [values[index + 1] - values[index] - 1 for index in range(len(values) - 1)]
        for entity_id, values in query_positions.items()
    }
    all_gaps = [gap for values in query_gaps.values() for gap in values]
    query_spans = {entity_id: values[-1] - values[0] + 1 for entity_id, values in query_positions.items()}
    slots = {entity_id: core.entity_permutation.index(entity_id) + 1 for entity_id in core.query_entities}
    return {
        "entity_count": core.profile.entity_count,
        "entity_permutation": list(core.entity_permutation),
        "minimum_query_gap": min(all_gaps),
        "mean_query_gap": sum(all_gaps) / len(all_gaps),
        "query_entity_permutation_slots": slots,
        "query_event_count": len(core.query_entities) * UPDATES_PER_ENTITY,
        "query_event_positions": query_positions,
        "query_gap_vector": query_gaps,
        "query_relevant_spans": query_spans,
        "schedule_kind": schedule_kind,
        "total_event_count": len(events),
        "non_query_event_count": len(events) - len(core.query_entities) * UPDATES_PER_ENTITY,
        "updates_per_entity": UPDATES_PER_ENTITY,
    }


def _build_schedule(core: CaseCore, schedule_kind: str) -> GeneratedCase:
    events, provenance = _events_and_provenance(core, schedule_kind)
    replayed = replay(events, core.profile.active_entities)
    derived = derive(replayed.entity_states, core.query_entities, RULE_ID)
    answer = decide(derived, RULE_ID)
    if answer != core.answer_class:
        raise GenerationError("constructed query tuple does not match preselected answer class")
    if len(events) != core.profile.total_events:
        raise GenerationError("scheduler produced an incorrect event count")
    for event_id, expected in provenance.items():
        actual = replayed.event_provenance[event_id]
        if actual != {
            "expected_predecessor_state": expected.expected_predecessor_state,
            "history_ordinal": expected.history_ordinal,
        }:
            raise GenerationError("replay provenance disagrees with constructed history")
    case_id = f"{core.pair_id}-{schedule_kind}"
    return GeneratedCase(
        core=core,
        schedule_kind=schedule_kind,
        case_id=case_id,
        source_events=events,
        event_provenance=provenance,
        interleaving_metrics=_metrics(core, events, schedule_kind),
        canonical_entity_states=replayed.entity_states,
        canonical_derived_facts=derived,
        canonical_answer=answer,
    )


def generate_pair(profile: str | Profile, ordinal: int, seed: str | int) -> CasePair:
    """Generate one validated-by-construction paired case with no search or retry loop."""
    frozen_profile = _profile(profile)
    core = _build_core(frozen_profile, ordinal, seed)
    return CasePair(
        contiguous=_build_schedule(core, SCHEDULE_CONTIGUOUS),
        interleaved=_build_schedule(core, SCHEDULE_INTERLEAVED),
    )


__all__ = [
    "PROFILE_LEVEL_1",
    "PROFILE_LEVEL_2",
    "GenerationError",
    "answer_class_for_ordinal",
    "derive_subseed",
    "generate_pair",
]
