"""Unit tests for Dynamic Affordance Compiler (Grammar Expansion & Pruning)."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from dynamic_affordance import DynamicAffordanceCompiler


def test_grammar_expansion_on_emergent_entity():
    # Base candidates
    base_actions = ["divert_solar_power cryo_battery 60.0", "purge_cabin_heat 40.0"]

    # When aux_cooler is not active: action 'activate_secondary_cooler' is NOT present
    g_before = DynamicAffordanceCompiler.compile_grammar(
        allowed_actions=base_actions,
        known_entity_ids=["solar_array", "thermal_loop"],
        active_entities={"solar_array", "thermal_loop"},
    )
    assert "activate_secondary_cooler" not in g_before

    # When aux_cooler emerges and is active: grammar expands to admit 'activate_secondary_cooler'
    g_after = DynamicAffordanceCompiler.compile_grammar(
        allowed_actions=base_actions,
        known_entity_ids=["solar_array", "thermal_loop", "aux_cooler"],
        active_entities={"solar_array", "thermal_loop", "aux_cooler"},
    )
    assert "activate_secondary_cooler" in g_after


def test_grammar_pruning_on_retired_entity():
    # Base candidate targeting aux_cooler
    base_actions = ["activate_secondary_cooler", "purge_cabin_heat 40.0"]

    # When aux_cooler decommissions/retires: action is PRUNED
    g_retired = DynamicAffordanceCompiler.compile_grammar(
        allowed_actions=base_actions,
        known_entity_ids=["solar_array", "thermal_loop", "aux_cooler"],
        active_entities={"solar_array", "thermal_loop"},  # aux_cooler missing from active
    )
    assert "activate_secondary_cooler" not in g_retired
    assert "purge_cabin_heat 40.0" in g_retired
