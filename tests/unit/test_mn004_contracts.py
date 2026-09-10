from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-004-state-representation-intervention" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import mn004


def test_frozen_authority_and_evaluator_diagnostics() -> None:
    definition = mn004.validate_definition()
    assert definition["authority"]["ecc006_definition_fingerprint"] == "37f2dc1cc4cdfbf4a667c54f159bbd5203918f85f4d39001fa62ffcba379ac2e"
    mn004.validate_evaluator_fixtures()
    assert mn004.validate_frozen_failure_diagnostics() == 21


def test_definition_fingerprint_changes_with_critical_field() -> None:
    definition = mn004.validate_definition()
    changed = copy.deepcopy(definition)
    changed["llama_rules"]["aggregate_delta_minimum"] += 1
    assert mn004.definition_fingerprint(changed) != mn004.definition_fingerprint(definition)


def test_renderers_are_exact_semantic_pair() -> None:
    definition = mn004.validate_definition()
    case = {"id": "fixture", "entity": "Unit Fixture 1", "updates": ["RED", "BLUE", "GREEN", "AMBER"], "answer": "AMBER"}
    events = [
        {"entity": "Unit Drift 1", "state": "BLACK"},
        *[{"entity": case["entity"], "state": state} for state in case["updates"]],
        {"entity": "Unit Drift 2", "state": "WHITE"},
    ]
    natural = mn004.render_natural(events, case["entity"], definition)
    ledger = mn004.render_ledger(events, case["entity"], definition)
    mn004.validate_pair(case, events, natural, ledger, definition)
    assert mn004.parse_natural(natural, case["entity"], definition) == events
    assert mn004.parse_ledger(ledger, case["entity"], definition) == events


def test_ledger_parser_rejects_reordered_or_marked_source() -> None:
    definition = mn004.validate_definition()
    prompt = "Chronological state-transition ledger:\nevent=1 | entity=Unit X | new_state=RED\nevent=3 | entity=Unit X | new_state=BLUE\n\nQuestion:\nWhat is the current state of Unit X? Return only the state."
    with pytest.raises(mn004.ContractError, match="ledger"):
        mn004.parse_ledger(prompt, "Unit X", definition)


def test_fresh_case_rule_is_frozen() -> None:
    definition = mn004.validate_definition()
    cases = mn004.fresh_cases(definition)
    assert [case["id"] for case in cases] == definition["workload"]["fresh_case_ids"]
    assert cases[0]["entity"] == "Unit Ledger 9201"
    assert cases[0]["updates"] == ["RED", "BLUE", "AMBER", "GREEN"]
