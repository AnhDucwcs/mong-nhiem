"""Unit tests for Dynamic Schema Evolution Engine."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from microworld_engine import SimulatedMicroworld, WorldEntity
from schema_evolution_engine import SchemaEvolutionEngine, SchemaEvolutionRule


def test_entity_emergence_on_tick():
    rule = SchemaEvolutionRule(
        rule_id="EMERGE_AUX_COOLER",
        lifecycle_action="EMERGE",
        target_entity_id="aux_cooler",
        trigger_type="tick",
        trigger_tick=2,
        payload={
            "entity_type": "cooler",
            "properties": {"cooling_kw": 30.0},
            "relations": {"cools": "thermal_loop"},
            "ttl": 10,
        },
    )
    world = SimulatedMicroworld(
        domain="orbital_life_support",
        initial_entities={
            "thermal_loop": {"entity_type": "cooling", "properties": {"temperature": 75.0}},
        },
        schema_rules=[rule],
    )

    assert "aux_cooler" not in world.entities

    # Tick 1: rule not triggered
    world.tick_simulation(elapsed_ticks=1)
    assert "aux_cooler" not in world.entities

    # Tick 2: rule triggers
    events = world.tick_simulation(elapsed_ticks=1)
    assert "aux_cooler" in world.entities
    assert world.entities["aux_cooler"].is_active is True
    assert world.entities["aux_cooler"].properties["cooling_kw"] == 30.0
    assert world.entities["aux_cooler"].relations["cools"] == "thermal_loop"
    assert len(events) == 1
    assert events[0]["type"] == "SCHEMA_EMERGE"


def test_schema_mutation_properties_and_relations():
    rule = SchemaEvolutionRule(
        rule_id="MUTATE_BUS",
        lifecycle_action="MUTATE_SCHEMA",
        target_entity_id="critical_bus",
        trigger_type="tick",
        trigger_tick=1,
        payload={
            "properties": {"harmonic_thd": 0.08},
            "relations": {"coupled_to": "secondary_feeder"},
        },
    )
    world = SimulatedMicroworld(
        domain="smart_microgrid",
        initial_entities={
            "critical_bus": {"entity_type": "substation", "properties": {"voltage": 380.0}},
        },
        schema_rules=[rule],
    )

    world.tick_simulation(elapsed_ticks=1)
    bus = world.entities["critical_bus"]
    assert bus.properties["harmonic_thd"] == 0.08
    assert bus.relations["coupled_to"] == "secondary_feeder"
    assert bus.version == 2


def test_entity_retirement_and_ttl_expiration():
    world = SimulatedMicroworld(
        domain="orbital_life_support",
        initial_entities={
            "temp_sensor": {"entity_type": "sensor", "properties": {"bias": 1.0}, "ttl": 2},
        },
    )
    assert world.entities["temp_sensor"].is_active is True

    # Tick 1: ttl becomes 1
    world.tick_simulation(elapsed_ticks=1)
    assert world.entities["temp_sensor"].ttl == 1
    assert world.entities["temp_sensor"].is_active is True

    # Tick 2: ttl becomes 0 -> retired
    world.tick_simulation(elapsed_ticks=1)
    assert world.entities["temp_sensor"].ttl == 0
    assert world.entities["temp_sensor"].is_active is False
