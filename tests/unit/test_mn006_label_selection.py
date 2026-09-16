from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

from mn006 import label_selection as diagnostic

AUDIT = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
    / "definition"
    / "label-selection-diagnostic-v1"
    / "static-audit.json"
)


def _plan() -> tuple[diagnostic.DiagnosticCase, ...]:
    return diagnostic.build_plan()


def test_frozen_label_and_grammar_contract() -> None:
    assert diagnostic.DIAGNOSTIC_VERSION == "mn006-label-selection-diagnostic-v1"
    assert diagnostic.LABELS == ("A", "B")
    assert diagnostic.GRAMMAR_AB == 'root ::= "A" | "B"\n'
    assert diagnostic.GRAMMAR_BA == 'root ::= "B" | "A"\n'
    assert diagnostic.SOURCE_ORDINALS == (0, 1, 2, 3)


def test_static_audit_fingerprints_the_exact_plan_and_tokenizer_findings() -> None:
    audit = json.loads(AUDIT.read_bytes().decode("utf-8"))
    assert audit["diagnostic_plan_sha256"] == diagnostic.plan_fingerprint()
    assert audit["tokenizer_audit"]["labels"]["A"]["at_answer_start"] == [32]
    assert audit["tokenizer_audit"]["labels"]["B"]["at_answer_start"] == [33]
    assert audit["grammar_audit"]["static_conclusion"] == (
        "no obvious structural grammar-acceptance or termination asymmetry found"
    )


def test_plan_is_small_balanced_and_fingerprinted() -> None:
    plan = _plan()
    direct = [case for case in plan if case.stage == diagnostic.DIRECT_STAGE]
    contiguous = [case for case in plan if case.stage == diagnostic.CONTIGUOUS_STAGE]
    assert len(plan) == 24
    assert len(direct) == 16
    assert len(contiguous) == 8
    assert [case.request_ordinal for case in plan] == list(range(1, 25))
    assert sum(case.equal_state for case in plan) == 12
    assert sum(case.canonical_answer == "A" for case in plan) == 12
    assert sum(case.canonical_answer == "B" for case in plan) == 12
    assert diagnostic.plan_fingerprint() == "cfa3aac029aa803cfbd546bf9bba3808739f343758acadca12214d53af4aa465"


def test_each_source_case_has_mapping_and_grammar_counterfactuals() -> None:
    plan = _plan()
    for ordinal in diagnostic.SOURCE_ORDINALS:
        direct = [
            case
            for case in plan
            if case.stage == diagnostic.DIRECT_STAGE and case.source_ordinal == ordinal
        ]
        contiguous = [
            case
            for case in plan
            if case.stage == diagnostic.CONTIGUOUS_STAGE and case.source_ordinal == ordinal
        ]
        assert len(direct) == 4
        assert len(contiguous) == 2
        assert {case.mapping.identifier for case in direct} == {"M1_equal_A", "M2_equal_B"}
        assert {case.grammar_order for case in direct} == {"A_then_B", "B_then_A"}
        assert {case.mapping.identifier for case in contiguous} == {"M1_equal_A", "M2_equal_B"}
        assert {case.grammar_order for case in contiguous} == {"A_then_B"}
        assert {case.canonical_answer for case in contiguous} == {"A", "B"}


def test_prompts_are_canonical_and_keep_d1_and_d2_causally_separate() -> None:
    plan = _plan()
    direct = next(case for case in plan if case.stage == diagnostic.DIRECT_STAGE)
    contiguous = next(case for case in plan if case.stage == diagnostic.CONTIGUOUS_STAGE)
    assert direct.public_prompt.startswith("The final query states are:\n")
    assert "All entities begin" not in direct.public_prompt
    assert contiguous.public_prompt.startswith("All entities begin in S0.\n")
    assert "The final query states" not in contiguous.public_prompt
    for case in plan:
        assert case.public_prompt.endswith("\n")
        assert "\r\n" not in case.public_prompt
        assert case.grammar in diagnostic.GRAMMARS.values()
        assert case.canonical_answer in diagnostic.LABELS


def test_parser_remains_strict() -> None:
    assert diagnostic.parse_label("A") == "A"
    assert diagnostic.parse_label(" B \n") == "B"
    for value in ("a", "A.", "Answer: A", "A B", "", "VALID"):
        assert diagnostic.parse_label(value) is None


def test_predeclared_d1_outcome_categories() -> None:
    direct = [case for case in _plan() if case.stage == diagnostic.DIRECT_STAGE]
    perfect = {case.record_id: case.canonical_answer for case in direct}
    assert diagnostic.classify_d1(perfect) == "mapping_following_supported"
    assert diagnostic.classify_d1({case.record_id: "A" for case in direct}) == "fixed_label_preference_supported"
    order_sensitive = {
        case.record_id: "A" if case.grammar_order == "A_then_B" else "B"
        for case in direct
    }
    assert diagnostic.classify_d1(order_sensitive) == "grammar_order_asymmetry_observed"
    with pytest.raises(diagnostic.LabelSelectionError, match="frozen direct-mapping"):
        diagnostic.classify_d1({})


def test_predeclared_d2_outcome_categories() -> None:
    contiguous = [case for case in _plan() if case.stage == diagnostic.CONTIGUOUS_STAGE]
    perfect = {case.record_id: case.canonical_answer for case in contiguous}
    assert diagnostic.classify_d2(perfect) == "contiguous_mapping_and_relation_supported"
    assert diagnostic.classify_d2({case.record_id: "A" for case in contiguous}) == "fixed_label_preference_recurred"
    assert diagnostic.score(contiguous[0], "A.") == {
        "correct": False,
        "malformed": True,
        "parsed_answer": None,
    }
