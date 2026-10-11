"""Tests for CounterfactualSandbox in Stage 3."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from causal_synthesis_engine import CausalSynthesisEngine
from counterfactual_sandbox import CounterfactualSandbox
from microworld_engine import SimulatedMicroworld


def test_sandbox_isolated_evaluation():
    engine = CausalSynthesisEngine("orbital_life_support")
    sandbox = CounterfactualSandbox(causal_engine=engine)

    init_entities = {
        "thermal_loop": {
            "entity_type": "cooling",
            "properties": {"temperature": 75.0},
        },
        "cryo_battery": {
            "entity_type": "battery",
            "properties": {"charge_kwh": 20.0},
        },
        "solar_array": {
            "entity_type": "solar",
            "properties": {"output_kw": 50.0},
        },
        "o2_scrubber": {
            "entity_type": "life_support",
            "properties": {"o2_pressure": 20.0},
        },
    }

    world = SimulatedMicroworld(
        domain="orbital_life_support",
        initial_entities=init_entities,
    )

    # 1. Action that triggers causal trap (divert when temp > 70 C)
    res_danger = sandbox.evaluate_hypothetical_action(world, "divert_solar_power cryo_battery 80.0")
    assert res_danger.is_viable is False
    assert "CAUSAL_TRAP_ANTICIPATED" in res_danger.breach_reason

    # Verify primary world state was NOT mutated
    assert world.entities["thermal_loop"].properties["temperature"] == 75.0
    assert world.entities["o2_scrubber"].properties["o2_pressure"] == 20.0

    # 2. Action that is safe (purge cabin heat)
    res_safe = sandbox.evaluate_hypothetical_action(world, "purge_cabin_heat 40.0")
    assert res_safe.is_viable is True
    assert res_safe.breach_reason is None

    # Primary world state still unmutated
    assert world.entities["thermal_loop"].properties["temperature"] == 75.0
