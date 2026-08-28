"""Focused offline contracts for the fresh Qwen ECC-005 confirmation."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-003-effective-context-capacity" / "experiments" / "ecc-005-qwen-position-confirmation" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import ecc005


def test_frozen_definition_has_30_fresh_cases_and_stable_fingerprint() -> None:
    definition, cases = ecc005.load_definition()
    assert len(cases) == 30
    assert ecc005.definition_fingerprint() == ecc005.definition_fingerprint()
    assert [item["id"] for item in ecc005.positions(definition)] == ["early", "late"]


def test_diagnostic_tracks_numeric_suffix_only_failure() -> None:
    definition, cases = ecc005.load_definition()
    failure = ecc005.classify_failure(cases[0], cases[0]["answer"].split("-")[1], 10, "late", definition)
    assert failure["kind"] == "partial_or_malformed_code"


def test_complete_summary_classifies_directional_endpoint() -> None:
    definition, cases = ecc005.load_definition()
    records = []
    for level in (8192, 16384):
        for position in ("early", "late"):
            for index, case in enumerate(cases):
                passed = not (level == 16384 and position == "late" and index < 5)
                records.append({"case_id": case["id"], "requested_input_tokens": level,
                                "requested_evidence_position": position, "error": None, "truncated": False,
                                "actual_input_tokens": level - 1, "timing": {"total_ms": 1.0},
                                "evaluation": {"passed": passed}, "failure": None if passed else {"kind": "other_text"},
                                "output": {"raw_text": case["answer"] if passed else "wrong"},
                                "expected_answer": case["answer"]})
    summary = ecc005.summarize("test", records, [8192, 16384], ["early", "late"], [case["id"] for case in cases], True, definition)
    assert summary["interpretation"]["status"] == "position_sensitivity_observed"
    assert summary["paired_transitions"][1]["early_vs_late"]["early_pass_late_fail"] == 5


def test_rejects_historical_target_overlap(monkeypatch: pytest.MonkeyPatch) -> None:
    original = ecc005.load_json
    cases_path = ecc005.DEFINITION / "cases.json"

    historical_entity = ecc005.ecc004.load_json(ecc005.ecc004.DEFINITION / "cases.json")["cases"][0]["entity"]

    def overlap(path: Path):
        value = original(path)
        if path == cases_path:
            value["cases"][0]["entity"] = historical_entity
        return value

    monkeypatch.setattr(ecc005, "load_json", overlap)
    with pytest.raises(ecc005.ContractError, match="overlap"):
        ecc005.load_definition()
