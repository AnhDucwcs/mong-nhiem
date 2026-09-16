"""Static, non-model contract for the MN-006 output-selection minimality ladder."""
from __future__ import annotations

from dataclasses import dataclass

from .fingerprinting import (
    canonical_json_sha256,
    canonical_text_bytes,
    canonical_text_sha256,
)
from .label_selection import GRAMMARS, LABELS, parse_label

CONTRACT_VERSION = "mn006-output-selection-minimality-v1"
S0_STAGE = "S0_direct_copy"
S1_STAGE = "S1_direct_relation"
S0_RUN_ID = "output-selection-s0-run-0001"
S1_RUN_ID = "output-selection-s1-run-0001"
RUNTIME_CONTRACT_VERSION = "mn006-baseline-runtime-v1"
EXPECTED_PLAN_SHA256 = "8180ea423a05eeb2930b84cee6102fd94595e13856f1a91e1afe4d599bb8e827"
PARSER_VERSION = "mn006-label-selection-parser-v1"
S0_ORDER = (("A", "A_then_B"), ("B", "B_then_A"), ("B", "A_then_B"), ("A", "B_then_A"))
S1_ORDER = (("S1", "S2"), ("S1", "S1"), ("S2", "S2"), ("S2", "S1"))


class OutputSelectionError(ValueError):
    """Raised when the frozen minimality diagnostic contract is violated."""


@dataclass(frozen=True)
class MinimalityCase:
    record_id: str
    request_ordinal: int
    stage: str
    grammar_order: str
    public_prompt: str
    canonical_answer: str
    target_label: str | None = None
    query_states: tuple[str, str] | None = None

    @property
    def grammar(self) -> str:
        return GRAMMARS[self.grammar_order]

    @property
    def equal_state(self) -> bool | None:
        if self.query_states is None:
            return None
        return self.query_states[0] == self.query_states[1]

    def authority_dict(self) -> dict[str, object]:
        return {
            "canonical_answer": self.canonical_answer,
            "grammar": self.grammar,
            "grammar_id": self.grammar_order,
            "public_prompt": self.public_prompt,
            "public_prompt_sha256": canonical_text_sha256(self.public_prompt),
            "record_id": self.record_id,
            "request_ordinal": self.request_ordinal,
            "stage": self.stage,
            "target_label": self.target_label,
            "query_states": list(self.query_states) if self.query_states is not None else None,
            "equal_state": self.equal_state,
        }


def s0_prompt(target_label: str) -> str:
    if target_label not in LABELS:
        raise OutputSelectionError("S0 target label must be A or B")
    return f"Target label: {target_label}\nOutput exactly the target label.\nAllowed labels: A or B.\n"


def s1_prompt(query_states: tuple[str, str]) -> str:
    first_state, second_state = query_states
    if first_state not in {"S1", "S2"} or second_state not in {"S1", "S2"}:
        raise OutputSelectionError("S1 states must be S1 or S2")
    return (
        f"E01 STATE = {first_state}\n"
        f"E02 STATE = {second_state}\n"
        "Output A if the states are equal.\n"
        "Output B if the states are different.\n"
        "Output exactly one label: A or B.\n"
    )


def build_s0_plan() -> tuple[MinimalityCase, ...]:
    cases = tuple(
        MinimalityCase(
            record_id=f"s0-{ordinal:06d}-target-{target_label}-{grammar_order}",
            request_ordinal=ordinal,
            stage=S0_STAGE,
            grammar_order=grammar_order,
            public_prompt=s0_prompt(target_label),
            canonical_answer=target_label,
            target_label=target_label,
        )
        for ordinal, (target_label, grammar_order) in enumerate(S0_ORDER, start=1)
    )
    validate_s0_plan(cases)
    return cases


def build_s1_plan() -> tuple[MinimalityCase, ...]:
    cases = tuple(
        MinimalityCase(
            record_id=f"s1-{ordinal:06d}-{first_state}-{second_state}-A_then_B",
            request_ordinal=ordinal,
            stage=S1_STAGE,
            grammar_order="A_then_B",
            public_prompt=s1_prompt((first_state, second_state)),
            canonical_answer="A" if first_state == second_state else "B",
            query_states=(first_state, second_state),
        )
        for ordinal, (first_state, second_state) in enumerate(S1_ORDER, start=1)
    )
    validate_s1_plan(cases)
    return cases


def build_plan() -> tuple[MinimalityCase, ...]:
    cases = (*build_s0_plan(), *build_s1_plan())
    validate_plan(cases)
    return cases


def _validate_text(case: MinimalityCase) -> None:
    if case.canonical_answer not in LABELS:
        raise OutputSelectionError("canonical answer must be A or B")
    if case.grammar not in GRAMMARS.values():
        raise OutputSelectionError("grammar differs from frozen A/B variants")
    if canonical_text_bytes(case.public_prompt) != case.public_prompt.encode("utf-8"):
        raise OutputSelectionError("prompt is not canonical UTF-8/LF text")


