"""Focused offline contracts for the ECC-007 causal-reasoning baseline."""
from __future__ import annotations

import sys
from pathlib import Path

import jsonschema
import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-003-effective-context-capacity" / "experiments" / "ecc-007-causal-reasoning" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import ecc007


def test_frozen_definition_is_balanced_and_fingerprint_is_stable() -> None:
    definition, cases = ecc007.load_definition()
    assert definition["controls"]["causal_hop_count"] == 2
    assert len(cases) == 8
    assert sum(case["positive"] for case in cases) == 4
    assert ecc007.definition_fingerprint() == ecc007.definition_fingerprint()


def test_positive_and_negative_graphs_have_expected_reachability() -> None:
    positive = ecc007.graph(1, 2, True)
    negative = ecc007.graph(2, 2, False)
    assert ecc007.reachable(positive["edges"], positive["source"], positive["target"])
    assert not ecc007.reachable(negative["edges"], negative["source"], negative["target"])
    assert ecc007.evaluate(positive, " YES.\n") == (True, "yes")
    assert ecc007.evaluate(negative, "yes") == (False, "yes")


def test_distractors_are_unique_and_disconnected() -> None:
    _definition, cases = ecc007.load_definition()
    case = cases[0]
    _context, _content, _prefix, distractors = ecc007.compose(case, 20, 20260828, 10)
    assert len(distractors) == len(set(distractors))
    assert not ecc007.reachable(distractors, case["source"], case["target"])


def test_composition_is_deterministic_with_stable_hash() -> None:
    _definition, cases = ecc007.load_definition()
    first = ecc007.compose(cases[0], 20, 20260828, 10)[1]
    second = ecc007.compose(cases[0], 20, 20260828, 10)[1]
    assert first == second


def test_case_result_schema_rejects_missing_contract_fields() -> None:
    schema = ecc007.load_json(ecc007.ROOT / "schemas" / "case-result.schema.json")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({}, schema)


def test_summary_uses_contiguous_prefix_and_right_censoring() -> None:
    _definition, cases = ecc007.load_definition()
    records = []
    for level, passes in ((512, 8), (2048, 7), (8192, 8), (16384, 4)):
        for index, case in enumerate(cases):
            passed = index < passes
            records.append({"requested_input_tokens": level, "error": None, "truncated": False, "actual_input_tokens": level - 1, "timing": {"total_ms": 1.0}, "evaluation": {"passed": passed}, "failure": None if passed else "incorrect_causal_inference"})
    summary = ecc007.summarize("test", records, [512, 2048, 8192, 16384], [case["id"] for case in cases], True)
    assert summary["ecc"]["metrics"]["ECC95"] == {"tested_level": 512, "status": "resolved"}
    assert summary["non_monotonic"]


def test_load_definition_rejects_reachability_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    original = ecc007.load_json
    cases_path = ecc007.DEFINITION / "cases.json"

    def corrupted(path: Path):
        value = original(path)
        if path == cases_path:
            value["cases"][0]["target"] = "NODE_701_Z"
        return value

    monkeypatch.setattr(ecc007, "load_json", corrupted)
    with pytest.raises(ecc007.ContractError, match="case graph mismatch"):
        ecc007.load_definition()
