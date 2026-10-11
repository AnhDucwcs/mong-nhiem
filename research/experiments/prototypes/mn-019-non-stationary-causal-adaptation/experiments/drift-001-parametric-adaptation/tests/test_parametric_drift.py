"""Unit tests for parametric drift calculations in microworld engine."""
import pytest
import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from microworld_engine import ParametricDriftRule, SimulatedMicroworld, WorldEntity


def test_linear_decay_drift():
    rule = ParametricDriftRule(
        target_entity_id="solar_array",
        property_name="efficiency",
        drift_type="linear_decay",
        rate=0.05,
        start_tick=10,
        floor_value=0.2,
    )
    # Before start_tick: multiplier = 1.0
    assert rule.compute_multiplier(5) == 1.0
    assert rule.compute_multiplier(10) == 1.0

    # At tick 15 (elapsed = 5): 1.0 - (0.05 * 5) = 0.75
    assert pytest.approx(rule.compute_multiplier(15), 0.01) == 0.75

    # At tick 30 (elapsed = 20): 1.0 - (0.05 * 20) = 0.0 -> hit floor 0.2
    assert rule.compute_multiplier(30) == 0.2


def test_exponential_decay_drift():
    rule = ParametricDriftRule(
        target_entity_id="battery_bank",
        property_name="internal_resistance",
        drift_type="exponential_decay",
        rate=0.1,
        start_tick=0,
    )
    # At tick 0: e^0 = 1.0
    assert rule.compute_multiplier(0) == 1.0
    # At tick 10: e^-1.0 ~= 0.3678
    assert pytest.approx(rule.compute_multiplier(10), 0.01) == 0.368


def test_step_shock_drift():
    rule = ParametricDriftRule(
        target_entity_id="thermal_loop",
        property_name="coolant_flow",
        drift_type="step_shock",
        rate=0.4,
        start_tick=20,
    )
    assert rule.compute_multiplier(19) == 1.0
    assert rule.compute_multiplier(20) == 0.4
    assert rule.compute_multiplier(50) == 0.4


def test_coupled_cross_channel_drift():
    rule = ParametricDriftRule(
        target_entity_id="solar_array",
        property_name="efficiency",
        drift_type="step_shock",
        rate=0.5,
        start_tick=5,
        coupled_entities=["cryo_battery"],
    )
    entities = {
        "solar_array": WorldEntity("solar_array", "solar_panel", properties={"output_kw": 50.0}),
        "cryo_battery": WorldEntity("cryo_battery", "battery", properties={"charge_kwh": 20.0}),
    }
    world = SimulatedMicroworld(
        domain="orbital_life_support",
        initial_entities=entities,
        drift_rules=[rule],
    )
    world.current_tick = 10

    # Solar array gets full 0.5 degradation
    assert world.get_drift_multiplier("solar_array", "efficiency") == 0.5
    # Coupled cryo_battery gets 50% coupled severity: 1.0 - (0.5 * 0.5) = 0.75
    assert world.get_drift_multiplier("cryo_battery", "charge_kwh") == 0.75
