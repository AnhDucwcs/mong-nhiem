"""Static direct-state-vector qualification contract for MN-006."""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from itertools import product
from pathlib import Path
from typing import Any

from .fingerprinting import (
    canonical_json_bytes,
    canonical_json_sha256,
    canonical_text_bytes,
    canonical_text_sha256,
    sha256_bytes,
)
from .generation import generate_pair
from .inventory import INVENTORY_ROOT, ROOT_SEED, validate_materialized_inventory
from .model import ENTITY_IDS, PROFILE_LEVEL_2, SCHEDULE_CONTIGUOUS, STATES, SourceEvent
from .oracle import replay

CONTRACT_VERSION = "mn006-direct-state-vector-interface-v1"
QUALIFICATION_CONTRACT_VERSION = "mn006-direct-state-vector-qualification-v1"
RUN_ID = "direct-state-vector-qualification-run-0001"
STAGE = "direct_state_vector_qualification"
PARSER_VERSION = "mn006-direct-state-vector-parser-v1"
EVALUATOR_VERSION = "mn006-direct-state-vector-evaluator-v1"
RUNTIME_CONTRACT_VERSION = "mn006-baseline-runtime-v1"
EXPECTED_INVENTORY_SHA256 = "8cdcf1e792f495c9a4ca57ddcda865769db01bad8cfab65c9afb4cd225ad2ec9"
EXPECTED_REDESIGN_SHA256 = "ca328e63d2fbeaa84de4996b74138b649a025ba9b57bf7d4d8d9743600818698"
EXPECTED_PLAN_SHA256 = "5a487200b0dd72275d37482bc0c3c5cd09feed483419223005519b5034064bbc"

EXPERIMENT_ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = EXPERIMENT_ROOT / "definition" / "direct-state-vector-qualification-v1" / "plan.json"
REDESIGN_PATH = EXPERIMENT_ROOT / "measurement-interface-redesign.md"
REDESIGN_RELATIVE_PATH = "research/experiments/prototypes/mn-006-distributed-state-integration/measurement-interface-redesign.md"

STATE_VOCABULARY = STATES
VECTOR_ORDER = tuple(product(STATE_VOCABULARY, repeat=2))
Q0_LAYER = "Q0_exact_vector_output"
Q1_LAYER = "Q1_task_bearing_contiguous_endpoint"
Q1_PROFILE = PROFILE_LEVEL_2.identifier
DIRECT_STATE_VECTOR_GRAMMAR = 'root ::= state "," state\nstate ::= "S0" | "S1" | "S2"\n'

