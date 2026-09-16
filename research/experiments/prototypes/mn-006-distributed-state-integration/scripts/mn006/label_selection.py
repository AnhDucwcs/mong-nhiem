"""Static, non-model contract for the MN-006 label-selection diagnostic."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .fingerprinting import (
    canonical_json_sha256,
    canonical_text_bytes,
    canonical_text_sha256,
)
from .inventory import INVENTORY_ROOT, validate_materialized_inventory
from .model import PROFILE_LEVEL_1, SCHEDULE_CONTIGUOUS

DIAGNOSTIC_VERSION = "mn006-label-selection-diagnostic-v1"
DIRECT_STAGE = "D1_direct_mapping"
CONTIGUOUS_STAGE = "D2_contiguous_state_tracking"
LABELS = ("A", "B")
GRAMMAR_AB = 'root ::= "A" | "B"\n'
GRAMMAR_BA = 'root ::= "B" | "A"\n'
GRAMMARS = {"A_then_B": GRAMMAR_AB, "B_then_A": GRAMMAR_BA}
SOURCE_PROFILE = PROFILE_LEVEL_1.identifier
SOURCE_SCHEDULE = SCHEDULE_CONTIGUOUS
SOURCE_ORDINALS = (0, 1, 2, 3)


class LabelSelectionError(ValueError):
    """Raised when a static diagnostic contract invariant is violated."""


@dataclass(frozen=True)
class Mapping:
    identifier: str
    equal_label: str
    unequal_label: str

    def answer_for(self, equal_state: bool) -> str:
        return self.equal_label if equal_state else self.unequal_label


MAPPINGS = (
    Mapping("M1_equal_A", "A", "B"),
    Mapping("M2_equal_B", "B", "A"),
)


@dataclass(frozen=True)
class DiagnosticCase:
    record_id: str
    request_ordinal: int
    stage: str
    source_case_id: str
    source_ordinal: int
    query_entities: tuple[str, str]
    query_states: tuple[str, str]
    equal_state: bool
    mapping: Mapping
    grammar_order: str
    public_prompt: str

    @property
    def grammar(self) -> str:
        return GRAMMARS[self.grammar_order]

    @property
    def canonical_answer(self) -> str:
        return self.mapping.answer_for(self.equal_state)

    def authority_dict(self) -> dict[str, object]:
        return {
            "canonical_answer": self.canonical_answer,
            "equal_state": self.equal_state,
            "grammar": self.grammar,
            "grammar_order": self.grammar_order,
            "mapping": {
                "equal_label": self.mapping.equal_label,
                "identifier": self.mapping.identifier,
                "unequal_label": self.mapping.unequal_label,
            },
            "public_prompt": self.public_prompt,
            "public_prompt_sha256": canonical_text_sha256(self.public_prompt),
            "query_entities": list(self.query_entities),
            "query_states": list(self.query_states),
            "record_id": self.record_id,
            "request_ordinal": self.request_ordinal,
            "source_case_id": self.source_case_id,
            "source_ordinal": self.source_ordinal,
            "stage": self.stage,
        }


def parse_label(text: str) -> str | None:
    """Use the same strict outer-ASCII-trim policy with the diagnostic labels."""
    normalized = text.strip(" \t\n\r\f\v")
    return normalized if normalized in LABELS else None


def _mapping_instruction(mapping: Mapping, query_entities: tuple[str, str]) -> list[str]:
    first, second = query_entities
    return [
        f"For {first} and {second}, use this mapping:",
        f"equal states -> {mapping.equal_label}",
        f"unequal states -> {mapping.unequal_label}",
        "Output exactly one label: A or B.",
    ]


def _direct_prompt(
    query_entities: tuple[str, str], query_states: tuple[str, str], mapping: Mapping
) -> str:
    first, second = query_entities
    first_state, second_state = query_states
    lines = [
        "The final query states are:",
        f"{first} STATE = {first_state}",
        f"{second} STATE = {second_state}",
        *_mapping_instruction(mapping, query_entities),
    ]
    return "\n".join(lines) + "\n"


def _contiguous_prompt(record: dict[str, Any], mapping: Mapping) -> str:
    lines = ["All entities begin in S0."]
    lines.extend(
        f"{event['entity_id']} STATE = {event['assigned_state']}"
        for event in record["source_events"]
    )
    query_entities = tuple(record["query"]["entities"])
    lines.extend(_mapping_instruction(mapping, query_entities))
    return "\n".join(lines) + "\n"


def _load_source_records(root: Path = INVENTORY_ROOT) -> tuple[dict[str, Any], ...]:
    """Read exactly four mechanically selected Level 1 contiguous authority cases."""
    validate_materialized_inventory(root)
    authority_path = root / "authority" / f"{SOURCE_PROFILE}.json"
    records = json.loads(authority_path.read_bytes().decode("utf-8"))["records"]
    selected: list[dict[str, Any]] = []
    for ordinal in SOURCE_ORDINALS:
        case_id = f"mn006-v1-{SOURCE_PROFILE}-{ordinal:06d}-{SOURCE_SCHEDULE}"
        matching = [record for record in records if record["case_id"] == case_id]
        if len(matching) != 1:
            raise LabelSelectionError(f"missing selected source case: {case_id}")
        record = matching[0]
        if record["profile"] != SOURCE_PROFILE or record["schedule_kind"] != SOURCE_SCHEDULE:
            raise LabelSelectionError(f"source condition mismatch: {case_id}")
        query = tuple(record["query"]["entities"])
        if len(query) != 2:
            raise LabelSelectionError(f"query arity mismatch: {case_id}")
        if record["canonical_derived_facts"]["equal_state"] != (
            record["canonical_entity_states"][query[0]] == record["canonical_entity_states"][query[1]]
        ):
            raise LabelSelectionError(f"authority equality mismatch: {case_id}")
        selected.append(record)
    outcomes = [record["canonical_derived_facts"]["equal_state"] for record in selected]
    if outcomes.count(True) != 2 or outcomes.count(False) != 2:
        raise LabelSelectionError("source selection must contain exactly two equal and two unequal cases")
    return tuple(selected)


def build_plan(root: Path = INVENTORY_ROOT) -> tuple[DiagnosticCase, ...]:
    """Build the complete prospective D1 plan and contingent D2 plan without model work."""
    cases: list[DiagnosticCase] = []
    request_ordinal = 1
    for source in _load_source_records(root):
        source_ordinal = int(source["case_id"].split("-")[-2])
        query_entities = tuple(source["query"]["entities"])
        query_states = tuple(source["canonical_entity_states"][entity] for entity in query_entities)
        equal_state = bool(source["canonical_derived_facts"]["equal_state"])
        mappings = MAPPINGS if source_ordinal % 2 == 0 else tuple(reversed(MAPPINGS))
        for mapping in mappings:
            grammar_orders = ("A_then_B", "B_then_A") if mapping.identifier == "M1_equal_A" else ("B_then_A", "A_then_B")
            for grammar_order in grammar_orders:
                record_id = f"d1-{source_ordinal:06d}-{mapping.identifier}-{grammar_order}"
                cases.append(DiagnosticCase(
                    record_id, request_ordinal, DIRECT_STAGE, source["case_id"], source_ordinal,
                    query_entities, query_states, equal_state, mapping, grammar_order,
                    _direct_prompt(query_entities, query_states, mapping),
                ))
                request_ordinal += 1
    for source in _load_source_records(root):
        source_ordinal = int(source["case_id"].split("-")[-2])
        query_entities = tuple(source["query"]["entities"])
        query_states = tuple(source["canonical_entity_states"][entity] for entity in query_entities)
        equal_state = bool(source["canonical_derived_facts"]["equal_state"])
        mappings = MAPPINGS if source_ordinal % 2 == 0 else tuple(reversed(MAPPINGS))
        for mapping in mappings:
            record_id = f"d2-{source_ordinal:06d}-{mapping.identifier}-A_then_B"
            cases.append(DiagnosticCase(
                record_id, request_ordinal, CONTIGUOUS_STAGE, source["case_id"], source_ordinal,
                query_entities, query_states, equal_state, mapping, "A_then_B",
                _contiguous_prompt(source, mapping),
            ))
            request_ordinal += 1
    validate_plan(tuple(cases))
    return tuple(cases)


def validate_plan(cases: tuple[DiagnosticCase, ...]) -> None:
    """Validate the frozen selection, mapping, grammar, and stage boundaries."""
    if len(cases) != 24 or [case.request_ordinal for case in cases] != list(range(1, 25)):
        raise LabelSelectionError("diagnostic plan must contain exactly 24 ordered records")
    d1 = [case for case in cases if case.stage == DIRECT_STAGE]
    d2 = [case for case in cases if case.stage == CONTIGUOUS_STAGE]
    if len(d1) != 16 or len(d2) != 8:
        raise LabelSelectionError("unexpected stage counts")
    if any(case.grammar not in (GRAMMAR_AB, GRAMMAR_BA) for case in cases):
        raise LabelSelectionError("diagnostic grammar differs from frozen A/B variants")
    if any(parse_label(case.canonical_answer) is None for case in cases):
        raise LabelSelectionError("canonical diagnostic answer falls outside A/B")
    if any(canonical_text_bytes(case.public_prompt) != case.public_prompt.encode("utf-8") for case in cases):
        raise LabelSelectionError("diagnostic public prompt is not canonical UTF-8/LF text")
    for ordinal in SOURCE_ORDINALS:
        d1_for_source = [case for case in d1 if case.source_ordinal == ordinal]
        d2_for_source = [case for case in d2 if case.source_ordinal == ordinal]
        if len(d1_for_source) != 4 or len(d2_for_source) != 2:
            raise LabelSelectionError(f"unexpected diagnostic coverage for source ordinal {ordinal}")
        if {case.mapping.identifier for case in d1_for_source} != {mapping.identifier for mapping in MAPPINGS}:
            raise LabelSelectionError("D1 lacks mapping counterbalance")
        if {case.grammar_order for case in d1_for_source} != set(GRAMMARS):
            raise LabelSelectionError("D1 lacks grammar-order counterbalance")
        if {case.mapping.identifier for case in d2_for_source} != {mapping.identifier for mapping in MAPPINGS}:
            raise LabelSelectionError("D2 lacks mapping counterbalance")
        if {case.grammar_order for case in d2_for_source} != {"A_then_B"}:
            raise LabelSelectionError("D2 must use the fixed A-then-B grammar")


def plan_authority(root: Path = INVENTORY_ROOT) -> dict[str, object]:
    """Return the non-measured, reproducible authority representation of the diagnostic plan."""
    cases = build_plan(root)
    return {
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "labels": list(LABELS),
        "records": [case.authority_dict() for case in cases],
        "source_inventory_aggregate_sha256": "8cdcf1e792f495c9a4ca57ddcda865769db01bad8cfab65c9afb4cd225ad2ec9",
        "source_profile": SOURCE_PROFILE,
        "source_schedule": SOURCE_SCHEDULE,
        "source_ordinals": list(SOURCE_ORDINALS),
    }


def plan_fingerprint(root: Path = INVENTORY_ROOT) -> str:
    return canonical_json_sha256(plan_authority(root))


def score(case: DiagnosticCase, raw_output: str) -> dict[str, object]:
    """Apply the frozen diagnostic parser and exact label evaluator."""
    parsed = parse_label(raw_output)
    return {
        "correct": parsed == case.canonical_answer,
        "malformed": parsed is None,
        "parsed_answer": parsed,
    }


def classify_d1(results: dict[str, str], root: Path = INVENTORY_ROOT) -> str:
    """Apply the predeclared direct-mapping outcome categories to exactly D1 records."""
    d1 = [case for case in build_plan(root) if case.stage == DIRECT_STAGE]
    if set(results) != {case.record_id for case in d1}:
        raise LabelSelectionError("D1 results do not match the frozen direct-mapping plan")
    parsed = {case.record_id: parse_label(results[case.record_id]) for case in d1}
    if any(value is None for value in parsed.values()):
        return "direct_mapping_malformed_or_inconclusive"
    stable = True
    for ordinal in SOURCE_ORDINALS:
        for mapping in MAPPINGS:
            paired = [case for case in d1 if case.source_ordinal == ordinal and case.mapping == mapping]
            if len({parsed[case.record_id] for case in paired}) != 1:
                stable = False
    if not stable:
        return "grammar_order_asymmetry_observed"
    if all(parsed[case.record_id] == case.canonical_answer for case in d1):
        return "mapping_following_supported"
    if len(set(parsed.values())) == 1:
        return "fixed_label_preference_supported"
    return "mapping_diagnostic_inconclusive"


def classify_d2(results: dict[str, str], root: Path = INVENTORY_ROOT) -> str:
    """Apply the predeclared contiguous state/relation outcome categories to D2 records."""
    d2 = [case for case in build_plan(root) if case.stage == CONTIGUOUS_STAGE]
    if set(results) != {case.record_id for case in d2}:
        raise LabelSelectionError("D2 results do not match the frozen contiguous plan")
    parsed = {case.record_id: parse_label(results[case.record_id]) for case in d2}
    if any(value is None for value in parsed.values()):
        return "contiguous_mapping_malformed_or_inconclusive"
    if all(parsed[case.record_id] == case.canonical_answer for case in d2):
        return "contiguous_mapping_and_relation_supported"
    if len(set(parsed.values())) == 1:
        return "fixed_label_preference_recurred"
    return "contiguous_state_or_relation_diagnostic_inconclusive"
