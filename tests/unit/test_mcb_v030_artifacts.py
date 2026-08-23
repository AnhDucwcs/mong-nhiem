from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "baselines" / "mn-002-model-qualification" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mcb_v030


def test_definition_fingerprint_is_stable_for_frozen_files() -> None:
    assert mcb_v030.definition_fingerprint() == "2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a"


def test_structured_output_requires_exact_object_contract() -> None:
    case = next(case for case in mcb_v030.load_cases() if case["suite"] == "structured_output")
    valid = json.dumps({key: value["const"] for key, value in case["expected"]["schema"]["properties"].items()})
    assert mcb_v030.evaluate(case, valid)[0]
    assert not mcb_v030.evaluate(case, valid[:-1] + ', "extra": true}')[0]
