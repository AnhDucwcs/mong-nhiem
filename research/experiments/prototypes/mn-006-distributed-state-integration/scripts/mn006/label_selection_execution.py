"""Frozen, non-model D1 execution contract for the label-selection diagnostic."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .fingerprinting import canonical_text_bytes, canonical_text_sha256
from .label_selection import (
    DIAGNOSTIC_VERSION,
    DIRECT_STAGE,
    GRAMMAR_AB,
    GRAMMAR_BA,
    LABELS,
    MAPPINGS,
    SOURCE_ORDINALS,
    DiagnosticCase,
    build_plan,
    classify_d1,
    plan_fingerprint,
    score,
)

D1_RUN_ID = "label-selection-d1-run-0001"
EVIDENCE_SCHEMA_VERSION = "mn006-label-selection-d1-evidence-v1"
PARSER_VERSION = "mn006-label-selection-parser-v1"
EVALUATOR_VERSION = "mn006-label-selection-evaluator-v1"
RUNTIME_CONTRACT_VERSION = "mn006-baseline-runtime-v1"
EXPECTED_DIAGNOSTIC_PLAN_SHA256 = "cfa3aac029aa803cfbd546bf9bba3808739f343758acadca12214d53af4aa465"
EXPECTED_D1_REQUEST_COUNT = 16
REQUEST_ORDER_CONTRACT = "D1; source_ordinal_ascending; planner_mapping_order; planner_grammar_order"
D1_REQUEST_PARAMETERS = {
    "chat_template_kwargs": {},
    "max_tokens": 16,
    "seed": 42,
    "temperature": 0.0,
}


class D1ExecutionError(ValueError):
    """Raised when a D1-only execution or retained-record invariant is violated."""


def grammar_language(grammar: str) -> frozenset[str]:
    """Return the literal language of one frozen two-label D1 grammar."""
    if not grammar.endswith("\n") or grammar.count("\n") != 1:
        raise D1ExecutionError("D1 grammar must contain exactly one final LF")
    literals = re.findall(r'"([^"\n]+)"', grammar)
    if grammar.startswith("root ::= ") is False or len(literals) != 2:
        raise D1ExecutionError("D1 grammar does not have exactly two root literals")
    return frozenset(literals)


def build_d1_request_plan() -> tuple[DiagnosticCase, ...]:
    """Consume only the frozen direct-state stage; D2 is intentionally excluded."""
    if plan_fingerprint() != EXPECTED_DIAGNOSTIC_PLAN_SHA256:
        raise D1ExecutionError("diagnostic plan fingerprint differs from the frozen D1 contract")
    cases = tuple(case for case in build_plan() if case.stage == DIRECT_STAGE)
    validate_d1_request_plan(cases)
    return cases


def validate_d1_request_plan(cases: tuple[DiagnosticCase, ...]) -> None:
    """Check the exact 4 × 2 × 2 D1 matrix without constructing D2 requests."""
    if len(cases) != EXPECTED_D1_REQUEST_COUNT:
        raise D1ExecutionError("D1 request count differs from the frozen 16")
    if [case.request_ordinal for case in cases] != list(range(1, 17)):
        raise D1ExecutionError("D1 request order differs from the frozen planner")
    if any(case.stage != DIRECT_STAGE for case in cases):
        raise D1ExecutionError("D1 executor received a non-D1 case")
    if tuple(sorted({case.source_ordinal for case in cases})) != SOURCE_ORDINALS:
        raise D1ExecutionError("D1 source ordinals differ from the frozen set")
    source_relations = {
        ordinal: {case.equal_state for case in cases if case.source_ordinal == ordinal}
        for ordinal in SOURCE_ORDINALS
    }
    if any(len(relations) != 1 for relations in source_relations.values()):
        raise D1ExecutionError("a D1 source ordinal has inconsistent equality relation")
    if sum(next(iter(relations)) for relations in source_relations.values()) != 2:
        raise D1ExecutionError("D1 source set must contain two equality cases")
    if {grammar_language(case.grammar) for case in cases} != {frozenset(LABELS)}:
        raise D1ExecutionError("D1 grammars do not share the frozen A/B language")
    if grammar_language(GRAMMAR_AB) != grammar_language(GRAMMAR_BA):
        raise D1ExecutionError("D1 grammar variants differ in accepted language")
    expected_mappings = {mapping.identifier for mapping in MAPPINGS}
    for ordinal in SOURCE_ORDINALS:
        source_cases = [case for case in cases if case.source_ordinal == ordinal]
        if len(source_cases) != 4:
            raise D1ExecutionError(f"D1 source ordinal {ordinal} lacks four cells")
        if {case.mapping.identifier for case in source_cases} != expected_mappings:
            raise D1ExecutionError(f"D1 source ordinal {ordinal} lacks mapping counterbalance")
        for mapping in MAPPINGS:
            paired = [case for case in source_cases if case.mapping.identifier == mapping.identifier]
            if {case.grammar_order for case in paired} != {"A_then_B", "B_then_A"}:
                raise D1ExecutionError("D1 grammar-order pair is incomplete")
            if len({case.canonical_answer for case in paired}) != 1:
                raise D1ExecutionError("grammar order must not change the canonical D1 answer")
    if any(canonical_text_bytes(case.public_prompt) != case.public_prompt.encode("utf-8") for case in cases):
        raise D1ExecutionError("D1 public prompt is not canonical UTF-8/LF text")


def build_request_payload(case: DiagnosticCase) -> dict[str, object]:
    """Build the future request with no data beyond the frozen D1 case and grammar."""
    if case.stage != DIRECT_STAGE:
        raise D1ExecutionError("D2 or another stage cannot be submitted by the D1 executor")
    if case.grammar not in (GRAMMAR_AB, GRAMMAR_BA):
        raise D1ExecutionError("request grammar differs from the frozen D1 variants")
    if grammar_language(case.grammar) != frozenset(LABELS):
        raise D1ExecutionError("request grammar language differs from A/B")
    prompt_bytes = canonical_text_bytes(case.public_prompt)
    if prompt_bytes != case.public_prompt.encode("utf-8"):
        raise D1ExecutionError("D1 prompt is not canonical UTF-8/LF text")
    return {
        "chat_template_kwargs": D1_REQUEST_PARAMETERS["chat_template_kwargs"],
        "grammar": case.grammar,
        "max_tokens": D1_REQUEST_PARAMETERS["max_tokens"],
        "messages": [{"role": "user", "content": prompt_bytes.decode("utf-8")}],
        "seed": D1_REQUEST_PARAMETERS["seed"],
        "temperature": D1_REQUEST_PARAMETERS["temperature"],
    }


def plan_entry(case: DiagnosticCase) -> dict[str, object]:
    """Expose explicit D1 identity fields for future append-only evidence records."""
    return {
        "canonical_answer": case.canonical_answer,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "equal_state": case.equal_state,
        "grammar": case.grammar,
        "grammar_id": case.grammar_order,
        "mapping": {
            "equal_label": case.mapping.equal_label,
            "identifier": case.mapping.identifier,
            "unequal_label": case.mapping.unequal_label,
        },
        "prompt_byte_count": len(canonical_text_bytes(case.public_prompt)),
        "prompt_sha256": canonical_text_sha256(case.public_prompt),
        "public_prompt": case.public_prompt,
        "query_entities": list(case.query_entities),
        "query_states": list(case.query_states),
        "record_id": case.record_id,
        "request_ordinal": case.request_ordinal,
        "source_case_id": case.source_case_id,
        "source_ordinal": case.source_ordinal,
        "stage": case.stage,
    }


def evaluate_raw_output(case: DiagnosticCase, raw_output: str) -> dict[str, object]:
    """Use the frozen strict A/B parser and grammar-independent canonical label."""
    if case.stage != DIRECT_STAGE:
        raise D1ExecutionError("D1 evaluator received a non-D1 case")
    return {"canonical_answer": case.canonical_answer, "score": float(score(case, raw_output)["correct"]), **score(case, raw_output)}


def summarize_d1_records(records: list[dict[str, Any]], cases: tuple[DiagnosticCase, ...]) -> dict[str, object]:
    """Recompute the frozen D1 classification from a complete retained record sequence."""
    validate_d1_request_plan(cases)
    expected = {case.record_id: case for case in cases}
    complete = len(records) == len(cases) and {record.get("record_id") for record in records} == set(expected)
    complete = complete and not any(record.get("infrastructure_status") != "complete" for record in records)
    if not complete:
        return {
            "classification": "infrastructure_invalid",
            "completed_requests": sum(record.get("infrastructure_status") == "complete" for record in records),
            "expected_requests": len(cases),
            "outcome": "infrastructure_invalid",
        }
    raw_outputs = {str(record["record_id"]): str(record.get("raw_output", "")) for record in records}
    evaluations = {case.record_id: evaluate_raw_output(case, raw_outputs[case.record_id]) for case in cases}
    if any(record.get("evaluation") != evaluations[str(record["record_id"])] for record in records):
        raise D1ExecutionError("stored D1 evaluator result differs from recomputation")
    malformed = sum(bool(evaluation["malformed"]) for evaluation in evaluations.values())
    return {
        "classification": classify_d1(raw_outputs),
        "completed_requests": len(records),
        "expected_requests": len(cases),
        "infrastructure_failure_count": 0,
        "malformed_count": malformed,
        "outcome": "protocol_valid",
        "request_order_contract": REQUEST_ORDER_CONTRACT,
    }


def validate_d1_run_directory(run_dir: Path) -> dict[str, object]:
    """Validate retained D1 evidence only after a future run has written it."""
    cases = build_d1_request_plan()
    metadata = json.loads((run_dir / "metadata.json").read_bytes())
    if metadata.get("diagnostic_plan_sha256") != EXPECTED_DIAGNOSTIC_PLAN_SHA256:
        raise D1ExecutionError("D1 metadata does not identify the frozen diagnostic plan")
    records = [json.loads(line) for line in (run_dir / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    expected_entries = {case.record_id: plan_entry(case) for case in cases}
    for record in records:
        expected = expected_entries.get(record.get("record_id"))
        if expected is None:
            raise D1ExecutionError("retained record is outside the frozen D1 plan")
        for key, value in expected.items():
            if record.get(key) != value:
                raise D1ExecutionError(f"retained D1 record mismatch: {key}")
    summary = summarize_d1_records(records, cases)
    stored = json.loads((run_dir / "summary.json").read_bytes())
    if stored != summary:
        raise D1ExecutionError("stored D1 summary differs from recomputation")
    return summary
