"""Deterministic structural audits for answer proxies and regular-schedule positions."""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence

from .model import (
    ANSWERS,
    SCHEDULE_CONTIGUOUS,
    SCHEDULE_INTERLEAVED,
    CasePair,
    GeneratedCase,
)


class AuditError(ValueError):
    """Raised when a bounded batch exposes a structural proxy or coverage defect."""


def _case_members(items: Iterable[CasePair | GeneratedCase]) -> list[GeneratedCase]:
    members: list[GeneratedCase] = []
    for item in items:
        if isinstance(item, CasePair):
            members.extend((item.contiguous, item.interleaved))
        else:
            members.append(item)
    return members


def _unique_cores(items: Iterable[CasePair | GeneratedCase]) -> list[GeneratedCase]:
    by_pair: dict[str, GeneratedCase] = {}
    schedules: dict[str, set[str]] = defaultdict(set)
    for case in _case_members(items):
        pair_id = case.core.pair_id
        existing = by_pair.get(pair_id)
        if existing is not None and existing.core != case.core:
            raise AuditError("one pair ID maps to divergent canonical cores")
        by_pair[pair_id] = case
        schedules[pair_id].add(case.schedule_kind)
    for pair_id, kinds in schedules.items():
        if kinds and kinds != {SCHEDULE_CONTIGUOUS, SCHEDULE_INTERLEAVED}:
            raise AuditError(f"pair {pair_id} is missing a matched schedule")
    return [by_pair[pair_id] for pair_id in sorted(by_pair)]


def answer_proxy_audit(items: Sequence[CasePair | GeneratedCase]) -> dict[str, object]:
    """Report and reject simple deterministic label proxies, not model statistics."""
    cores = _unique_cores(items)
    if not cores:
        raise AuditError("answer-proxy audit requires at least one paired case")
    answers = Counter(case.canonical_answer for case in cores)
    if set(answers) - set(ANSWERS) or abs(answers["VALID"] - answers["INVALID"]) > 1:
        raise AuditError("canonical ordinal batch is not answer-balanced")
    by_answer_query_ids: dict[str, Counter[str]] = {answer: Counter() for answer in ANSWERS}
    by_answer_slots: dict[str, Counter[int]] = {answer: Counter() for answer in ANSWERS}
    by_answer_tuples: dict[str, Counter[tuple[str, str]]] = {answer: Counter() for answer in ANSWERS}
    schedule_answers: dict[str, Counter[str]] = {SCHEDULE_CONTIGUOUS: Counter(), SCHEDULE_INTERLEAVED: Counter()}
    for case in cores:
        answer = case.canonical_answer
        for entity_id in case.core.query_entities:
            by_answer_query_ids[answer][entity_id] += 1
            by_answer_slots[answer][case.core.entity_permutation.index(entity_id) + 1] += 1
        state_tuple = tuple(case.canonical_entity_states[entity_id] for entity_id in case.core.query_entities)
        by_answer_tuples[answer][state_tuple] += 1
        schedule_answers[SCHEDULE_CONTIGUOUS][answer] += 1
        schedule_answers[SCHEDULE_INTERLEAVED][answer] += 1
    if schedule_answers[SCHEDULE_CONTIGUOUS] != schedule_answers[SCHEDULE_INTERLEAVED]:
        raise AuditError("answer distribution differs between paired schedules")
    query_id_sets = {answer: set(counts) for answer, counts in by_answer_query_ids.items()}
    slot_sets = {answer: set(counts) for answer, counts in by_answer_slots.items()}
    if min(answers.values()) >= 4 and not (query_id_sets["VALID"] & query_id_sets["INVALID"]):
        raise AuditError("query identities are disjoint by answer class")
    if min(answers.values()) >= 4 and not (slot_sets["VALID"] & slot_sets["INVALID"]):
        raise AuditError("query permutation slots are disjoint by answer class")
    for answer, candidates in (("VALID", 3), ("INVALID", 6)):
        expected = min(candidates, answers[answer])
        if len(by_answer_tuples[answer]) < expected:
            raise AuditError(f"{answer} final-state tuple rotation lacks bounded coverage")
    return {
        "answer_counts": dict(answers),
        "answer_x_query_entity_ids": {answer: dict(counts) for answer, counts in by_answer_query_ids.items()},
        "answer_x_query_permutation_slots": {answer: dict(counts) for answer, counts in by_answer_slots.items()},
        "answer_x_query_final_state_tuple": {
            answer: {"/".join(key): value for key, value in counts.items()}
            for answer, counts in by_answer_tuples.items()
        },
        "answer_x_schedule_kind": {kind: dict(counts) for kind, counts in schedule_answers.items()},
        "pair_count": len(cores),
    }


def positional_audit(items: Sequence[CasePair | GeneratedCase], require_full_slot_coverage: bool = False) -> dict[str, object]:
    """Make regular round-robin position effects visible without changing the scheduler."""
    cores = _unique_cores(items)
    if not cores:
        raise AuditError("positional audit requires at least one paired case")
    profile_ids = {case.core.profile.identifier for case in cores}
    if len(profile_ids) != 1:
        raise AuditError("positional audit must be run per profile")
    profile = cores[0].core.profile
    slots_by_answer: dict[str, Counter[int]] = {answer: Counter() for answer in ANSWERS}
    patterns_by_answer: dict[str, Counter[tuple[int, ...]]] = {answer: Counter() for answer in ANSWERS}
    for case in cores:
        slots = tuple(sorted(case.core.entity_permutation.index(entity_id) + 1 for entity_id in case.core.query_entities))
        slots_by_answer[case.canonical_answer].update(slots)
        patterns_by_answer[case.canonical_answer][slots] += 1
    for answer, counts in slots_by_answer.items():
        if counts and set(counts) in ({1}, {profile.entity_count}):
            raise AuditError(f"{answer} query entities are locked to an extreme permutation slot")
    if require_full_slot_coverage:
        for answer, counts in slots_by_answer.items():
            if len(counts) != profile.entity_count:
                raise AuditError(f"{answer} does not cover every permutation slot in this bounded audit batch")
    return {
        "entity_count": profile.entity_count,
        "periodicity": "one seeded permutation repeats across all three rounds",
        "query_event_position_pattern": {
            answer: {
                "/".join(str(slot) for slot in pattern): count
                for pattern, count in patterns.items()
            }
            for answer, patterns in patterns_by_answer.items()
        },
        "query_permutation_slot_counts": {answer: dict(counts) for answer, counts in slots_by_answer.items()},
    }
