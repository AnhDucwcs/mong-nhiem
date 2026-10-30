"""Unit Tests for Mộng Nhiễm Living World Declarative Schema Integration.

Verifies schema compilation, continuous state evolution, action verb grammar,
and redline invariant safety triggers.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path

from mong_nhiem.kernel import MongNhiemKernel
from mong_nhiem.schema import DeclarativeSchemaLoader


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "demo" / "schema" / "living_world.json"


def test_living_world_schema_compilation() -> None:
    """Verifies that demo/schema/living_world.json compiles cleanly into CompiledWorldSchema."""
    assert SCHEMA_PATH.exists(), f"Schema file not found at {SCHEMA_PATH}"
    schema = DeclarativeSchemaLoader.load_from_file(str(SCHEMA_PATH))

    assert schema.schema_name == "mong_nhiem_living_world"
    expected_verbs = {"MOVE_TO", "FORAGE_BERRY", "DRINK_WATER", "SHELTER_BURROW", "REST_COLONY"}
    compiled_verbs = {p.action_verb for p in schema.preconditions}
    assert expected_verbs.issubset(compiled_verbs)

    trait_names = {t.name for t in schema.continuous_traits}
    assert {"hunger", "thirst", "energy", "predator_distance", "bush_north_amount"}.issubset(trait_names)


def test_living_world_kernel_instantiation_and_tick() -> None:
    """Verifies that MongNhiemKernel initializes and steps nominal ticks."""
    kernel = MongNhiemKernel.from_schema(str(SCHEMA_PATH))
    result = kernel.tick(stimulus="Nominal foraging observation", delta_time=0.05)

    assert result.tick >= 0
    assert result.delta_time == 0.05
    assert "hunger" in result.state_snapshot
    assert "energy" in result.state_snapshot
    assert result.in_standby is False


def test_living_world_predator_redline_trigger() -> None:
    """Verifies that predator proximity breaches trip the ReflexCircuitBreaker immediately."""
    kernel = MongNhiemKernel.from_schema(str(SCHEMA_PATH))
    # Simulate predator breaching the 35px safety threshold
    kernel.state_engine.set_variable("predator_distance", 25.0)

    result = kernel.tick(stimulus="Wolf ambush detected within safety perimeter")
    assert result.action_verb == "EMERGENCY_BURROW_EVAC"
    assert "CRITICAL REDLINE BREACH" in result.comm_message
    assert "EMERGENCY_BURROW_EVAC" in result.fired_invariants