# Each sequence is three direct assignments beginning from the frozen implicit S0.
# Query histories occupy the first two positions; remaining positions map to active
# non-query entities in canonical entity-ID order. Every row totals S0/S1/S2 = 8/8/8.
Q1_HISTORY_TEMPLATES: dict[tuple[str, str], tuple[tuple[str, str, str], ...]] = {
    ("S0", "S0"): (("S1", "S2", "S0"), ("S1", "S2", "S0"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2")),
    ("S0", "S1"): (("S1", "S2", "S0"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2")),
    ("S0", "S2"): (("S1", "S2", "S0"), ("S1", "S0", "S2"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2")),
    ("S1", "S0"): (("S1", "S0", "S1"), ("S1", "S2", "S0"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2")),
    ("S1", "S1"): (("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2")),
    ("S1", "S2"): (("S1", "S0", "S1"), ("S1", "S0", "S2"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2")),
    ("S2", "S0"): (("S1", "S0", "S2"), ("S1", "S2", "S0"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2")),
    ("S2", "S1"): (("S1", "S0", "S2"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2")),
    ("S2", "S2"): (("S1", "S0", "S2"), ("S1", "S0", "S2"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S1", "S0", "S1"), ("S2", "S0", "S2"), ("S2", "S0", "S2"), ("S2", "S0", "S2")),
}


class DirectStateVectorError(ValueError):
    """Raised when the frozen direct-state-vector qualification contract is violated."""


@dataclass(frozen=True)
class QualificationSource:
    """Qualification-only, contiguous source facts under the unchanged transition semantics."""

    source_id: str
    inherited_baseline_case_id: str
    expected_vector: tuple[str, str]
    query_entities: tuple[str, str]
    entity_permutation: tuple[str, ...]
    entity_histories: Mapping[str, tuple[str, str, str]]
    source_events: tuple[SourceEvent, ...]

    def authority_dict(self) -> dict[str, object]:
        return {
            "entity_histories": {entity: list(history) for entity, history in self.entity_histories.items()},
            "entity_permutation": list(self.entity_permutation),
            "expected_vector": list(self.expected_vector),
            "inherited_baseline_case_id": self.inherited_baseline_case_id,
            "profile": Q1_PROFILE,
            "query_entities": list(self.query_entities),
            "schedule_kind": SCHEDULE_CONTIGUOUS,
            "source_events": [event.public_dict() for event in self.source_events],
            "source_id": self.source_id,
        }


@dataclass(frozen=True)
class DirectStateVectorCase:
    """One non-model qualification cell under the frozen state-vector interface."""

    layer: str
    record_id: str
    request_ordinal: int
    expected_vector: tuple[str, str]
    public_prompt: str
    source: QualificationSource | None = None

    @property
    def grammar(self) -> str:
        return DIRECT_STATE_VECTOR_GRAMMAR

    def authority_dict(self) -> dict[str, object]:
        return {
            "expected_vector": list(self.expected_vector),
            "grammar": self.grammar,
            "grammar_id": "ordered_two_state_vector_v1",
            "layer": self.layer,
            "public_prompt": self.public_prompt,
            "public_prompt_sha256": canonical_text_sha256(self.public_prompt),
            "record_id": self.record_id,
            "request_ordinal": self.request_ordinal,
            "source": self.source.authority_dict() if self.source is not None else None,
            "stage": STAGE,
        }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DirectStateVectorError(message)


def vector_text(vector: tuple[str, str]) -> str:
    """Render the one canonical bare ordered vector form."""
    _require(vector in VECTOR_ORDER, "vector falls outside the frozen ordered state space")
    return f"{vector[0]},{vector[1]}"


def parse_vector(raw_output: str) -> tuple[str, str] | None:
    """Parse exactly two ordered state tokens after only outer ASCII whitespace trim."""
    if not isinstance(raw_output, str):
        return None
    candidate = raw_output.strip(" \t\n\r\f\v")
    parts = candidate.split(",")
    if len(parts) != 2 or any(part not in STATE_VOCABULARY for part in parts):
        return None
    return (parts[0], parts[1])


def q0_prompt(vector: tuple[str, str]) -> str:
    """Supply two semantic state values without supplying their serialized answer bytes."""
    _require(vector in VECTOR_ORDER, "Q0 vector falls outside the frozen state space")
    return (
        f"First query state: {vector[0]}\n"
        f"Second query state: {vector[1]}\n"
        "Output exactly two state tokens in this order, separated by one comma.\n"
    )


def q1_prompt(source: QualificationSource) -> str:
    """Render a state-bearing contiguous case without the v1 equality adapter."""
    first, second = source.query_entities
    lines = ["All entities begin in S0."]
    lines.extend(f"{event.entity_id} STATE = {event.assigned_state}" for event in source.source_events)
    lines.extend(
        (
            f"For {first} and {second}, output their final states in this order.",
            "Output exactly two state tokens from S0, S1, S2 separated by one comma.",
        )
    )
    return "\n".join(lines) + "\n"


@cache
def _inherited_query_metadata() -> dict[tuple[str, str], tuple[tuple[str, str], tuple[str, ...], str]]:
    """Use existing primary-inventory query identities and contiguous scheduler permutations."""
    manifest = validate_materialized_inventory(INVENTORY_ROOT)
    _require(
        manifest.get("aggregate_inventory_sha256") == EXPECTED_INVENTORY_SHA256,
        "canonical baseline inventory fingerprint differs",
    )
    selected: dict[tuple[str, str], tuple[tuple[str, str], tuple[str, ...], str]] = {}
    for ordinal in range(32):
        case = generate_pair(PROFILE_LEVEL_2, ordinal, ROOT_SEED).contiguous
        vector = tuple(case.canonical_entity_states[entity] for entity in case.core.query_entities)
        _require(vector in VECTOR_ORDER, "inherited case has a state outside the frozen vector space")
        selected.setdefault(vector, (case.core.query_entities, case.core.entity_permutation, case.case_id))
    _require(set(selected) == set(VECTOR_ORDER), "primary contiguous inventory does not cover every ordered state vector")
    return selected


@cache
def _qualification_source(vector: tuple[str, str]) -> QualificationSource:
    """Build one deterministic extra qualification source with balanced global state-token counts."""
    metadata = _inherited_query_metadata()
    query_entities, permutation, inherited_case_id = metadata[vector]
    template = Q1_HISTORY_TEMPLATES.get(vector)
    _require(template is not None and len(template) == len(ENTITY_IDS), "Q1 history template differs from frozen vector space")
    non_query_entities = tuple(entity for entity in ENTITY_IDS if entity not in query_entities)
    entity_order = query_entities + non_query_entities
    histories = {entity: history for entity, history in zip(entity_order, template, strict=True)}
    _require(set(histories) == set(ENTITY_IDS), "Q1 histories do not cover exactly the active primary entities")
    _require(tuple(histories[entity][-1] for entity in query_entities) == vector, "Q1 query histories do not end at expected vector")
    counts = Counter(state for history in histories.values() for state in history)
    _require(counts == Counter({"S0": 8, "S1": 8, "S2": 8}), "Q1 state-token frequency is not balanced")
    for history in histories.values():
        predecessor = "S0"
        for state in history:
            _require(state in STATE_VOCABULARY and state != predecessor, "Q1 contains an invalid or no-op assignment")
            predecessor = state
    events = tuple(
        SourceEvent(
            event_id=f"{entity}-{history_ordinal}",
            global_ordinal=global_ordinal,
            entity_id=entity,
            assigned_state=histories[entity][history_ordinal - 1],
        )
        for global_ordinal, (entity, history_ordinal) in enumerate(
            ((entity, history_ordinal) for entity in permutation for history_ordinal in range(1, 4)),
            start=1,
        )
    )
    replayed = replay(events, ENTITY_IDS)
    _require(tuple(replayed.entity_states[entity] for entity in query_entities) == vector, "Q1 replay differs from expected vector")
    return QualificationSource(
        source_id=f"mn006-direct-state-vector-q1-{vector[0]}-{vector[1]}",
        inherited_baseline_case_id=inherited_case_id,
        expected_vector=vector,
        query_entities=query_entities,
        entity_permutation=permutation,
        entity_histories=histories,
        source_events=events,
    )


def build_q0_plan() -> tuple[DirectStateVectorCase, ...]:
    cases = tuple(
        DirectStateVectorCase(
            layer=Q0_LAYER,
            record_id=f"q0-{ordinal:02d}-{first}-{second}",
            request_ordinal=ordinal,
            expected_vector=(first, second),
            public_prompt=q0_prompt((first, second)),
        )
        for ordinal, (first, second) in enumerate(VECTOR_ORDER, start=1)
    )
    validate_q0_plan(cases)
    return cases


def build_q1_plan() -> tuple[DirectStateVectorCase, ...]:
    cases = tuple(
        DirectStateVectorCase(
            layer=Q1_LAYER,
            record_id=f"q1-{ordinal:02d}-{first}-{second}",
            request_ordinal=ordinal + len(VECTOR_ORDER),
            expected_vector=(first, second),
            public_prompt=q1_prompt(_qualification_source((first, second))),
            source=_qualification_source((first, second)),
        )
        for ordinal, (first, second) in enumerate(VECTOR_ORDER, start=1)
    )
    validate_q1_plan(cases)
    return cases


def _validate_common_plan(cases: Sequence[DirectStateVectorCase], layer: str, ordinals: Sequence[int]) -> None:
    _require(len(cases) == len(VECTOR_ORDER), f"{layer} must contain exactly nine records")
    _require([case.request_ordinal for case in cases] == list(ordinals), f"{layer} request order differs")
    _require([case.expected_vector for case in cases] == list(VECTOR_ORDER), f"{layer} vector order differs")
    _require(len({case.record_id for case in cases}) == len(cases), f"{layer} record IDs are not unique")
    for case in cases:
        _require(case.layer == layer, f"record is not in {layer}")
        _require(case.grammar == DIRECT_STATE_VECTOR_GRAMMAR, "record grammar differs from the frozen vector grammar")
        _require(canonical_text_bytes(case.public_prompt) == case.public_prompt.encode("utf-8"), "prompt is not canonical UTF-8/LF")
        _require(parse_vector(vector_text(case.expected_vector)) == case.expected_vector, "canonical vector is not parser-valid")


def validate_q0_plan(cases: Sequence[DirectStateVectorCase]) -> None:
    _validate_common_plan(cases, Q0_LAYER, range(1, 10))
    for case in cases:
        _require(case.source is None, "Q0 must not use source histories")
        _require(case.public_prompt == q0_prompt(case.expected_vector), "Q0 prompt differs from frozen template")
        _require(vector_text(case.expected_vector) not in case.public_prompt, "Q0 exposes serialized answer bytes")


def _validate_q1_no_leakage(case: DirectStateVectorCase) -> None:
    source = case.source
    _require(source is not None, "Q1 lacks qualification source facts")
    _require(case.expected_vector == source.expected_vector, "Q1 expected vector differs from source")
    _require(case.public_prompt == q1_prompt(source), "Q1 prompt differs from the frozen direct-state serializer")
    _require(vector_text(case.expected_vector) not in case.public_prompt, "Q1 prompt exposes serialized answer bytes")
    _require("VALID" not in case.public_prompt and "INVALID" not in case.public_prompt, "Q1 retains the v1 answer vocabulary")
    _require("equal" not in case.public_prompt.casefold() and "different" not in case.public_prompt.casefold(), "Q1 retains equality reasoning")
    for forbidden in ("canonical", "derived", "provenance", "history_ordinal", "target answer"):
        _require(forbidden not in case.public_prompt.casefold(), f"Q1 exposes authority metadata: {forbidden}")
    _require(source.entity_permutation == tuple(source.entity_permutation), "Q1 source permutation is malformed")
    for entity in source.query_entities:
        _require(sum(event.entity_id == entity for event in source.source_events) == 3, "Q1 query history count differs")
        _require(f"{entity} STATE =" in case.public_prompt, "Q1 omits a query source event")


def validate_q1_plan(cases: Sequence[DirectStateVectorCase]) -> None:
    _validate_common_plan(cases, Q1_LAYER, range(10, 19))
    for case in cases:
        source = case.source
        _require(source is not None, "Q1 lacks qualification source")
        _require(len(source.source_events) == PROFILE_LEVEL_2.total_events, "Q1 source event count differs from primary profile")
        _require(source.query_entities == tuple(source.query_entities) and len(set(source.query_entities)) == 2, "Q1 query identity differs")
        _validate_q1_no_leakage(case)


def build_plan() -> tuple[DirectStateVectorCase, ...]:
    cases = build_q0_plan() + build_q1_plan()
    validate_plan(cases)
    return cases


def q1_no_leakage_audit() -> dict[str, object]:
    """Return deterministic audit facts distinguishing legitimate replay from serializer leakage."""
    cases = build_q1_plan()
    slot_pairs = []
    first_before_second = 0
    second_before_first = 0
    frequency_signatures: set[tuple[tuple[str, int], ...]] = set()
    for case in cases:
        source = case.source
        _require(source is not None, "Q1 audit lacks source")
        first_slot = source.entity_permutation.index(source.query_entities[0]) + 1
        second_slot = source.entity_permutation.index(source.query_entities[1]) + 1
        slot_pairs.append([first_slot, second_slot])
        first_before_second += int(first_slot < second_slot)
        second_before_first += int(second_slot < first_slot)
        counts = Counter(event.assigned_state for event in source.source_events)
        frequency_signatures.add(tuple(sorted(counts.items())))
    return {
        "answer_vector_not_serialized_in_prompt": True,
        "authority_metadata_not_rendered": True,
        "first_query_before_second_count": first_before_second,
        "query_entity_slot_pairs": slot_pairs,
        "query_order_matches_event_order": False,
        "second_query_before_first_count": second_before_first,
        "state_frequency_signature": [list(pair) for pair in sorted(frequency_signatures)],
        "state_frequency_uniquely_identifies_vector": False,
        "unmarked_latest_assignment_recovery_is_legitimate": True,
    }


def validate_plan(cases: Sequence[DirectStateVectorCase]) -> None:
    _require(len(cases) == 18, "qualification plan must contain exactly eighteen records")
    _require([case.request_ordinal for case in cases] == list(range(1, 19)), "qualification request order differs")
    q0 = tuple(case for case in cases if case.layer == Q0_LAYER)
    q1 = tuple(case for case in cases if case.layer == Q1_LAYER)
    _require(len(q0) == 9 and len(q1) == 9, "qualification layers differ from the frozen 9+9 contract")
    _require(tuple(cases[:9]) == q0 and tuple(cases[9:]) == q1, "qualification layers are not ordered Q0 then Q1")
    validate_q0_plan(q0)
    validate_q1_plan(q1)
    audit = q1_no_leakage_audit()
    _require(audit["first_query_before_second_count"] > 0, "Q1 query order is never earlier in source order")
    _require(audit["second_query_before_first_count"] > 0, "Q1 query order is never later in source order")
    _require(not audit["state_frequency_uniquely_identifies_vector"], "Q1 state-frequency signature leaks an answer vector")


def plan_authority() -> dict[str, object]:
    return {
        "classification_contract": {
            "infrastructure_invalid": {"classification": None, "outcome": "infrastructure_invalid"},
            "protocol_valid": [
                "direct_state_vector_interface_qualified",
                "direct_state_vector_interface_blocked",
            ],
        },
        "contract_version": CONTRACT_VERSION,
        "grammar": DIRECT_STATE_VECTOR_GRAMMAR,
        "grammar_id": "ordered_two_state_vector_v1",
        "layers": {
            "Q0": {"record_count": 9, "purpose": "exact_vector_output"},
            "Q1": {
                "profile": Q1_PROFILE,
                "record_count": 9,
                "schedule_kind": SCHEDULE_CONTIGUOUS,
                "purpose": "task_bearing_contiguous_endpoint",
                "source_strategy": "qualification_only_histories_reuse_primary_query_identity_and_permutation",
            },
        },
        "no_leakage_audit": q1_no_leakage_audit(),
        "parser": {
            "parser_version": PARSER_VERSION,
            "trim": "leading/trailing ASCII whitespace only",
            "vector_form": "STATE,STATE",
        },
        "prerequisites": {
            "measurement_interface_redesign": {
                "disposition": "single_measurement_interface_candidate_identified",
                "path": REDESIGN_RELATIVE_PATH,
                "sha256": EXPECTED_REDESIGN_SHA256,
            },
            "semantic_inventory": {
                "aggregate_sha256": EXPECTED_INVENTORY_SHA256,
                "inventory_version": "mn006-v1-baseline-inventory-1",
            },
        },
        "qualification_contract_version": QUALIFICATION_CONTRACT_VERSION,
        "qualification_decision": {
            "exact_requirement": "Q0_9_of_9_and_Q1_9_of_9",
            "failure_result": "direct_state_vector_interface_blocked",
            "success_result": "direct_state_vector_interface_qualified",
        },
        "records": [case.authority_dict() for case in build_plan()],
        "run_id": RUN_ID,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "stage": STAGE,
        "state_vocabulary": list(STATE_VOCABULARY),
    }


def plan_fingerprint() -> str:
    return canonical_json_sha256(plan_authority())


def validate_frozen_plan() -> dict[str, object]:
    authority = plan_authority()
    _require(plan_fingerprint() == EXPECTED_PLAN_SHA256, "direct-state-vector plan fingerprint differs from frozen contract")
    _require(PLAN_PATH.is_file(), "direct-state-vector authority plan is missing")
    payload = PLAN_PATH.read_bytes()
    _require(b"\r\n" not in payload, "direct-state-vector authority plan contains CRLF")
    _require(sha256_bytes(payload) == EXPECTED_PLAN_SHA256, "direct-state-vector authority plan physical fingerprint differs")
    _require(payload == canonical_json_bytes(authority), "direct-state-vector authority plan bytes differ from static contract")
    _require(REDESIGN_PATH.is_file(), "measurement-interface redesign prerequisite is missing")
    _require(sha256_bytes(REDESIGN_PATH.read_bytes()) == EXPECTED_REDESIGN_SHA256, "measurement-interface redesign prerequisite differs")
    return authority


def score(case: DirectStateVectorCase, raw_output: str) -> dict[str, object]:
    parsed = parse_vector(raw_output)
    return {
        "correct": parsed == case.expected_vector,
        "expected_vector": list(case.expected_vector),
        "malformed": parsed is None,
        "parsed_vector": list(parsed) if parsed is not None else None,
    }


def classify_results(results: Mapping[str, str]) -> dict[str, object]:
    cases = build_plan()
    _require(set(results) == {case.record_id for case in cases}, "results do not match the frozen eighteen-record plan")
    scores = {case.record_id: score(case, results[case.record_id]) for case in cases}
    q0_scores = [scores[case.record_id] for case in cases if case.layer == Q0_LAYER]
    q1_scores = [scores[case.record_id] for case in cases if case.layer == Q1_LAYER]
    malformed = any(bool(value["malformed"]) for value in scores.values())
    exact = all(bool(value["correct"]) for value in scores.values())
    status = (
        "malformed_or_serialization_invalid"
        if malformed
        else "exact_qualification_success"
        if exact
        else "exact_qualification_failure"
    )
    return {
        "classification": "direct_state_vector_interface_qualified" if exact else "direct_state_vector_interface_blocked",
        "layers": {
            "Q0": {
                "correct": sum(bool(value["correct"]) for value in q0_scores),
                "expected": 9,
                "malformed": sum(bool(value["malformed"]) for value in q0_scores),
            },
            "Q1": {
                "correct": sum(bool(value["correct"]) for value in q1_scores),
                "expected": 9,
                "malformed": sum(bool(value["malformed"]) for value in q1_scores),
            },
        },
        "outcome": "protocol_valid",
        "qualification_status": status,
    }


def summarize_records(records: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    cases = build_plan()
    complete = (
        len(records) == len(cases)
        and [record.get("record_id") for record in records] == [case.record_id for case in cases]
        and [record.get("request_ordinal") for record in records] == [case.request_ordinal for case in cases]
        and all(record.get("infrastructure_status") == "complete" for record in records)
    )
    if not complete:
        return {
            "classification": None,
            "outcome": "infrastructure_invalid",
            "qualification_status": "infrastructure_invalid",
        }
    return classify_results({str(record["record_id"]): str(record.get("raw_output", "")) for record in records})
