from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "experiments" / "prototypes" / "mn-005-state-tracking-intervention-selection" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import mn005


def test_frozen_authority_and_case_selection() -> None:
    definition, cases, _ecc = mn005.load_definition()
    assert definition["workload"]["case_ids"] == list(mn005.CASE_IDS)
    assert [case["id"] for case in cases] == list(mn005.CASE_IDS)


def test_frozen_prompt_and_literal_transport() -> None:
    source = {"context": "Context event log:\nState update: Unit Test 1 changed to RED.", "arm_a": "Context event log:\nState update: Unit Test 1 changed to RED.\n\nQuestion:\nWhat is the current state of Unit Test 1? Return only the state."}
    artifact = b"entity=Unit Test 1 | state=RED"
    content, slot, _rendered = mn005.stage_b_prompt(source, {"entity": "Unit Test 1"}, artifact)
    assert slot == artifact
    assert "<artifact>\nentity=Unit Test 1 | state=RED\n</artifact>" in content
    assert mn005.stage_a_prompt(source, "B").endswith(mn005.CONTROL_INSTRUCTION)
    assert "Do not include an ordinal, current, latest, final" in mn005.stage_a_prompt(source, "C")


def test_evaluator_and_reconstruction_diagnostic() -> None:
    case = {"entity": "Unit Test 1", "updates": ["RED", "BLUE", "AMBER", "GREEN"], "answer": "GREEN"}
    assert mn005.final_evaluation(case, "GREEN", "stop")["passed"]
    assert not mn005.final_evaluation(case, "BLUE", "stop")["passed"]
    artifact = "\n".join([f"entity=Unit Test 1 | state={state}" for state in case["updates"]]).encode()
    diagnostic = mn005.reconstruction_diagnostic(case, artifact, "stop")
    assert diagnostic["full_exact_reconstruction"]
    assert diagnostic["source_order_correct"]


def test_support_taxonomy() -> None:
    definition, _cases, _ecc = mn005.load_definition()
    arm_a = [{"protocol_valid": True, "infrastructure_status": "complete", "evaluation": {"passed": False}} for _ in range(6)]
    pairs = []
    for _index in range(6):
        pairs.append({"case_id": f"case-{_index}", "B": {"protocol_valid": True, "infrastructure_status": "complete", "evaluation": {"passed": False}}, "C": {"protocol_valid": True, "infrastructure_status": "complete", "evaluation": {"passed": True}, "stage_a_diagnostic": {"full_exact_reconstruction": True, "prohibited_fields": [], "non_target_insertions": []}}})
    assert mn005.classify(arm_a, pairs, definition)["classification"] == "supported"
    arm_a[0]["evaluation"]["passed"] = True
    assert mn005.classify(arm_a, pairs, definition)["classification"] == "inconclusive"


def test_attempt_identity_and_first_valid_policy(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(mn005, "RUNS", tmp_path)
    assert mn005.next_attempt_id() == "attempt-0001"
    invalid = tmp_path / "attempt-0001"; invalid.mkdir()
    (invalid / "summary.json").write_text('{"attempt_status":"experiment_invalid"}\n', encoding="utf-8")
    assert mn005.next_attempt_id() == "attempt-0002"
    assert not mn005.has_canonical_attempt()
    canonical = tmp_path / "attempt-0002"; canonical.mkdir()
    (canonical / "summary.json").write_text('{"attempt_status":"canonical_valid"}\n', encoding="utf-8")
    assert mn005.has_canonical_attempt()
