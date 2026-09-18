"""Pure replay -> derive -> decide oracle for frozen MN-006 v1 semantics."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .model import ANSWERS, INITIAL_STATE, PARSER_VERSION, RULE_ID, STATES, SourceEvent


class OracleError(ValueError):
    """Raised when a purported source sequence violates frozen oracle semantics."""


@dataclass(frozen=True)
class ReplayResult:
    entity_states: Mapping[str, str]
    event_provenance: Mapping[str, Mapping[str, object]]


def replay(
    source_events: Sequence[SourceEvent],
    active_entities: Sequence[str],
    initial_state: str = INITIAL_STATE,
) -> ReplayResult:
    """Replay public assignments in global source order without deriving an answer."""
    entities = tuple(active_entities)
    if initial_state != INITIAL_STATE:
        raise OracleError("MN-006 v1 initial state must be S0")
    if len(set(entities)) != len(entities) or not entities:
        raise OracleError("active entities must be a non-empty unique sequence")
    states = {entity_id: initial_state for entity_id in entities}
    provenance: dict[str, Mapping[str, object]] = {}
    expected_ordinal = 1
    per_entity_ordinal = {entity_id: 0 for entity_id in entities}
    seen_event_ids: set[str] = set()
    for event in source_events:
        if event.global_ordinal != expected_ordinal:
            raise OracleError("source events must have consecutive one-based global ordinals")
        expected_ordinal += 1
        if event.event_id in seen_event_ids:
            raise OracleError("source event IDs must be unique")
        seen_event_ids.add(event.event_id)
        if event.entity_id not in states:
            raise OracleError(f"invalid entity ID in source event: {event.entity_id}")
        if event.assigned_state not in STATES:
            raise OracleError(f"invalid state token in source event: {event.assigned_state}")
        predecessor = states[event.entity_id]
        if event.assigned_state == predecessor:
            raise OracleError(f"no-op assignment for {event.entity_id}")
        per_entity_ordinal[event.entity_id] += 1
        states[event.entity_id] = event.assigned_state
        provenance[event.event_id] = {
            "expected_predecessor_state": predecessor,
            "history_ordinal": per_entity_ordinal[event.entity_id],
        }
    return ReplayResult(entity_states=states, event_provenance=provenance)


def derive(
    canonical_entity_states: Mapping[str, str],
    query_entities: Sequence[str],
    rule_id: str = RULE_ID,
) -> dict[str, bool]:
    """Derive the one frozen depth-1 fact from exactly two query states."""
    if rule_id != RULE_ID:
        raise OracleError("unknown MN-006 rule ID")
    if len(query_entities) != 2 or query_entities[0] == query_entities[1]:
        raise OracleError("MN-006 v1 requires exactly two distinct query entities")
    first, second = query_entities
    try:
        state_a = canonical_entity_states[first]
        state_b = canonical_entity_states[second]
    except KeyError as error:
        raise OracleError("query entity is absent from canonical state") from error
    if state_a not in STATES or state_b not in STATES:
        raise OracleError("canonical state map contains an invalid state token")
    return {"equal_state": state_a == state_b}


def decide(canonical_derived_facts: Mapping[str, bool], rule_id: str = RULE_ID) -> str:
    """Map the frozen equality fact to the sole canonical output label."""
    if rule_id != RULE_ID:
        raise OracleError("unknown MN-006 rule ID")
    if set(canonical_derived_facts) != {"equal_state"}:
        raise OracleError("MN-006 v1 requires exactly the equal_state derived fact")
    value = canonical_derived_facts["equal_state"]
    if not isinstance(value, bool):
        raise OracleError("equal_state must be boolean")
    return "VALID" if value else "INVALID"


def parse_answer(raw: str) -> str | None:
    """Parse exactly one case-sensitive label after outer ASCII-whitespace trim."""
    if not isinstance(raw, str):
        return None
    parsed = raw.strip(" \t\n\r\f\v")
    return parsed if parsed in ANSWERS else None


def parser_metadata() -> dict[str, object]:
    return {
        "allowed_answers": list(ANSWERS),
        "parser_version": PARSER_VERSION,
        "trim": "leading/trailing ASCII whitespace only",
    }