def validate_s0_plan(cases: tuple[MinimalityCase, ...]) -> None:
    if len(cases) != 4 or [case.request_ordinal for case in cases] != [1, 2, 3, 4]:
        raise OutputSelectionError("S0 must contain exactly four ordered requests")
    if any(case.stage != S0_STAGE for case in cases):
        raise OutputSelectionError("S0 plan contains a non-S0 request")
    if [case.target_label for case in cases] != ["A", "B", "B", "A"]:
        raise OutputSelectionError("S0 target order differs from frozen counterbalance")
    if [case.grammar_order for case in cases] != ["A_then_B", "B_then_A", "A_then_B", "B_then_A"]:
        raise OutputSelectionError("S0 grammar order differs from frozen counterbalance")
    if any(case.query_states is not None or case.equal_state is not None for case in cases):
        raise OutputSelectionError("S0 must not include state or relation content")
    for target_label in LABELS:
        paired = [case for case in cases if case.target_label == target_label]
        if len(paired) != 2 or {case.grammar_order for case in paired} != set(GRAMMARS):
            raise OutputSelectionError("each S0 target must receive both grammar orders")
        if any(case.canonical_answer != target_label for case in paired):
            raise OutputSelectionError("S0 canonical label must copy the explicit target")
    for case in cases:
        _validate_text(case)
        if case.public_prompt != s0_prompt(str(case.target_label)):
            raise OutputSelectionError("S0 prompt differs from frozen template")


def validate_s1_plan(cases: tuple[MinimalityCase, ...]) -> None:
    if len(cases) != 4 or [case.request_ordinal for case in cases] != [1, 2, 3, 4]:
        raise OutputSelectionError("S1 must contain exactly four ordered requests")
    if any(case.stage != S1_STAGE for case in cases):
        raise OutputSelectionError("S1 plan contains a non-S1 request")
    if any(case.grammar_order != "A_then_B" for case in cases):
        raise OutputSelectionError("S1 must use only the fixed G_AB grammar")
    if any(case.target_label is not None for case in cases):
        raise OutputSelectionError("S1 must not include an explicit target label")
    if [case.query_states for case in cases] != list(S1_ORDER):
        raise OutputSelectionError("S1 state-pair order differs from frozen balance")
    if sum(bool(case.equal_state) for case in cases) != 2:
        raise OutputSelectionError("S1 must contain exactly two equal-state cases")
    if {case.canonical_answer for case in cases} != set(LABELS):
        raise OutputSelectionError("S1 must expose both canonical labels")
    if sum(case.canonical_answer == "A" for case in cases) != 2:
        raise OutputSelectionError("S1 must be label balanced")
    for case in cases:
        _validate_text(case)
        if case.public_prompt != s1_prompt(case.query_states or ("", "")):
            raise OutputSelectionError("S1 prompt differs from frozen template")
        if case.canonical_answer != ("A" if case.equal_state else "B"):
            raise OutputSelectionError("S1 direct rule is inconsistent with its relation")


def validate_plan(cases: tuple[MinimalityCase, ...]) -> None:
    if len(cases) != 8:
        raise OutputSelectionError("minimality plan must contain exactly eight prospective records")
    s0 = tuple(case for case in cases if case.stage == S0_STAGE)
    s1 = tuple(case for case in cases if case.stage == S1_STAGE)
    validate_s0_plan(s0)
    validate_s1_plan(s1)
    if len(s0) != 4 or len(s1) != 4:
        raise OutputSelectionError("unexpected stage coverage")


def plan_authority() -> dict[str, object]:
    cases = build_plan()
    return {
        "contract_version": CONTRACT_VERSION,
        "labels": list(LABELS),
        "parser_version": PARSER_VERSION,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "stage_dependencies": {
            S0_STAGE: "eligible_for_separate_future_execution",
            S1_STAGE: "eligible_only_if_S0_classification_is_direct_copy_supported",
        },
        "records": [case.authority_dict() for case in cases],
    }


def plan_fingerprint() -> str:
    return canonical_json_sha256(plan_authority())


def validate_frozen_plan() -> dict[str, object]:
    authority = plan_authority()
    if canonical_json_sha256(authority) != EXPECTED_PLAN_SHA256:
        raise OutputSelectionError("output-selection plan fingerprint differs from frozen contract")
    return authority


def score(case: MinimalityCase, raw_output: str) -> dict[str, object]:
    parsed = parse_label(raw_output)
    return {"correct": parsed == case.canonical_answer, "malformed": parsed is None, "parsed_answer": parsed}


def _require_results(results: dict[str, str], cases: tuple[MinimalityCase, ...], stage: str) -> dict[str, str | None]:
    if set(results) != {case.record_id for case in cases}:
        raise OutputSelectionError(f"{stage} results do not match the frozen plan")
    return {case.record_id: parse_label(results[case.record_id]) for case in cases}


def classify_s0(results: dict[str, str]) -> str:
    cases = build_s0_plan()
    parsed = _require_results(results, cases, "S0")
    if any(value is None for value in parsed.values()):
        return "direct_copy_malformed_or_invalid"
    for target_label in LABELS:
        paired = [case for case in cases if case.target_label == target_label]
        if len({parsed[case.record_id] for case in paired}) != 1:
            return "grammar_order_asymmetry_observed"
    if all(parsed[case.record_id] == case.canonical_answer for case in cases):
        return "direct_copy_supported"
    if len(set(parsed.values())) == 1:
        return "fixed_label_preference_persisted"
    return "direct_copy_inconclusive"


def s1_eligible(s0_classification: str) -> bool:
    return s0_classification == "direct_copy_supported"


def require_s1_eligibility(s0_classification: str) -> None:
    if not s1_eligible(s0_classification):
        raise OutputSelectionError("S1 is blocked unless S0 is exactly direct_copy_supported")


def classify_s1(results: dict[str, str], *, s0_classification: str) -> str:
    require_s1_eligibility(s0_classification)
    cases = build_s1_plan()
    parsed = _require_results(results, cases, "S1")
    if any(value is None for value in parsed.values()):
        return "direct_relation_malformed_or_invalid"
    if all(parsed[case.record_id] == case.canonical_answer for case in cases):
        return "direct_relation_supported"
    if len(set(parsed.values())) == 1:
        return "fixed_label_preference_recurred"
    return "direct_relation_inconclusive"
