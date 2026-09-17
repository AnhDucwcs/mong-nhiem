"""Static, non-model contract for the explicit-relation direct-rule control."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .fingerprinting import (
    canonical_json_sha256,
    canonical_text_bytes,
    canonical_text_sha256,
)
from .label_selection import GRAMMAR_AB, LABELS, parse_label

CONTRACT_VERSION = "mn006-explicit-relation-direct-rule-v1"
RUN_ID = "explicit-relation-direct-rule-run-0001"
STAGE = "explicit_relation_direct_rule"
RUNTIME_CONTRACT_VERSION = "mn006-baseline-runtime-v1"
PARSER_VERSION = "mn006-label-selection-parser-v1"
EXPECTED_PLAN_SHA256 = "dc40c15a896f5f0413783818c39593b8a9c34eeea3ef4ce284e1b311112bc80a"
CAUSAL_REVIEW_PATH = "research/experiments/prototypes/mn-006-distributed-state-integration/recurring-fixed-label-causal-review.md"
EXPECTED_CAUSAL_REVIEW_SHA256 = "a5e4bbca96d18043d5b0280c076425ba9beedf30feaf149a5645e6196cb8580a"
RELATION_ORDER = ("different", "equal")
RELATION_LABELS = {"equal": "A", "different": "B"}


class ExplicitRelationError(ValueError):
    """Raised when the frozen explicit-relation contract is violated."""


@dataclass(frozen=True)
class ExplicitRelationCase:
    record_id: str
    request_ordinal: int
    relation: str
    canonical_answer: str
    public_prompt: str

    @property
    def grammar(self) -> str:
        return GRAMMAR_AB

    def authority_dict(self) -> dict[str, object]:
        return {
            "canonical_answer": self.canonical_answer,
            "grammar": self.grammar,
            "grammar_id": "A_then_B",
            "public_prompt": self.public_prompt,
            "public_prompt_sha256": canonical_text_sha256(self.public_prompt),
            "record_id": self.record_id,
            "relation": self.relation,
            "request_ordinal": self.request_ordinal,
            "stage": STAGE,
        }


def explicit_relation_prompt(relation: str) -> str:
    if relation not in RELATION_LABELS:
        raise ExplicitRelationError("relation must be exactly equal or different")
    return (
        f"Relation: {relation}\n"
        "Output A if the relation is equal.\n"
        "Output B if the relation is different.\n"
        "Output exactly one label: A or B.\n"
    )


def build_plan() -> tuple[ExplicitRelationCase, ...]:
    cases = tuple(
        ExplicitRelationCase(
            record_id=f"explicit-relation-{ordinal:06d}-{relation}-A_then_B",
            request_ordinal=ordinal,
            relation=relation,
            canonical_answer=RELATION_LABELS[relation],
            public_prompt=explicit_relation_prompt(relation),
        )
        for ordinal, relation in enumerate(RELATION_ORDER, start=1)
    )
    validate_plan(cases)
    return cases


def validate_plan(cases: tuple[ExplicitRelationCase, ...]) -> None:
    if len(cases) != 2 or [case.request_ordinal for case in cases] != [1, 2]:
        raise ExplicitRelationError("plan must contain exactly two ordered records")
    if [case.relation for case in cases] != list(RELATION_ORDER):
        raise ExplicitRelationError("relation order differs from the frozen S1 projection")
    if [case.canonical_answer for case in cases] != ["B", "A"]:
        raise ExplicitRelationError("canonical labels differ from the fixed direct rule")
    for case in cases:
        if case.grammar != GRAMMAR_AB:
            raise ExplicitRelationError("every record must use the fixed G_AB grammar")
        if case.canonical_answer not in LABELS:
            raise ExplicitRelationError("canonical answer falls outside the A/B vocabulary")
        if case.public_prompt != explicit_relation_prompt(case.relation):
            raise ExplicitRelationError("prompt differs from the frozen minimal template")
        if canonical_text_bytes(case.public_prompt) != case.public_prompt.encode("utf-8"):
            raise ExplicitRelationError("prompt is not canonical UTF-8/LF text")


def plan_authority() -> dict[str, object]:
    return {
        "classification_precedence": [
            "explicit_relation_malformed_or_invalid",
            "explicit_relation_direct_rule_supported",
            "fixed_label_preference_persisted",
            "explicit_relation_inconclusive",
        ],
        "contract_version": CONTRACT_VERSION,
        "labels": list(LABELS),
        "parser_version": PARSER_VERSION,
        "prerequisites": {
            "causal_review": {
                "disposition": "next_minimal_diagnostic_identified",
                "path": CAUSAL_REVIEW_PATH,
                "sha256": EXPECTED_CAUSAL_REVIEW_SHA256,
            },
            "s0": {
                "classification": "direct_copy_supported",
                "outcome": "protocol_valid",
                "run_id": "output-selection-s0-run-0001",
            },
            "s1": {
                "classification": "fixed_label_preference_recurred",
                "outcome": "protocol_valid",
                "run_id": "output-selection-s1-run-0001",
            },
        },
        "records": [case.authority_dict() for case in build_plan()],
        "retained_context": {
            "d1": {
                "classification": "fixed_label_preference_supported",
                "execution_prerequisite": False,
                "run_id": "label-selection-d1-run-0001",
            }
        },
        "run_id": RUN_ID,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "stage": STAGE,
    }


def plan_fingerprint() -> str:
    return canonical_json_sha256(plan_authority())


def validate_frozen_plan() -> dict[str, object]:
    authority = plan_authority()
    if canonical_json_sha256(authority) != EXPECTED_PLAN_SHA256:
        raise ExplicitRelationError("explicit-relation plan fingerprint differs from frozen contract")
    return authority


def score(case: ExplicitRelationCase, raw_output: str) -> dict[str, object]:
    parsed = parse_label(raw_output)
    return {"correct": parsed == case.canonical_answer, "malformed": parsed is None, "parsed_answer": parsed}


def classify(results: Mapping[str, str]) -> str:
    cases = build_plan()
    if set(results) != {case.record_id for case in cases}:
        raise ExplicitRelationError("results do not match the frozen two-record plan")
    parsed = {case.record_id: parse_label(results[case.record_id]) for case in cases}
    if any(value is None for value in parsed.values()):
        return "explicit_relation_malformed_or_invalid"
    if all(parsed[case.record_id] == case.canonical_answer for case in cases):
        return "explicit_relation_direct_rule_supported"
    if all(parsed[case.record_id] == "A" for case in cases):
        return "fixed_label_preference_persisted"
    return "explicit_relation_inconclusive"


def summarize_records(records: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    cases = build_plan()
    complete = (
        len(records) == len(cases)
        and [record.get("record_id") for record in records] == [case.record_id for case in cases]
        and [record.get("request_ordinal") for record in records] == [case.request_ordinal for case in cases]
        and all(record.get("infrastructure_status") == "complete" for record in records)
    )
    if not complete:
        return {"classification": None, "outcome": "infrastructure_invalid"}
    results = {str(record["record_id"]): str(record.get("raw_output", "")) for record in records}
    return {"classification": classify(results), "outcome": "protocol_valid"}
