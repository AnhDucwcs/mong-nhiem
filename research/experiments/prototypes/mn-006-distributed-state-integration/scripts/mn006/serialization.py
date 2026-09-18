"""Public/evaluator/authority record boundaries for frozen MN-006 v1 cases."""
from __future__ import annotations

from typing import Any

from .fingerprinting import canonical_json_sha256, canonical_text_sha256
from .model import (
    ANSWERS,
    GENERATOR_VERSION,
    INITIAL_STATE,
    PARSER_VERSION,
    RULE_ID,
    SEMANTIC_CONTRACT_VERSION,
    VALIDATOR_VERSION,
    GeneratedCase,
)


def question_text(query_entities: tuple[str, str]) -> str:
    first, second = query_entities
    return (
        f"For {first} and {second}, output VALID if their states are equal; otherwise output INVALID.\n"
        "Output exactly one label: VALID or INVALID."
    )


def public_record(case: GeneratedCase) -> dict[str, Any]:
    """Return only model-visible source facts and the shared fixed instruction."""
    return {
        "allowed_answers": list(ANSWERS),
        "case_id": case.case_id,
        "initial_state": INITIAL_STATE,
        "profile": case.core.profile.identifier,
        "public_serialization_version": SEMANTIC_CONTRACT_VERSION,
        "query": {
            "entities": list(case.core.query_entities),
            "question": question_text(case.core.query_entities),
            "rule_id": RULE_ID,
        },
        "schedule_kind": case.schedule_kind,
        "source_events": [event.public_dict() for event in case.source_events],
    }


def evaluator_record(case: GeneratedCase) -> dict[str, Any]:
    """Return the minimal evaluator-only answer and strict parser metadata."""
    return {
        "allowed_answers": list(ANSWERS),
        "canonical_answer": case.canonical_answer,
        "case_id": case.case_id,
        "parser": {
            "case_sensitive": True,
            "parser_version": PARSER_VERSION,
            "trim": "leading/trailing ASCII whitespace only",
        },
    }


def serialize_public_text(case: GeneratedCase) -> str:
    """Render the frozen source grammar; it contains no authority-only values."""
    lines = ["All entities begin in S0."]
    lines.extend(f"{event.entity_id} STATE = {event.assigned_state}" for event in case.source_events)
    lines.extend(question_text(case.core.query_entities).splitlines())
    return "\n".join(lines) + "\n"


def _authority_core_record(case: GeneratedCase) -> dict[str, Any]:
    return {
        "answer_class": case.core.answer_class,
        "canonical_answer": case.canonical_answer,
        "canonical_derived_facts": dict(case.canonical_derived_facts),
        "canonical_entity_states": dict(case.canonical_entity_states),
        "case_id": case.case_id,
        "entity_histories": {entity_id: list(history) for entity_id, history in case.core.entity_histories.items()},
        "entities": list(case.core.profile.active_entities),
        "event_provenance": {
            event_id: value.authority_dict() for event_id, value in case.event_provenance.items()
        },
        "generation_metadata": {
            "generator_version": GENERATOR_VERSION,
            "pair_id": case.core.pair_id,
            "root_seed": case.core.root_seed,
            "subseeds": dict(case.core.subseeds),
            "validator_version": VALIDATOR_VERSION,
        },
        "initial_state": INITIAL_STATE,
        "interleaving_metrics": dict(case.interleaving_metrics),
        "profile": case.core.profile.identifier,
        "query": {"entities": list(case.core.query_entities), "rule_id": RULE_ID},
        "schedule_kind": case.schedule_kind,
        "schema_version": SEMANTIC_CONTRACT_VERSION,
        "semantic_contract_version": SEMANTIC_CONTRACT_VERSION,
        "source_events": [event.public_dict() for event in case.source_events],
    }


def authority_record(case: GeneratedCase) -> dict[str, Any]:
    """Return provenance-rich authority data with non-self-referential hashes."""
    core = _authority_core_record(case)
    core_hash = canonical_json_sha256(core)
    result = dict(core)
    metadata = dict(core["generation_metadata"])
    metadata["canonical_hashes"] = {
        "authority_core_sha256": core_hash,
        "evaluator_json_sha256": canonical_json_sha256(evaluator_record(case)),
        "public_json_sha256": canonical_json_sha256(public_record(case)),
        "public_text_sha256": canonical_text_sha256(serialize_public_text(case)),
    }
    result["generation_metadata"] = metadata
    return result
