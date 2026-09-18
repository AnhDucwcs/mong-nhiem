"""Frozen MN-006 v1 constants and immutable case data structures."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

SEMANTIC_CONTRACT_VERSION = "mn006-v1"
GENERATOR_VERSION = "mn006-generator-v1"
VALIDATOR_VERSION = "mn006-validator-v1"
PARSER_VERSION = "mn006-answer-parser-v1"
RULE_ID = "mn006-v1-equal-state"

STATES = ("S0", "S1", "S2")
INITIAL_STATE = "S0"
ANSWERS = ("VALID", "INVALID")
ENTITY_IDS = tuple(f"E{number:02d}" for number in range(1, 9))
UPDATES_PER_ENTITY = 3

SCHEDULE_CONTIGUOUS = "contiguous_control"
SCHEDULE_INTERLEAVED = "interleaved"


@dataclass(frozen=True)
class Profile:
    """A frozen primary profile; contiguous is a paired schedule, not a profile."""

    identifier: str
    entity_count: int

    @property
    def active_entities(self) -> tuple[str, ...]:
        return ENTITY_IDS[: self.entity_count]

    @property
    def total_events(self) -> int:
        return self.entity_count * UPDATES_PER_ENTITY

    @property
    def interleaved_gap(self) -> int:
        return self.entity_count - 1

    @property
    def interleaved_span(self) -> int:
        return 2 * self.entity_count + 1


PROFILE_LEVEL_1 = Profile("level_1_light_interleaved", 3)
PROFILE_LEVEL_2 = Profile("level_2_primary_interleaved", 8)
PROFILES = {
    PROFILE_LEVEL_1.identifier: PROFILE_LEVEL_1,
    PROFILE_LEVEL_2.identifier: PROFILE_LEVEL_2,
}


@dataclass(frozen=True)
class SourceEvent:
    """One public assignment event.  Previous state stays authority-only."""

    event_id: str
    global_ordinal: int
    entity_id: str
    assigned_state: str

    def public_dict(self) -> dict[str, object]:
        return {
            "assigned_state": self.assigned_state,
            "entity_id": self.entity_id,
            "event_id": self.event_id,
            "global_ordinal": self.global_ordinal,
        }


@dataclass(frozen=True)
class EventProvenance:
    """Authority-only provenance for deterministic replay audit."""

    event_id: str
    history_ordinal: int
    expected_predecessor_state: str

    def authority_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "expected_predecessor_state": self.expected_predecessor_state,
            "history_ordinal": self.history_ordinal,
        }


@dataclass(frozen=True)
class CaseCore:
    """Schedule-independent facts shared by a matched pair."""

    profile: Profile
    ordinal: int
    root_seed: str
    answer_class: str
    query_entities: tuple[str, str]
    entity_histories: Mapping[str, tuple[str, str, str]]
    entity_permutation: tuple[str, ...]
    subseeds: Mapping[str, int]
    pair_id: str


@dataclass(frozen=True)
class GeneratedCase:
    """One rendered schedule for a schedule-independent canonical case."""

    core: CaseCore
    schedule_kind: str
    case_id: str
    source_events: tuple[SourceEvent, ...]
    event_provenance: Mapping[str, EventProvenance]
    interleaving_metrics: Mapping[str, object]
    canonical_entity_states: Mapping[str, str]
    canonical_derived_facts: Mapping[str, bool]
    canonical_answer: str


@dataclass(frozen=True)
class CasePair:
    """The matched contiguous and regular round-robin forms of one core case."""

    contiguous: GeneratedCase
    interleaved: GeneratedCase
