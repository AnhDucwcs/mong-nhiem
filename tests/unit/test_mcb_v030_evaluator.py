from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[2] / "research" / "experiments" / "baselines" / "mn-002-model-qualification" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import mcb_v030


def _case(values: list[str]) -> dict:
    return {"evaluation": {"method": "accepted_values"}, "expected": {"value": values[0], "accepted_values": values}}


def test_explicit_aliases_allow_only_declared_surface_forms() -> None:
    case = _case(["box Blue", "Blue"])
    assert mcb_v030.evaluate(case, "Blue.")[0]
    assert not mcb_v030.evaluate(case, "box Red")[0]
    assert not mcb_v030.evaluate(case, "Blue, not Red")[0]


def test_causal_boolean_and_entity_aliases_remain_conservative() -> None:
    assert mcb_v030.evaluate(_case(["the guard", "guard"]), "guard")[0]
    assert not mcb_v030.evaluate(_case(["the guard", "guard"]), "sensor")[0]
    assert mcb_v030.evaluate(_case(["no"]), "No.")[0]
    assert not mcb_v030.evaluate(_case(["no"]), "yes")[0]
