from __future__ import annotations

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

import run_mn006_baseline as baseline
import run_mn006_label_selection_d1 as runner
from mn006 import label_selection as diagnostic
from mn006 import label_selection_execution as execution
from mn006.measurement import validate_attempt_directory

RUNS = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration" / "runs"


def _cases() -> tuple[diagnostic.DiagnosticCase, ...]:
    return execution.build_d1_request_plan()


def test_d1_identity_runtime_and_plan_hash_are_frozen() -> None:
    assert execution.D1_RUN_ID == "label-selection-d1-run-0001"
    assert execution.EXPECTED_DIAGNOSTIC_PLAN_SHA256 == diagnostic.plan_fingerprint()
    assert execution.EXPECTED_D1_REQUEST_COUNT == 16
    assert execution.D1_REQUEST_PARAMETERS == {
        "chat_template_kwargs": {},
        "max_tokens": 16,
        "seed": 42,
        "temperature": 0.0,
    }
    assert execution.D1_REQUEST_PARAMETERS["max_tokens"] == baseline.INFERENCE["output_tokens"]
    assert baseline.INFERENCE["configured_context_size"] == 16896
    assert baseline.INFERENCE["threads"] == 12
    assert baseline.INFERENCE["batch_size"] == 2048
    assert baseline.INFERENCE["parallel_slots"] == 1
    assert baseline.INFERENCE["prompt_cache"] is False
    assert execution.D1_REQUEST_PARAMETERS["temperature"] == baseline.INFERENCE["temperature"]
    assert execution.D1_REQUEST_PARAMETERS["seed"] == baseline.INFERENCE["seed"]


def test_exact_d1_matrix_and_source_composition() -> None:
    cases = _cases()
    assert len(cases) == 16
    assert [case.request_ordinal for case in cases] == list(range(1, 17))
    assert tuple(sorted({case.source_ordinal for case in cases})) == (0, 1, 2, 3)
    source_relations = {
        ordinal: {case.equal_state for case in cases if case.source_ordinal == ordinal}
        for ordinal in (0, 1, 2, 3)
    }
    assert sum(next(iter(values)) for values in source_relations.values()) == 2
    for ordinal in (0, 1, 2, 3):
        source_cases = [case for case in cases if case.source_ordinal == ordinal]
        assert len(source_cases) == 4
        assert {case.mapping.identifier for case in source_cases} == {"M1_equal_A", "M2_equal_B"}
        assert {case.grammar_order for case in source_cases} == {"A_then_B", "B_then_A"}


def test_grammar_variants_are_exact_and_language_equivalent() -> None:
    assert diagnostic.GRAMMAR_AB == 'root ::= "A" | "B"\n'
    assert diagnostic.GRAMMAR_BA == 'root ::= "B" | "A"\n'
    assert execution.grammar_language(diagnostic.GRAMMAR_AB) == frozenset({"A", "B"})
    assert execution.grammar_language(diagnostic.GRAMMAR_BA) == frozenset({"A", "B"})
    assert diagnostic.GRAMMAR_AB.endswith("\n") and diagnostic.GRAMMAR_AB.count("\n") == 1
    assert diagnostic.GRAMMAR_BA.endswith("\n") and diagnostic.GRAMMAR_BA.count("\n") == 1


def test_payloads_are_direct_state_only_and_preserve_mapping_and_grammar() -> None:
    for case in _cases():
        entry = execution.plan_entry(case)
        payload = execution.build_request_payload(case)
        prompt = payload["messages"][0]["content"]
        assert payload["grammar"] == case.grammar
        assert payload["temperature"] == 0.0
        assert set(payload) == {"chat_template_kwargs", "grammar", "max_tokens", "messages", "seed", "temperature"}
        assert payload["chat_template_kwargs"] == {}
        assert payload["seed"] == 42
        assert payload["max_tokens"] == 16
        assert prompt == entry["public_prompt"]
        assert prompt.startswith("The final query states are:\n")
        assert "All entities begin" not in prompt
        assert "source_events" not in prompt
        assert "canonical_answer" not in prompt
        assert "VALID" not in prompt and "INVALID" not in prompt
        assert execution.grammar_language(payload["grammar"]) == frozenset({"A", "B"})
        assert "equal states ->" in prompt and "unequal states ->" in prompt


