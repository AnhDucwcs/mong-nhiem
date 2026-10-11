"""Integration tests for DualEngineOrchestrator under Dynamic Schema Evolution."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hierarchical_planner import SubGoal
from orchestrator import DualEngineOrchestrator
from schema_evolution_engine import SchemaEvolutionRule


def test_arm3_emergent_entity_action_success():
    # Rule: aux_cooler emerges at tick 1
    rule = SchemaEvolutionRule(
        rule_id="EMERGE_COOLER",
        lifecycle_action="EMERGE",
        target_entity_id="aux_cooler",
        trigger_type="tick",
        trigger_tick=1,
        payload={
            "entity_type": "cooler",
            "properties": {"cooling_kw": 30.0},
            "relations": {"cools": "thermal_loop"},
        },
    )

    # Subgoals: G1 requires thermal_loop temp <= 60.0, candidate actions include activate_secondary_cooler
    subgoals = [
        SubGoal(
            subgoal_id="G1_COOL",
            description="Cool thermal loop below 65 C",
            target_entity="thermal_loop",
            target_property="temperature",
            operator="<=",
            target_value=65.0,
            candidate_actions=["purge_cabin_heat 40.0"],  # will expand to include activate_secondary_cooler
        )
    ]

    orch = DualEngineOrchestrator(
        domain="orbital_life_support",
        initial_entities={
            "thermal_loop": {"entity_type": "cooling", "properties": {"temperature": 75.0}},
            "cryo_battery": {"entity_type": "battery", "properties": {"charge_kwh": 20.0}},
        },
        subgoals=subgoals,
        schema_rules=[rule],
        arm="arm3_dynamic_schema_host",
    )

    # Turn 1: Advance simulation with purge_cabin_heat, triggering tick and emergence of aux_cooler
    ok1, msg1, meta1 = orch.execute_turn("ACTION: DISPATCH purge_cabin_heat 40.0")
    assert ok1 is True
    assert "aux_cooler" in orch.world.entities

    # Turn 2: Dispatch action on emergent entity
    ok2, msg2, meta2 = orch.execute_turn("ACTION: DISPATCH activate_secondary_cooler")
    assert ok2 is True
    assert orch.world.entities["thermal_loop"].properties["temperature"] <= 65.0

    # Turn 3: Resolve
    ok3, msg3, meta3 = orch.execute_turn("ACTION: RESOLVE COMPLETE")
    assert ok3 is True

    summary = orch.finalize()
    assert summary["is_success"] is True
    assert summary["committed_schema_violations"] == 0
    assert "aux_cooler" in summary["emerged_entities"]


def test_schema_invariant_guard_intercepts_unemerged_entity():
    # Attempting to dispatch action on non-existent entity
    orch = DualEngineOrchestrator(
        domain="orbital_life_support",
        initial_entities={
            "thermal_loop": {"entity_type": "cooling", "properties": {"temperature": 75.0}},
        },
        subgoals=[SubGoal("G1", "Test", "thermal_loop", "temperature", "<=", 60.0, [])],
        schema_rules=[],
        arm="arm3_dynamic_schema_host",
    )

    # Dispatch action targeting aux_cooler before it emerges
    ok, msg, meta = orch.execute_turn("ACTION: DISPATCH activate_secondary_cooler")
    assert ok is False
    assert "SCHEMA_VIOLATION" in msg
    assert orch.committed_schema_violations == 1
    assert "activate_secondary_cooler" in orch.banned_actions


def test_simulate_counterfactual_step():
    orch = DualEngineOrchestrator(
        domain="smart_microgrid",
        initial_entities={
            "critical_bus": {"entity_type": "substation", "properties": {"voltage": 380.0}},
            "battery_bank": {"entity_type": "storage", "properties": {"soc": 80.0}},
        },
        subgoals=[],
    )

    # Perform counterfactual simulation
    ok, err, result = orch.world.simulate_counterfactual_step("discharge_battery 30.0")
    assert ok is True

    # Live state was NOT altered!
    assert orch.world.entities["battery_bank"].properties["soc"] == 80.0
    # But counterfactual result reflected change
    assert result["battery_bank"]["soc"] == 56.0
