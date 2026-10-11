"""Integration tests for DualEngineOrchestrator under parametric drift."""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hierarchical_planner import HierarchicalPlanner, SubGoal
from microworld_engine import ParametricDriftRule, SimulatedMicroworld, WorldEntity
from orchestrator import DualEngineOrchestrator


def create_test_orbital_world():
    entities = {
        "solar_array": WorldEntity("solar_array", "solar_panel", properties={"output_kw": 50.0}),
        "cryo_battery": WorldEntity("cryo_battery", "battery", properties={"charge_kwh": 10.0}),
        "thermal_loop": WorldEntity("thermal_loop", "cooling", properties={"temperature": 65.0}),
        "o2_scrubber": WorldEntity("o2_scrubber", "life_support", properties={"o2_pressure": 20.0}),
    }
    drift = [
        ParametricDriftRule(
            target_entity_id="thermal_loop",
            property_name="coolant_flow",
            drift_type="linear_decay",
            rate=0.08,
            start_tick=2,
        )
    ]
    world = SimulatedMicroworld(
        domain="orbital_life_support",
        initial_entities=entities,
        drift_rules=drift,
    )
    subgoals = [
        SubGoal(
            subgoal_id="G1_CHARGE",
            description="Charge cryo battery to >= 12.0 kWh",
            target_entity="cryo_battery",
            target_property="charge_kwh",
            operator=">=",
            target_value=12.0,
            candidate_actions=["divert_solar_power cryo_battery 60.0"],
        ),
        SubGoal(
            subgoal_id="G2_COOL",
            description="Cool thermal loop to <= 60.0 C",
            target_entity="thermal_loop",
            target_property="temperature",
            operator="<=",
            target_value=60.0,
            candidate_actions=["purge_cabin_heat 40.0"],
        ),
    ]
    planner = HierarchicalPlanner(subgoals)
    return world, planner


def test_orchestrator_arm3_adaptation_and_rollback():
    world, planner = create_test_orbital_world()
    orch = DualEngineOrchestrator(world=world, planner=planner, arm="arm3_dynamic_host")

    # Turn 1: Charge battery
    ok, msg, _ = orch.execute_turn("ACTION: DISPATCH divert_solar_power cryo_battery 60.0")
    assert ok is True
    assert planner.subgoals[0].is_completed is True

    # Turn 2: Attempt high purge under thermal drift
    # As coolant flow drifts, purge_cabin_heat 40.0 would breach conservation!
    # In Arm 3, GBNF compiler with monitor injects engage_auxiliary_cryo_pump
    orch.compile_turn_grammar()
    ok, msg, _ = orch.execute_turn("ACTION: DISPATCH engage_auxiliary_cryo_pump")
    assert ok is True
    assert planner.subgoals[1].is_completed is True

    # Turn 3: Resolve
    ok, msg, _ = orch.execute_turn("ACTION: RESOLVE COMPLETE")
    assert ok is True
    assert msg == "TASK_RESOLVED_SUCCESSFULLY"

    metrics = orch.finalize()
    assert metrics["is_success"] is True
    assert metrics["committed_conservation_breaches"] == 0
    assert metrics["max_prompt_tokens"] <= 512
