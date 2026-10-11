"""Tests for ProactiveAffordanceGate in Stage 3."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from causal_synthesis_engine import CausalSynthesisEngine
from counterfactual_sandbox import CounterfactualSandbox
from microworld_engine import SimulatedMicroworld
from proactive_affordance_gate import ProactiveAffordanceGate


def test_proactive_affordance_filtering():
    engine = CausalSynthesisEngine("orbital_life_support")
    sandbox = CounterfactualSandbox(causal_engine=engine)
    gate = ProactiveAffordanceGate(sandbox=sandbox)

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

    candidates = [
        "divert_solar_power cryo_battery 80.0",  # Trapped!
        "purge_cabin_heat 40.0",                 # Safe
    ]

    viable, pruned, cards = gate.filter_viable_actions(world, candidates)

    assert "purge_cabin_heat 40.0" in viable
    assert "divert_solar_power cryo_battery 80.0" not in viable
    assert "divert_solar_power cryo_battery 80.0" in pruned
    assert gate.proactive_bypasses_count == 1
    assert len(cards) == 1
    assert "CRULE_SOLAR_HEAT_COUPLING" in cards[0]
