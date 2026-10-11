"""Integration tests for DualEngineOrchestrator in Stage 3."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hierarchical_planner import SubGoal
from orchestrator import DualEngineOrchestrator


def test_orchestrator_arm3_proactive_bypass():
    subgoals = [
        SubGoal(
            subgoal_id="G1_COOL",
            description="Cool thermal loop <= 65 C",
            target_entity="thermal_loop",
            target_property="temperature",
            operator="<=",
            target_value=65.0,
            candidate_actions=[
                "divert_solar_power cryo_battery 80.0",  # Trapped!
                "purge_cabin_heat 40.0",                 # Safe
            ],
        )
    ]

    init_entities = {
        "thermal_loop": {"entity_type": "cooling", "properties": {"temperature": 75.0}},
        "cryo_battery": {"entity_type": "battery", "properties": {"charge_kwh": 20.0}},
        "solar_array": {"entity_type": "solar", "properties": {"output_kw": 50.0}},
        "o2_scrubber": {"entity_type": "life_support", "properties": {"o2_pressure": 20.0}},
    }

    orch = DualEngineOrchestrator(
        domain="orbital_life_support",
        initial_entities=init_entities,
        subgoals=subgoals,
        arm="arm3_counterfactual_causal_host",
    )

    # 1. Check active grammar prunes trapped action
    viable, pruned = orch.get_active_viable_actions()
    assert "purge_cabin_heat 40.0" in viable
    assert "divert_solar_power cryo_battery 80.0" in pruned
    assert orch.proactive_bypasses == 1

    # 2. Dispatch safe action
    ok1, msg1, meta1 = orch.execute_turn("ACTION: DISPATCH purge_cabin_heat 40.0")
    assert ok1 is True
    assert orch.world.entities["thermal_loop"].properties["temperature"] <= 68.0

    # 3. Resolve
    orch.planner.subgoals[0].is_completed = True
    orch.planner.active_index = 1
    ok2, msg2, meta2 = orch.execute_turn("ACTION: RESOLVE COMPLETE")
    assert ok2 is True

    summary = orch.finalize()
    assert summary["is_success"] is True
    assert summary["committed_violations"] == 0
    assert summary["proactive_bypasses"] >= 1


def test_orchestrator_arm2_reactive_trap_hit():
    subgoals = [
        SubGoal(
            subgoal_id="G1_COOL",
            description="Cool thermal loop <= 65 C",
            target_entity="thermal_loop",
            target_property="temperature",
            operator="<=",
            target_value=65.0,
            candidate_actions=[
                "divert_solar_power cryo_battery 80.0",  # Trapped!
                "purge_cabin_heat 40.0",                 # Safe
            ],
        )
    ]

    init_entities = {
        "thermal_loop": {"entity_type": "cooling", "properties": {"temperature": 75.0}},
        "cryo_battery": {"entity_type": "battery", "properties": {"charge_kwh": 20.0}},
        "solar_array": {"entity_type": "solar", "properties": {"output_kw": 50.0}},
        "o2_scrubber": {"entity_type": "life_support", "properties": {"o2_pressure": 20.0}},
    }

    orch = DualEngineOrchestrator(
        domain="orbital_life_support",
        initial_entities=init_entities,
        subgoals=subgoals,
        arm="arm2_reactive_control",
    )

    # In Arm 2, trapped action is NOT proactively pruned
    viable, pruned = orch.get_active_viable_actions()
    assert "divert_solar_power cryo_battery 80.0" in viable

    # Arm 2 dispatches trapped action: hits trap and triggers rollback
    ok, msg, meta = orch.execute_turn("ACTION: DISPATCH divert_solar_power cryo_battery 80.0")
    assert ok is False
    assert "BREACH" in msg
    assert orch.reactive_traps_hit == 1
    assert "divert_solar_power cryo_battery 80.0" in orch.banned_actions
