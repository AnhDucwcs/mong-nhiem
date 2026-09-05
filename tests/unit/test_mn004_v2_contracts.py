from __future__ import annotations

import copy
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-004-state-representation-intervention" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mn004_v2
import run_mn004_v2


def row(case_id: str, level: int, passed: bool) -> dict:
    return {"case_id": case_id, "requested_input_tokens": level, "evaluation": {"passed": passed}, "validator_status": "valid", "truncated": False, "error": None}


def rows(level: int, passes: int) -> list[dict]:
    definition = mn004_v2.definition()
    return [row(case_id, level, index < passes) for index, case_id in enumerate(definition["workload"]["authorized_case_ids"])]


def test_definition_fingerprint_covers_contract_critical_fields() -> None:
    definition = mn004_v2.definition()
    changed = copy.deepcopy(definition)
    changed["llama_rules"]["primary_delta_minimum"] += 1
    assert mn004_v2.definition_fingerprint(definition) != mn004_v2.definition_fingerprint(changed)


def test_authorized_inventory_is_exactly_2k_and_8k() -> None:
    selected = mn004_v2.authorized_inventory()
    assert len(selected) == 48
    assert {item["requested_input_tokens"] for item in selected} == {2048, 8192}
    assert sum(item["requested_input_tokens"] == 2048 for item in selected) == 24
    assert sum(item["requested_input_tokens"] == 8192 for item in selected) == 24


def test_reproduction_gate_requires_exact_frozen_zero_of_six() -> None:
    frozen = mn004_v2.definition()["workload"]["frozen_reproduction_case_ids"]
    assert mn004_v2.reproduction_verdict([row(case_id, 8192, False) for case_id in frozen]) == "compatible"
    assert mn004_v2.reproduction_verdict([row(case_id, 8192, case_id == frozen[0]) for case_id in frozen]) == "baseline_drift"


def test_llama_primary_and_reference_rules_are_mechanical() -> None:
    untreated = rows(2048, 20) + rows(8192, 2)
    ledger = rows(2048, 18) + rows(8192, 12)
    verdict = mn004_v2.llama_verdict(untreated, ledger)
    assert verdict["primary_verdict"] == "supported_under_bounded_claim"
    assert verdict["verdict"] == "supported_under_bounded_claim"
    regression = mn004_v2.llama_verdict(untreated, rows(2048, 17) + rows(8192, 12))
    assert regression["verdict"] == "llama_reference_regression"


def test_qwen_control_blocks_ledger_until_eligible() -> None:
    assert mn004_v2.qwen_verdict(rows(8192, 19), None)["verdict"] == "control_not_qualified"
    assert mn004_v2.qwen_verdict(rows(8192, 20), None)["verdict"] == "eligible_pending_ledger"
    assert mn004_v2.qwen_verdict(rows(8192, 20), rows(8192, 17))["verdict"] == "qwen_regression"


def test_v2_phase_surface_excludes_16k_and_512() -> None:
    assert run_mn004_v2.phase_spec("llama_untreated")[2] == [2048, 8192]
    assert run_mn004_v2.phase_spec("qwen_8k_untreated")[2] == [8192]
