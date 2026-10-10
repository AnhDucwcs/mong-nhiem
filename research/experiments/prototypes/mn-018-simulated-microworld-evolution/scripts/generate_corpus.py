"""Corpus Generator for MN-018 Long-Horizon Microworld Evolution Benchmark.

Generates 30 heterogeneous long-horizon scenarios (T=50-100 steps) across 3 domains:
- Domain A: Autonomous Orbital Station Life Support (Cases 1-10)
- Domain B: Smart Industrial Microgrid & Storage (Cases 11-20)
- Domain C: Multi-Hub Autonomous Fleet Supply Chain (Cases 21-30)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def build_case_domain_a(case_num: int) -> Dict[str, Any]:
    """Build Domain A: Orbital Station Life Support case."""
    case_id = f"MN018-CASE-{case_num:03d}"
    is_stress = (case_num == 10)
    nominal_coolant = 100.0

    initial_entities = {
        "power_bus": {
            "entity_id": "power_bus",
            "entity_type": "bus",
            "version": 1,
            "properties": {"stored_kwh": 85.0, "status": "ACTIVE", "stabilized": False},
            "rate_of_decay": {"stored_kwh": -0.5},
        },
        "life_support": {
            "entity_id": "life_support",
            "entity_type": "environment",
            "version": 1,
            "properties": {"o2_percent": 21.0, "pressure_kpa": 101.3, "scrubber_state": "STANDBY"},
            "rate_of_decay": {"o2_percent": -0.02},
        },
        "coolant_loop_a": {
            "entity_id": "coolant_loop_a",
            "entity_type": "thermal_loop",
            "version": 1,
            "properties": {"volume_liters": 40.0, "temp_c": 35.0},
        },
        "coolant_loop_b": {
            "entity_id": "coolant_loop_b",
            "entity_type": "thermal_loop",
            "version": 1,
            "properties": {"volume_liters": 40.0, "temp_c": 34.0},
        },
        "coolant_reserve": {
            "entity_id": "coolant_reserve",
            "entity_type": "tank",
            "version": 1,
            "properties": {"volume_liters": 20.0},
        },
        "solar_array": {
            "entity_id": "solar_array",
            "entity_type": "generator",
            "version": 1,
            "properties": {"output_kw": 45.0, "tracking_mode": "AUTO"},
        },
    }

    # Scheduled background shocks
    scheduled_events = [
        {
            "trigger_tick": 12,
            "event_name": "orbital_eclipse_ingress",
            "entity_id": "solar_array",
            "updates": {"output_kw": 0.0, "tracking_mode": "ECLIPSE_STOW"},
        },
        {
            "trigger_tick": 28,
            "event_name": "orbital_eclipse_egress",
            "entity_id": "solar_array",
            "updates": {"output_kw": 45.0, "tracking_mode": "AUTO"},
        },
        {
            "trigger_tick": 38,
            "event_name": "thermal_spike_sensor",
            "entity_id": "coolant_loop_a",
            "updates": {"temp_c": 42.0},
        },
    ]
    if is_stress:
        scheduled_events.extend([
            {
                "trigger_tick": 55,
                "event_name": "micrometeorite_radiator_shunt",
                "entity_id": "coolant_loop_b",
                "updates": {"temp_c": 48.0},
            },
            {
                "trigger_tick": 75,
                "event_name": "secondary_solar_flare",
                "entity_id": "solar_array",
                "updates": {"output_kw": 55.0},
            },
        ])

    subgoals = [
        {
            "goal_id": "G1",
            "title": "Activate CO2 Scrubber",
            "description": "Engage primary life support scrubber to cycle cabin atmosphere",
            "prerequisites": [],
            "allowed_actions": ["scrubber_mode life_support ACTIVE", "adjust_o2_flow life_support 0.5"],
            "target": {"entity_id": "life_support", "prop": "scrubber_state", "value": "ACTIVE"},
        },
        {
            "goal_id": "G2",
            "title": "Balance Thermal Coolant Loop A",
            "description": "Transfer 5L coolant from reserve to loop A to maintain thermal equilibrium",
            "prerequisites": ["G1"],
            "allowed_actions": ["transfer_coolant coolant_reserve coolant_loop_a 5", "inspect_thermal coolant_loop_a"],
            "target": {"entity_id": "coolant_loop_a", "prop": "volume_liters", "value": 45.0},
        },
        {
            "goal_id": "G3",
            "title": "Reinforce Cabin Pressure",
            "description": "Regulate life support nitrogen bleed to maintain cabin pressure >= 102.0 kPa",
            "prerequisites": ["G2"],
            "allowed_actions": ["inject_buffer_gas life_support 102.5", "vent_cabin life_support"],
            "target": {"entity_id": "life_support", "prop": "pressure_kpa", "min_value": 102.0},
        },
        {
            "goal_id": "G4",
            "title": "Configure Solar Tracking",
            "description": "Lock solar tracking mode to MAXIMUM_INSOLATION",
            "prerequisites": ["G3"],
            "allowed_actions": ["set_solar_mode solar_array MAXIMUM_INSOLATION", "calibrate_gimbal solar_array"],
            "target": {"entity_id": "solar_array", "prop": "tracking_mode", "value": "MAXIMUM_INSOLATION"},
        },
        {
            "goal_id": "G5",
            "title": "Confirm Station Life Support Stabilization",
            "description": "Verify bus telemetry and emit station health stabilization clearance",
            "prerequisites": ["G4"],
            "allowed_actions": ["confirm_stabilization power_bus", "poll_telemetry power_bus"],
            "target": {"entity_id": "power_bus", "prop": "stabilized", "value": True},
        },
    ]

    all_actions = [
        "scrubber_mode life_support ACTIVE",
        "adjust_o2_flow life_support 0.5",
        "transfer_coolant coolant_reserve coolant_loop_a 5",
        "inspect_thermal coolant_loop_a",
        "inject_buffer_gas life_support 102.5",
        "vent_cabin life_support",
        "set_solar_mode solar_array MAXIMUM_INSOLATION",
        "calibrate_gimbal solar_array",
        "confirm_stabilization power_bus",
        "poll_telemetry power_bus",
    ]

    return {
        "case_id": case_id,
        "domain": "orbital_station",
        "title": f"Orbital Station Life Support Stabilization - Mission {case_num}",
        "mission_description": "Maintain life support integrity, balance thermal loops, and confirm bus stabilization across orbital eclipse dynamics.",
        "nominal_constants": {"nominal_coolant_liters": nominal_coolant},
        "initial_entities": initial_entities,
        "scheduled_events": scheduled_events,
        "subgoals": subgoals,
        "all_actions": all_actions,
        "max_turns": 100 if is_stress else 60,
    }


def build_case_domain_b(case_num: int) -> Dict[str, Any]:
    """Build Domain B: Smart Industrial Microgrid & Storage case."""
    case_id = f"MN018-CASE-{case_num:03d}"
    is_stress = (case_num == 20)

    initial_entities = {
        "grid_controller": {
            "entity_id": "grid_controller",
            "entity_type": "controller",
            "version": 1,
            "properties": {
                "generation_kw": 200.0,
                "load_kw": 180.0,
                "battery_net_kw": 20.0,
                "frequency_hz": 50.0,
                "grid_stable": False,
            },
        },
        "hospital_ward": {
            "entity_id": "hospital_ward",
            "entity_type": "critical_load",
            "version": 1,
            "properties": {"power_kw": 60.0, "min_required_kw": 50.0, "feeder": "BUS_A"},
        },
        "factory_load": {
            "entity_id": "factory_load",
            "entity_type": "industrial_load",
            "version": 1,
            "properties": {"power_kw": 120.0, "curtailable": True, "curtail_state": "NORMAL"},
        },
        "bess_unit": {
            "entity_id": "bess_unit",
            "entity_type": "storage",
            "version": 1,
            "properties": {"soc_percent": 65.0, "charge_rate_kw": 20.0, "mode": "CHARGE"},
            "rate_of_decay": {"soc_percent": -0.1},
        },
        "gas_turbine": {
            "entity_id": "gas_turbine",
            "entity_type": "generator",
            "version": 1,
            "properties": {"output_kw": 100.0, "fuel_flow_kg_h": 22.0, "status": "DISPATCHED"},
        },
        "solar_pv": {
            "entity_id": "solar_pv",
            "entity_type": "generator",
            "version": 1,
            "properties": {"output_kw": 100.0, "inverter_status": "ONLINE"},
        },
    }

    scheduled_events = [
        {
            "trigger_tick": 15,
            "event_name": "industrial_furnace_spike",
            "entity_id": "factory_load",
            "updates": {"power_kw": 150.0},
        },
        {
            "trigger_tick": 30,
            "event_name": "cloud_cover_drop",
            "entity_id": "solar_pv",
            "updates": {"output_kw": 40.0},
        },
    ]
    if is_stress:
        scheduled_events.extend([
            {
                "trigger_tick": 50,
                "event_name": "second_shift_commence",
                "entity_id": "factory_load",
                "updates": {"power_kw": 170.0},
            },
            {
                "trigger_tick": 70,
                "event_name": "ambient_heat_derate",
                "entity_id": "gas_turbine",
                "updates": {"output_kw": 90.0},
            },
        ])

    subgoals = [
        {
            "goal_id": "G1",
            "title": "Ramp Natural Gas Turbine",
            "description": "Ramp gas turbine output to 140 kW to absorb upcoming industrial shift load",
            "prerequisites": [],
            "allowed_actions": ["ramp_turbine gas_turbine 140", "inspect_turbine gas_turbine"],
            "target": {"entity_id": "gas_turbine", "prop": "output_kw", "value": 140.0},
        },
        {
            "goal_id": "G2",
            "title": "Switch BESS to Peak Shaving",
            "description": "Switch battery energy storage to peak shaving mode with net discharge",
            "prerequisites": ["G1"],
            "allowed_actions": ["set_bess_mode bess_unit DISCHARGE 30", "throttle_bess bess_unit 0"],
            "target": {"entity_id": "bess_unit", "prop": "mode", "value": "DISCHARGE"},
        },
        {
            "goal_id": "G3",
            "title": "Curtail Non-Critical Factory Load",
            "description": "Apply 20% curtailment to secondary industrial feeders",
            "prerequisites": ["G2"],
            "allowed_actions": ["curtail_load factory_load 100", "disconnect_substation factory_load"],
            "target": {"entity_id": "factory_load", "prop": "curtail_state", "value": "CURTAILED"},
        },
        {
            "goal_id": "G4",
            "title": "Lock Hospital Power Feeder",
            "description": "Transfer critical hospital ward to dual-redundant bus feeder",
            "prerequisites": ["G3"],
            "allowed_actions": ["lock_feeder hospital_ward DUAL_REDUNDANT", "audit_hospital hospital_ward"],
            "target": {"entity_id": "hospital_ward", "prop": "feeder", "value": "DUAL_REDUNDANT"},
        },
        {
            "goal_id": "G5",
            "title": "Certify Microgrid Stability",
            "description": "Validate 50.0 Hz grid frequency and certify power balance",
            "prerequisites": ["G4"],
            "allowed_actions": ["certify_stability grid_controller", "poll_grid grid_controller"],
            "target": {"entity_id": "grid_controller", "prop": "grid_stable", "value": True},
        },
    ]

    all_actions = [
        "ramp_turbine gas_turbine 140",
        "inspect_turbine gas_turbine",
        "set_bess_mode bess_unit DISCHARGE 30",
        "throttle_bess bess_unit 0",
        "curtail_load factory_load 100",
        "disconnect_substation factory_load",
        "lock_feeder hospital_ward DUAL_REDUNDANT",
        "audit_hospital hospital_ward",
        "certify_stability grid_controller",
        "poll_grid grid_controller",
    ]

    return {
        "case_id": case_id,
        "domain": "industrial_microgrid",
        "title": f"Smart Industrial Microgrid Dispatch - Mission {case_num}",
        "mission_description": "Balance generation and dynamic loads, preserve critical hospital power, and verify grid stability.",
        "nominal_constants": {},
        "initial_entities": initial_entities,
        "scheduled_events": scheduled_events,
        "subgoals": subgoals,
        "all_actions": all_actions,
        "max_turns": 100 if is_stress else 60,
    }


def build_case_domain_c(case_num: int) -> Dict[str, Any]:
    """Build Domain C: Multi-Hub Autonomous Fleet Supply Chain case."""
    case_id = f"MN018-CASE-{case_num:03d}"
    is_stress = (case_num == 30)
    nominal_inventory = 120

    initial_entities = {
        "hub_alpha": {
            "entity_id": "hub_alpha",
            "entity_type": "hub",
            "version": 1,
            "properties": {"inventory_units": 60, "dock_status": "CLEAR"},
        },
        "hub_beta": {
            "entity_id": "hub_beta",
            "entity_type": "hub",
            "version": 1,
            "properties": {"inventory_units": 40, "dock_status": "CLEAR"},
        },
        "hub_gamma": {
            "entity_id": "hub_gamma",
            "entity_type": "hub",
            "version": 1,
            "properties": {"inventory_units": 20, "dock_status": "CLEAR"},
        },
        "drone_alpha_1": {
            "entity_id": "drone_alpha_1",
            "entity_type": "drone",
            "version": 1,
            "properties": {
                "payload_units": 0,
                "max_capacity": 5,
                "battery_percent": 95.0,
                "location": "hub_alpha",
                "route_status": "IDLE",
            },
            "rate_of_decay": {"battery_percent": -0.2},
        },
        "drone_beta_1": {
            "entity_id": "drone_beta_1",
            "entity_type": "drone",
            "version": 1,
            "properties": {
                "payload_units": 0,
                "max_capacity": 5,
                "battery_percent": 90.0,
                "location": "hub_beta",
                "route_status": "IDLE",
            },
            "rate_of_decay": {"battery_percent": -0.2},
        },
        "fleet_coordinator": {
            "entity_id": "fleet_coordinator",
            "entity_type": "coordinator",
            "version": 1,
            "properties": {"active_routes": 0, "mission_certified": False},
        },
    }

    scheduled_events = [
        {
            "trigger_tick": 18,
            "event_name": "weather_headwind_alert",
            "entity_id": "drone_alpha_1",
            "updates": {"battery_percent": 75.0},
        },
        {
            "trigger_tick": 32,
            "event_name": "corridor_airspace_congestion",
            "entity_id": "hub_beta",
            "updates": {"dock_status": "CONGESTED"},
        },
    ]
    if is_stress:
        scheduled_events.extend([
            {
                "trigger_tick": 52,
                "event_name": "radar_recalibration_delay",
                "entity_id": "hub_gamma",
                "updates": {"dock_status": "CALIBRATING"},
            },
            {
                "trigger_tick": 72,
                "event_name": "thermal_battery_throttle",
                "entity_id": "drone_beta_1",
                "updates": {"battery_percent": 60.0},
            },
        ])

    subgoals = [
        {
            "goal_id": "G1",
            "title": "Load Critical Medical Payload at Hub Alpha",
            "description": "Load 4 inventory units from Hub Alpha into Drone Alpha 1",
            "prerequisites": [],
            "allowed_actions": ["load_payload hub_alpha drone_alpha_1 4", "inspect_drone drone_alpha_1"],
            "target": {"entity_id": "drone_alpha_1", "prop": "payload_units", "value": 4},
        },
        {
            "goal_id": "G2",
            "title": "Dispatch Drone Alpha 1 to Hub Beta",
            "description": "Execute flight dispatch of Drone Alpha 1 along designated transit corridor",
            "prerequisites": ["G1"],
            "allowed_actions": ["dispatch_flight drone_alpha_1 hub_beta", "hold_position drone_alpha_1"],
            "target": {"entity_id": "drone_alpha_1", "prop": "location", "value": "hub_beta"},
        },
        {
            "goal_id": "G3",
            "title": "Unload Payload at Hub Beta",
            "description": "Unload 4 units into Hub Beta inventory, maintaining total fleet conservation",
            "prerequisites": ["G2"],
            "allowed_actions": ["unload_payload drone_alpha_1 hub_beta 4", "inspect_hub hub_beta"],
            "target": {"entity_id": "drone_alpha_1", "prop": "payload_units", "value": 0},
        },
        {
            "goal_id": "G4",
            "title": "Dock Drone Alpha 1 for Recharging",
            "description": "Route Drone Alpha 1 to rapid charging bay",
            "prerequisites": ["G3"],
            "allowed_actions": ["dock_recharge drone_alpha_1 hub_beta", "status_check drone_alpha_1"],
            "target": {"entity_id": "drone_alpha_1", "prop": "route_status", "value": "RECHARGING"},
        },
        {
            "goal_id": "G5",
            "title": "Certify Fleet Manifest and Inventory Audit",
            "description": "Execute fleet manifest reconciliation and certify total conserved inventory",
            "prerequisites": ["G4"],
            "allowed_actions": ["certify_fleet fleet_coordinator", "audit_inventory fleet_coordinator"],
            "target": {"entity_id": "fleet_coordinator", "prop": "mission_certified", "value": True},
        },
    ]

    all_actions = [
        "load_payload hub_alpha drone_alpha_1 4",
        "inspect_drone drone_alpha_1",
        "dispatch_flight drone_alpha_1 hub_beta",
        "hold_position drone_alpha_1",
        "unload_payload drone_alpha_1 hub_beta 4",
        "inspect_hub hub_beta",
        "dock_recharge drone_alpha_1 hub_beta",
        "status_check drone_alpha_1",
        "certify_fleet fleet_coordinator",
        "audit_inventory fleet_coordinator",
    ]

    return {
        "case_id": case_id,
        "domain": "fleet_supply_chain",
        "title": f"Autonomous Fleet Supply Chain Logistics - Mission {case_num}",
        "mission_description": "Coordinate multi-hub payload transfers, preserve total inventory conservation, and maintain fleet battery integrity.",
        "nominal_constants": {"nominal_total_inventory": nominal_inventory},
        "initial_entities": initial_entities,
        "scheduled_events": scheduled_events,
        "subgoals": subgoals,
        "all_actions": all_actions,
        "max_turns": 100 if is_stress else 60,
    }


def main() -> None:
    cases: List[Dict[str, Any]] = []

    # Domain A: 10 cases (1-10)
    for i in range(1, 11):
        cases.append(build_case_domain_a(i))

    # Domain B: 10 cases (11-20)
    for i in range(11, 21):
        cases.append(build_case_domain_b(i))

    # Domain C: 10 cases (21-30)
    for i in range(21, 31):
        cases.append(build_case_domain_c(i))

    out_dir = Path(__file__).resolve().parent.parent / "definition" / "corpus-v1"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "cases.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)

    print(f"Generated {len(cases)} cases into {out_file}")


if __name__ == "__main__":
    main()
