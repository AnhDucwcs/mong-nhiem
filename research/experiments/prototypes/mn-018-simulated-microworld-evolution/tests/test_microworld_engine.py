"""Unit tests for MicroworldEngine, ConservationGuard, and multi-rate WorldClock."""
import pytest
import sys
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from microworld_engine import (
    ConservationGuard,
    MicroworldEngine,
    ScheduledEvent,
    WorldClock,
    WorldEntity,
)


def test_world_clock_and_monotonic_ticks():
    clock = WorldClock(start_tick=10)
    assert clock.current_tick == 10
    assert clock.advance(5) == 15
    assert clock.current_tick == 15
    with pytest.raises(ValueError):
        clock.advance(-1)


def test_entity_ttl_and_decay():
    engine = MicroworldEngine(domain="orbital_station", start_tick=0)
    entity = WorldEntity(
        entity_id="battery_1",
        entity_type="power_storage",
        version=1,
        properties={"stored_kwh": 50.0, "status": "ACTIVE"},
        ttl=3,
        rate_of_decay={"stored_kwh": -2.0},
    )
    engine.register_entity(entity)

    # Step 1 tick
    engine.step_ticks(1)
    e = engine.get_entity("battery_1")
    assert e.ttl == 2
    assert e.properties["stored_kwh"] == 48.0
    assert e.version == 2
    assert not e.is_expired()

    # Step 2 more ticks -> TTL expires
    engine.step_ticks(2)
    e = engine.get_entity("battery_1")
    assert e.ttl == 0
    assert e.is_expired()
    assert e.properties["status"] == "EXPIRED"


def test_conservation_guard_domain_a_orbital():
    nominal = {"nominal_coolant_liters": 100.0}
    engine = MicroworldEngine(domain="orbital_station", nominal_constants=nominal)

    p_bus = WorldEntity("power_bus", "bus", properties={"stored_kwh": 100.0})
    ls = WorldEntity("life_support", "env", properties={"o2_percent": 21.0, "pressure_kpa": 101.3})
    c_a = WorldEntity("coolant_loop_a", "loop", properties={"volume_liters": 40.0})
    c_b = WorldEntity("coolant_loop_b", "loop", properties={"volume_liters": 40.0})
    c_res = WorldEntity("coolant_reserve", "reserve", properties={"volume_liters": 20.0})

    for ent in [p_bus, ls, c_a, c_b, c_res]:
        engine.register_entity(ent)

    # Valid atomic transfer: transfer 5L from reserve to loop_a
    success, msg, v_dict = engine.apply_transaction({
        "coolant_reserve": {"volume_liters": 15.0},
        "coolant_loop_a": {"volume_liters": 45.0},
    }, expected_versions={"coolant_reserve": 1, "coolant_loop_a": 1})
    assert success

    # Invalid mutation: oxygen drops below 19.5%
    success, msg, v = engine.mutate_entity("life_support", {"o2_percent": 18.0}, expected_version=1)
    assert not success
    assert "Atmospheric O2 fraction out of safe bounds" in msg

    # Invalid mutation: pressure drops below 95.0 kPa
    success, msg, v = engine.mutate_entity("life_support", {"pressure_kpa": 90.0}, expected_version=1)
    assert not success
    assert "Cabin atmospheric pressure breached minimum" in msg

    # Invalid mutation: coolant leaks/created out of nowhere
    success, msg, v = engine.mutate_entity("coolant_loop_b", {"volume_liters": 50.0}, expected_version=1)
    assert not success
    assert "Total coolant volume mismatch" in msg


def test_conservation_guard_domain_b_microgrid():
    engine = MicroworldEngine(domain="industrial_microgrid")
    hosp = WorldEntity("hospital_ward", "load", properties={"power_kw": 60.0, "min_required_kw": 50.0})
    bess = WorldEntity("bess_unit", "storage", properties={"soc_percent": 75.0})
    grid = WorldEntity("grid_controller", "controller", properties={
        "generation_kw": 160.0,
        "load_kw": 140.0,
        "battery_net_kw": 20.0,  # 160 = 140 + 20
    })

    for ent in [hosp, bess, grid]:
        engine.register_entity(ent)

    # Valid mutation
    success, msg, v = engine.mutate_entity("bess_unit", {"soc_percent": 80.0}, expected_version=1)
    assert success

    # Invalid: hospital power drops below minimum
    success, msg, v = engine.mutate_entity("hospital_ward", {"power_kw": 40.0}, expected_version=1)
    assert not success
    assert "Critical hospital power dropped below required" in msg

    # Invalid: battery SOC out of bounds (> 100%)
    success, msg, v = engine.mutate_entity("bess_unit", {"soc_percent": 110.0}, expected_version=2)
    assert not success
    assert "Battery SOC out of physical limits" in msg

    # Invalid: grid energy imbalance
    success, msg, v = engine.mutate_entity("grid_controller", {"generation_kw": 200.0}, expected_version=1)
    assert not success
    assert "Microgrid energy balance violated" in msg


def test_conservation_guard_domain_c_fleet():
    nominal = {"nominal_total_inventory": 100}
    engine = MicroworldEngine(domain="fleet_supply_chain", nominal_constants=nominal)

    hub_a = WorldEntity("hub_alpha", "hub", properties={"inventory_units": 60})
    hub_b = WorldEntity("hub_beta", "hub", properties={"inventory_units": 40})
    drone_1 = WorldEntity("drone_1", "drone", properties={"payload_units": 0, "max_capacity": 5, "battery_percent": 100.0})

    for ent in [hub_a, hub_b, drone_1]:
        engine.register_entity(ent)

    # Valid transfer: load 3 units from hub_a onto drone_1
    # Note: atomic transfer updates both entities
    engine.entities["hub_alpha"].properties["inventory_units"] = 57
    success, msg, v = engine.mutate_entity("drone_1", {"payload_units": 3}, expected_version=1)
    assert success

    # Invalid: drone payload exceeds capacity
    success, msg, v = engine.mutate_entity("drone_1", {"payload_units": 10}, expected_version=2)
    assert not success
    assert "payload exceeds capacity" in msg

    # Invalid: duplicated inventory (sum is 110 != 100)
    engine.entities["hub_alpha"].properties["inventory_units"] = 70
    success, msg, v = engine.mutate_entity("drone_1", {"payload_units": 0}, expected_version=2)
    assert not success
    assert "Total fleet inventory conserved violation" in msg


def test_scheduled_background_events():
    engine = MicroworldEngine(domain="orbital_station")
    sensor = WorldEntity("sensor_rad", "telemetry", properties={"radiation_mrem": 5.0})
    engine.register_entity(sensor)

    def solar_flare(entities):
        entities["sensor_rad"].properties["radiation_mrem"] += 50.0
        entities["sensor_rad"].version += 1
        return "Radiation spiked by 50 mrem."

    engine.schedule_event(trigger_tick=3, event_name="solar_flare", mutation_fn=solar_flare)

    engine.step_ticks(2)
    assert engine.get_entity("sensor_rad").properties["radiation_mrem"] == 5.0

    events = engine.step_ticks(1)
    assert any("solar_flare" in e for e in events)
    assert engine.get_entity("sensor_rad").properties["radiation_mrem"] == 55.0
    assert engine.get_entity("sensor_rad").version == 2