def test_mapping_reversal_and_grammar_independent_answer() -> None:
    cases = _cases()
    for ordinal in (0, 1, 2, 3):
        source_cases = [case for case in cases if case.source_ordinal == ordinal]
        m1 = [case for case in source_cases if case.mapping.identifier == "M1_equal_A"]
        m2 = [case for case in source_cases if case.mapping.identifier == "M2_equal_B"]
        assert {case.canonical_answer for case in m1} in ({"A"}, {"B"})
        assert {case.canonical_answer for case in m2} in ({"A"}, {"B"})
        assert m1[0].canonical_answer != m2[0].canonical_answer
        for mapping_cases in (m1, m2):
            assert len({case.canonical_answer for case in mapping_cases}) == 1
            assert {case.grammar_order for case in mapping_cases} == {"A_then_B", "B_then_A"}


def test_strict_parser_and_evaluator() -> None:
    case = _cases()[0]
    assert diagnostic.parse_label(" A \n") == "A"
    for value in ("a", "b", "A.", "B.", "Answer: A", "A B", "VALID"):
        assert diagnostic.parse_label(value) is None
    assert execution.evaluate_raw_output(case, case.canonical_answer)["correct"] is True
    assert execution.evaluate_raw_output(case, "A.")["malformed"] is True


def test_exact_classification_precedence_and_fixtures() -> None:
    cases = _cases()
    perfect = {case.record_id: case.canonical_answer for case in cases}
    assert diagnostic.classify_d1(perfect) == "mapping_following_supported"
    assert diagnostic.classify_d1({case.record_id: "A" for case in cases}) == "fixed_label_preference_supported"
    order_sensitive = {
        case.record_id: "A" if case.grammar_order == "A_then_B" else "B"
        for case in cases
    }
    assert diagnostic.classify_d1(order_sensitive) == "grammar_order_asymmetry_observed"
    mixed_but_pair_stable = {
        case.record_id: ("A" if case.source_ordinal % 2 == 0 else "B")
        for case in cases
    }
    assert diagnostic.classify_d1(mixed_but_pair_stable) == "mapping_diagnostic_inconclusive"
    malformed = dict(perfect)
    malformed[cases[0].record_id] = "A."
    assert diagnostic.classify_d1(malformed) == "direct_mapping_malformed_or_inconclusive"


def test_grammar_order_pairs_exist_exactly_once() -> None:
    cases = _cases()
    pairs = {}
    for case in cases:
        pairs.setdefault((case.source_ordinal, case.mapping.identifier), []).append(case)
    assert len(pairs) == 8
    for pair in pairs.values():
        assert len(pair) == 2
        assert {case.grammar_order for case in pair} == {"A_then_B", "B_then_A"}


def test_dry_construction_is_d1_only_and_creates_no_evidence() -> None:
    assert not (RUNS / execution.D1_RUN_ID).exists()
    entries = runner.dry_construction()
    assert len(entries) == 16
    assert {entry["stage"] for entry in entries} == {diagnostic.DIRECT_STAGE}
    assert all(entry["record_id"].startswith("d1-") for entry in entries)
    assert not (RUNS / execution.D1_RUN_ID).exists()
    d2_case = next(case for case in diagnostic.build_plan() if case.stage == diagnostic.CONTIGUOUS_STAGE)
    assert "classify_d2" not in Path(runner.__file__).read_text(encoding="utf-8")
    with pytest.raises(execution.D1ExecutionError, match="D2"):
        execution.build_request_payload(d2_case)


def test_contract_metadata_is_diagnostic_not_attempt_0003() -> None:
    metadata = runner.contract_metadata("executor-commit")
    assert metadata["run_id"] == execution.D1_RUN_ID
    assert metadata["d1_stage"] == diagnostic.DIRECT_STAGE
    assert metadata["diagnostic_plan_sha256"] == execution.EXPECTED_DIAGNOSTIC_PLAN_SHA256
    assert "attempt-0003" not in str(metadata)
    assert not (RUNS / "attempt-0003").exists()


def test_frozen_baseline_attempts_remain_valid() -> None:
    assert validate_attempt_directory(RUNS / "attempt-0001", attempt_id="attempt-0001")["outcome"] == "protocol_valid"
    assert validate_attempt_directory(RUNS / "attempt-0002", attempt_id="attempt-0002")["outcome"] == "protocol_valid"
