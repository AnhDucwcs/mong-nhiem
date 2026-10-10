"""Unit tests for WorldClock, WorldEntity, and DynamicWorldEngine."""
from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from world_engine import DynamicWorldEngine, WorldClock, WorldEntity


def test_world_clock_advancement() -> None:
    clock = WorldClock(start_tick=10)
    assert clock.current_tick == 10
    assert clock.advance(5) == 15
    assert clock.current_tick == 15


def test_entity_ttl_decay_and_expiration() -> None:
    engine = DynamicWorldEngine()
    entity = WorldEntity(
        entity_id="lease_1",
        entity_type="Lease",
        version=1,
        ttl=3,
        properties={"status": "ACTIVE"},
    )
    engine.register_entity(entity)

    # Tick 1
    events = engine.step_ticks(1)
    e = engine.get_entity("lease_1")
    assert e is not None
    assert e.ttl == 2
    assert e.version == 1
    assert not e.is_expired()
    assert len(events) == 0

    # Advance 2 more ticks -> TTL expires
    events = engine.step_ticks(2)
    e = engine.get_entity("lease_1")
    assert e is not None
    assert e.ttl == 0
    assert e.version == 2
    assert e.is_expired()
    assert any("expired" in ev for ev in events)


def test_rate_of_decay_depletion() -> None:
    engine = DynamicWorldEngine()
    entity = WorldEntity(
        entity_id="battery_node",
        entity_type="Drone",
        version=1,
        properties={"power": 10.0},
        rate_of_decay={"power": -4.0},
    )
    engine.register_entity(entity)

    # Step 2 ticks: 10.0 -> 6.0 -> 2.0
    engine.step_ticks(2)
    e = engine.get_entity("battery_node")
    assert e is not None
    assert e.properties["power"] == 2.0
    assert e.version == 3

    # Step 1 tick: 2.0 -> 0.0 (depleted)
    events = engine.step_ticks(1)
    e = engine.get_entity("battery_node")
    assert e is not None
    assert e.properties["power"] == 0.0
    assert any("depleted" in ev for ev in events)


def test_optimistic_concurrency_mutation() -> None:
    engine = DynamicWorldEngine()
    entity = WorldEntity(
        entity_id="db_lock",
        entity_type="Lock",
        version=5,
        properties={"holder": "none"},
    )
    engine.register_entity(entity)

    # Mutate with correct expected_version
    ok, msg, ver = engine.mutate_entity("db_lock", {"holder": "agent_1"}, expected_version=5)
    assert ok is True
    assert ver == 6

    # Attempt mutation with stale expected_version 5 (now at 6)
    ok, msg, ver = engine.mutate_entity("db_lock", {"holder": "agent_2"}, expected_version=5)
    assert ok is False
    assert "STALE_VERSION_MISMATCH" in msg
    assert ver == 6


def test_scheduled_background_event() -> None:
    engine = DynamicWorldEngine()
    entity = WorldEntity(
        entity_id="server_1",
        entity_type="Host",
        version=1,
        properties={"status": "HEALTHY"},
    )
    engine.register_entity(entity)

    def fail_server(entities):
        entities["server_1"].properties["status"] = "CRASHED"
        entities["server_1"].version += 1
        return "Server crashed due to kernel panic."

    engine.schedule_event(trigger_tick=3, event_name="kernel_panic", mutation_fn=fail_server)

    # Advance to tick 2 (not yet triggered)
    engine.step_ticks(2)
    e = engine.get_entity("server_1")
    assert e.properties["status"] == "HEALTHY"

    # Advance to tick 3 (triggers event)
    events = engine.step_ticks(1)
    e = engine.get_entity("server_1")
    assert e.properties["status"] == "CRASHED"
    assert any("kernel_panic" in ev for ev in events)
