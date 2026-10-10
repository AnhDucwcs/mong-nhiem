"""Stress Corpus Generator for MN-018: High-Difficulty Microworld Evolution Benchmark.

Generates 30 ultra long-horizon stress scenarios (T=150-200 ticks, K=8 subgoals)
incorporating all 3 stress dimensions:
1. Multi-Distractor & Delayed Rollback Traps (4-6 actions per phase, delayed invariant breaches)
2. Cascading Compound Environmental Shocks (multiple concurrent shock clusters across ticks)
3. Ultra Long-Horizon (T=150-200 ticks, K=8 topological sub-goals, forcing 3-5 AutoDream cycles)

Domains:
- Domain A: Autonomous Orbital Station Life Support (Cases 1-10)
- Domain B: Smart Industrial Microgrid & Storage (Cases 11-20)
- Domain C: Multi-Hub Autonomous Fleet Supply Chain (Cases 21-30)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def build_stress_case_domain_a(case_num: int) -> Dict[str, Any]:
    """Build Domain A: Orbital Station Life Support stress case (K=8, 4-6 actions/phase)."""
    case_id = f"MN018-STRESS-CASE-{case_num:03d}"
    nominal_coolant = 100.0

    initial_entities = {
        "power_bus": {
            "entity_id": "power_bus",
            "entity_type": "bus",
            "version": 1,
            "properties": {
                "stored_kwh": 95.0,
                "status": "ACTIVE",
                "stabilized": False,
                "impedance_mode": "STANDARD",
            },
            "rate_of_decay": {"stored_kwh": -0.3},
        },
        "life_support": {
            "entity_id": "life_support",
            "entity_type": "environment",
            "version": 1,
            "properties": {
                "o2_percent": 21.0,
                "pressure_kpa": 101.3,
                "scrubber_state": "STANDBY",
                "airlock_state": "UNSEALED",
            },
            "rate_of_decay": {"o2_percent": -0.015},
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
            "properties": {"volume_liters": 40.0, "temp_c": 34.0, "radiator_mode": "NORMAL"},
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
            "properties": {"output_kw": 50.0, "tracking_mode": "AUTO"},
        },
    }

    # Cascading compound environmental shock clusters
    scheduled_events = [
        {
            "trigger_tick": 15,
            "event_name": "orbital_eclipse_ingress_cluster",
            "entity_id": "solar_array",
            "updates": {"output_kw": 0.0, "tracking_mode": "ECLIPSE_STOW"},
        },
        {
            "trigger_tick": 30,
            "event_name": "micrometeorite_radiator_impact",
            "entity_id": "coolant_loop_b",
            "updates": {"temp_c": 46.0},
        },
        {
            "trigger_tick": 50,
            "event_name": "secondary_thermal_spike",
            "entity_id": "coolant_loop_a",
            "updates": {"temp_c": 43.0},
        },
        {
            "trigger_tick": 75,
            "event_name": "orbital_eclipse_egress_surge",
            "entity_id": "solar_array",
            "updates": {"output_kw": 48.0, "tracking_mode": "AUTO"},
        },
        {
            "trigger_tick": 105,
            "event_name": "geomagnetic_storm_solar_flare",
            "entity_id": "solar_array",
            "updates": {"output_kw": 62.0},
        },
        {
            "trigger_tick": 135,
            "event_name": "radiator_bypass_pressure_flutter",
            "entity_id": "coolant_loop_b",
            "updates": {"temp_c": 37.0},
        },
    ]

    # K=8 Topological sub-goals with multi-distractors & delayed rollback traps
    subgoals = [
        {
            "goal_id": "G1",
            "title": "Activate Primary Atmosphere Scrubber",
            "description": "Engage primary CO2 scrubber to cycle atmosphere",
            "prerequisites": [],
            "allowed_actions": [
                "scrubber_mode life_support ACTIVE",
                "adjust_o2_flow life_support 0.5",
                "inspect_atmosphere life_support",
                "vent_cabin life_support",
            ],
            "target": {"entity_id": "life_support", "prop": "scrubber_state", "value": "ACTIVE"},
        },
        {
            "goal_id": "G2",
            "title": "Balance Thermal Coolant Loop A",
            "description": "Transfer 5L coolant from reserve to loop A",
            "prerequisites": ["G1"],
            "allowed_actions": [
                "transfer_coolant coolant_reserve coolant_loop_a 5",
                "inspect_thermal coolant_loop_a",
                "poll_coolant_reserve coolant_reserve",
                "purge_coolant coolant_reserve 10",
            ],
            "target": {"entity_id": "coolant_loop_a", "prop": "volume_liters", "value": 45.0},
        },
        {
            "goal_id": "G3",
            "title": "Bypass Loop B Radiator Valve",
            "description": "Set coolant loop B radiator mode to BYPASS to prevent overcooling",
            "prerequisites": ["G1", "G2"],
            "allowed_actions": [
                "set_radiator_mode coolant_loop_b BYPASS",
                "inspect_thermal coolant_loop_b",
                "calibrate_valve coolant_loop_b",
                "overheat_loop coolant_loop_b 120",
            ],
            "target": {"entity_id": "coolant_loop_b", "prop": "radiator_mode", "value": "BYPASS"},
        },
        {
            "goal_id": "G4",
            "title": "Pressurize Cabin Buffer Gas",
            "description": "Inject nitrogen buffer gas to reach >= 102.0 kPa",
            "prerequisites": ["G2", "G3"],
            "allowed_actions": [
                "inject_buffer_gas life_support 102.5",
                "inspect_cabin_pressure life_support",
                "poll_o2_fraction life_support",
                "depressurize_buffer life_support 80.0",
            ],
            "target": {"entity_id": "life_support", "prop": "pressure_kpa", "min_value": 102.0},
        },
        {
            "goal_id": "G5",
            "title": "Lock Solar Array to Maximum Insolation",
            "description": "Configure solar tracking gimbal to MAXIMUM_INSOLATION",
            "prerequisites": ["G4"],
            "allowed_actions": [
                "set_solar_mode solar_array MAXIMUM_INSOLATION",
                "calibrate_gimbal solar_array",
                "poll_solar_flux solar_array",
                "stow_solar_array solar_array 0.0",
            ],
            "target": {"entity_id": "solar_array", "prop": "tracking_mode", "value": "MAXIMUM_INSOLATION"},
        },
        {
            "goal_id": "G6",
            "title": "Recalibrate Main Power Bus Impedance",
            "description": "Shift power bus to HIGH_IMPEDANCE isolation mode",
            "prerequisites": ["G5"],
            "allowed_actions": [
                "recalibrate_bus power_bus HIGH_IMPEDANCE",
                "measure_impedance power_bus",
                "inspect_inverter power_bus",
                "overload_bus power_bus 150",
            ],
            "target": {"entity_id": "power_bus", "prop": "impedance_mode", "value": "HIGH_IMPEDANCE"},
        },
        {
            "goal_id": "G7",
            "title": "Seal Station Airlock Bulkhead",
            "description": "Lock airlock bulkheads into hermetically sealed LOCKED state",
            "prerequisites": ["G5", "G6"],
            "allowed_actions": [
                "seal_airlock life_support LOCKED",
                "status_check life_support",
                "audit_airlock_seals life_support",
                "vent_cabin life_support",
            ],
            "target": {"entity_id": "life_support", "prop": "airlock_state", "value": "LOCKED"},
        },
        {
            "goal_id": "G8",
            "title": "Confirm Comprehensive Station Stabilization",
            "description": "Verify bus telemetry and issue final stabilization certificate",
            "prerequisites": ["G6", "G7"],
            "allowed_actions": [
                "confirm_stabilization power_bus",
                "poll_telemetry power_bus",
                "audit_system_health power_bus",
            ],
            "target": {"entity_id": "power_bus", "prop": "stabilized", "value": True},
        },
    ]

    all_actions = [
        "scrubber_mode life_support ACTIVE",
        "adjust_o2_flow life_support 0.5",
        "inspect_atmosphere life_support",
        "vent_cabin life_support",
        "transfer_coolant coolant_reserve coolant_loop_a 5",
        "inspect_thermal coolant_loop_a",
        "poll_coolant_reserve coolant_reserve",
        "purge_coolant coolant_reserve 10",
        "set_radiator_mode coolant_loop_b BYPASS",
        "inspect_thermal coolant_loop_b",
        "calibrate_valve coolant_loop_b",
        "overheat_loop coolant_loop_b 120",
        "inject_buffer_gas life_support 102.5",
        "inspect_cabin_pressure life_support",
        "poll_o2_fraction life_support",
        "depressurize_buffer life_support 80.0",
        "set_solar_mode solar_array MAXIMUM_INSOLATION",
        "calibrate_gimbal solar_array",
        "poll_solar_flux solar_array",
        "stow_solar_array solar_array 0.0",
        "recalibrate_bus power_bus HIGH_IMPEDANCE",
        "measure_impedance power_bus",
        "inspect_inverter power_bus",
        "overload_bus power_bus 150",
        "seal_airlock life_support LOCKED",
        "status_check life_support",
        "audit_airlock_seals life_support",
        "confirm_stabilization power_bus",
        "poll_telemetry power_bus",
        "audit_system_health power_bus",
    ]

    return {
        "case_id": case_id,
        "domain": "orbital_station",
        "title": f"High-Stress Orbital Station Evolution - Mission {case_num}",
        "mission_description": "Maintain life support integrity, balance thermal loops, manage cascading shocks, and certify stabilization across extended horizon (T=150).",
        "nominal_constants": {"nominal_coolant_liters": nominal_coolant},
        "initial_entities": initial_entities,
        "scheduled_events": scheduled_events,
        "subgoals": subgoals,
        "all_actions": all_actions,
        "max_turns": 150,
    }


def build_stress_case_domain_b(case_num: int) -> Dict[str, Any]:
    """Build Domain B: Industrial Microgrid stress case (K=8, 4-6 actions/phase)."""
    case_id = f"MN018-STRESS-CASE-{case_num:03d}"

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
                "power_factor": 0.95,
                "breaker_state": "DISARMED",
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
            "properties": {"soc_percent": 70.0, "charge_rate_kw": 20.0, "mode": "CHARGE"},
            "rate_of_decay": {"soc_percent": -0.08},
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
            "properties": {"output_kw": 100.0, "inverter_status": "ONLINE", "sync_mode": "ISOLATED"},
        },
    }

    scheduled_events = [
        {
            "trigger_tick": 18,
            "event_name": "industrial_arc_furnace_surge",
            "entity_id": "factory_load",
            "updates": {"power_kw": 160.0},
        },
        {
            "trigger_tick": 35,
            "event_name": "cloud_stratus_cover_drop",
            "entity_id": "solar_pv",
            "updates": {"output_kw": 35.0},
        },
        {
            "trigger_tick": 55,
            "event_name": "heavy_machinery_second_shift",
            "entity_id": "factory_load",
            "updates": {"power_kw": 175.0},
        },
        {
            "trigger_tick": 80,
            "event_name": "ambient_heat_turbine_derate",
            "entity_id": "gas_turbine",
            "updates": {"output_kw": 115.0},
        },
        {
            "trigger_tick": 110,
            "event_name": "cloud_layer_clearing_burst",
            "entity_id": "solar_pv",
            "updates": {"output_kw": 85.0},
        },
        {
            "trigger_tick": 135,
            "event_name": "substation_power_factor_jitter",
            "entity_id": "grid_controller",
            "updates": {"power_factor": 0.94},
        },
    ]

    subgoals = [
        {
            "goal_id": "G1",
            "title": "Ramp Natural Gas Turbine",
            "description": "Ramp gas turbine generation output to 140 kW",
            "prerequisites": [],
            "allowed_actions": [
                "ramp_turbine gas_turbine 140",
                "inspect_turbine gas_turbine",
                "poll_fuel_rate gas_turbine",
                "trip_turbine gas_turbine",
            ],
            "target": {"entity_id": "gas_turbine", "prop": "output_kw", "value": 140.0},
        },
        {
            "goal_id": "G2",
            "title": "Switch BESS to Peak Shaving Discharge",
            "description": "Switch battery energy storage to peak shaving DISCHARGE mode",
            "prerequisites": ["G1"],
            "allowed_actions": [
                "set_bess_mode bess_unit DISCHARGE 30",
                "throttle_bess bess_unit 0",
                "inspect_bess bess_unit",
                "deep_discharge_bess bess_unit 120",
            ],
            "target": {"entity_id": "bess_unit", "prop": "mode", "value": "DISCHARGE"},
        },
        {
            "goal_id": "G3",
            "title": "Curtail Non-Critical Factory Load",
            "description": "Apply curtailment to industrial feeder loads",
            "prerequisites": ["G1", "G2"],
            "allowed_actions": [
                "curtail_load factory_load 100",
                "disconnect_substation factory_load",
                "inspect_load factory_load",
                "surge_factory_load factory_load 250",
            ],
            "target": {"entity_id": "factory_load", "prop": "curtail_state", "value": "CURTAILED"},
        },
        {
            "goal_id": "G4",
            "title": "Synchronize Solar PV Inverter Grid-Tie",
            "description": "Synchronize solar inverter phase to GRID_TIE mode",
            "prerequisites": ["G2", "G3"],
            "allowed_actions": [
                "sync_inverter solar_pv GRID_TIE",
                "check_inverter_harmonics solar_pv",
                "poll_solar_pv solar_pv",
                "overload_inverter solar_pv 300",
            ],
            "target": {"entity_id": "solar_pv", "prop": "sync_mode", "value": "GRID_TIE"},
        },
        {
            "goal_id": "G5",
            "title": "Lock Hospital Power to Dual-Redundant Feeder",
            "description": "Transfer critical hospital ward to DUAL_REDUNDANT feeder bus",
            "prerequisites": ["G3", "G4"],
            "allowed_actions": [
                "lock_feeder hospital_ward DUAL_REDUNDANT",
                "audit_hospital hospital_ward",
                "inspect_feeder hospital_ward",
                "shed_hospital_feeder hospital_ward",
            ],
            "target": {"entity_id": "hospital_ward", "prop": "feeder", "value": "DUAL_REDUNDANT"},
        },
        {
            "goal_id": "G6",
            "title": "Trim Microgrid Power Factor",
            "description": "Adjust capacitor bank power factor trim to 0.98",
            "prerequisites": ["G4", "G5"],
            "allowed_actions": [
                "trim_power_factor grid_controller 0.98",
                "measure_frequency grid_controller",
                "poll_power_factor grid_controller",
                "detune_capacitors grid_controller 0.70",
            ],
            "target": {"entity_id": "grid_controller", "prop": "power_factor", "value": 0.98},
        },
        {
            "goal_id": "G7",
            "title": "Arm Islanding Substation Breaker",
            "description": "Arm high-speed islanding breaker in case of grid detachment",
            "prerequisites": ["G5", "G6"],
            "allowed_actions": [
                "arm_breaker grid_controller ARMED",
                "poll_breaker_status grid_controller",
                "inspect_switchgear grid_controller",
                "trip_breaker grid_controller",
            ],
            "target": {"entity_id": "grid_controller", "prop": "breaker_state", "value": "ARMED"},
        },
        {
            "goal_id": "G8",
            "title": "Certify Microgrid Power & Frequency Stability",
            "description": "Validate 50.0 Hz frequency balance and certify stability",
            "prerequisites": ["G6", "G7"],
            "allowed_actions": [
                "certify_stability grid_controller",
                "poll_grid grid_controller",
                "audit_telemetry grid_controller",
            ],
            "target": {"entity_id": "grid_controller", "prop": "grid_stable", "value": True},
        },
    ]

    all_actions = [
        "ramp_turbine gas_turbine 140",
        "inspect_turbine gas_turbine",
        "poll_fuel_rate gas_turbine",
        "trip_turbine gas_turbine",
        "set_bess_mode bess_unit DISCHARGE 30",
        "throttle_bess bess_unit 0",
        "inspect_bess bess_unit",
        "deep_discharge_bess bess_unit 120",
        "curtail_load factory_load 100",
        "disconnect_substation factory_load",
        "inspect_load factory_load",
        "surge_factory_load factory_load 250",
        "sync_inverter solar_pv GRID_TIE",
        "check_inverter_harmonics solar_pv",
        "poll_solar_pv solar_pv",
        "overload_inverter solar_pv 300",
        "lock_feeder hospital_ward DUAL_REDUNDANT",
        "audit_hospital hospital_ward",
        "inspect_feeder hospital_ward",
        "shed_hospital_feeder hospital_ward",
        "trim_power_factor grid_controller 0.98",
        "measure_frequency grid_controller",
        "poll_power_factor grid_controller",
        "detune_capacitors grid_controller 0.70",
        "arm_breaker grid_controller ARMED",
        "poll_breaker_status grid_controller",
        "inspect_switchgear grid_controller",
        "trip_breaker grid_controller",
        "certify_stability grid_controller",
        "poll_grid grid_controller",
        "audit_telemetry grid_controller",
    ]

    return {
        "case_id": case_id,
        "domain": "industrial_microgrid",
        "title": f"High-Stress Industrial Microgrid Dispatch - Mission {case_num}",
        "mission_description": "Balance dynamic industrial generation and curtailable loads, preserve hospital feeder redundancy, and certify grid stability across long horizon (T=150).",
        "nominal_constants": {},
        "initial_entities": initial_entities,
        "scheduled_events": scheduled_events,
        "subgoals": subgoals,
        "all_actions": all_actions,
        "max_turns": 150,
    }


def build_stress_case_domain_c(case_num: int) -> Dict[str, Any]:
    """Build Domain C: Multi-Hub Fleet Supply Chain stress case (K=8, 4-6 actions/phase)."""
    case_id = f"MN018-STRESS-CASE-{case_num:03d}"
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
            "rate_of_decay": {"battery_percent": -0.15},
        },
        "drone_beta_1": {
            "entity_id": "drone_beta_1",
            "entity_type": "drone",
            "version": 1,
            "properties": {
                "payload_units": 0,
                "max_capacity": 5,
                "battery_percent": 92.0,
                "location": "hub_beta",
                "route_status": "IDLE",
            },
            "rate_of_decay": {"battery_percent": -0.15},
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
            "event_name": "corridor_headwind_squall",
            "entity_id": "drone_alpha_1",
            "updates": {"battery_percent": 78.0},
        },
        {
            "trigger_tick": 35,
            "event_name": "hub_beta_approach_congestion",
            "entity_id": "hub_beta",
            "updates": {"dock_status": "CONGESTED"},
        },
        {
            "trigger_tick": 58,
            "event_name": "radar_transponder_drift",
            "entity_id": "hub_gamma",
            "updates": {"dock_status": "CALIBRATING"},
        },
        {
            "trigger_tick": 82,
            "event_name": "drone_beta_battery_throttle",
            "entity_id": "drone_beta_1",
            "updates": {"battery_percent": 68.0},
        },
        {
            "trigger_tick": 112,
            "event_name": "hub_beta_congestion_cleared",
            "entity_id": "hub_beta",
            "updates": {"dock_status": "CLEAR"},
        },
        {
            "trigger_tick": 138,
            "event_name": "corridor_airspace_all_clear",
            "entity_id": "hub_gamma",
            "updates": {"dock_status": "CLEAR"},
        },
    ]

    subgoals = [
        {
            "goal_id": "G1",
            "title": "Load Critical Medical Payload at Hub Alpha",
            "description": "Load 4 inventory units into Drone Alpha 1 from Hub Alpha",
            "prerequisites": [],
            "allowed_actions": [
                "load_payload hub_alpha drone_alpha_1 4",
                "inspect_drone drone_alpha_1",
                "poll_hub_inventory hub_alpha",
                "dump_untracked_inventory drone_alpha_1 3",
            ],
            "target": {"entity_id": "drone_alpha_1", "prop": "payload_units", "value": 4},
        },
        {
            "goal_id": "G2",
            "title": "Dispatch Drone Alpha 1 to Hub Beta",
            "description": "Execute flight transit of Drone Alpha 1 along corridor to Hub Beta",
            "prerequisites": ["G1"],
            "allowed_actions": [
                "dispatch_flight drone_alpha_1 hub_beta",
                "hold_position drone_alpha_1",
                "check_weather drone_alpha_1",
                "force_drain_battery drone_alpha_1 100",
            ],
            "target": {"entity_id": "drone_alpha_1", "prop": "location", "value": "hub_beta"},
        },
        {
            "goal_id": "G3",
            "title": "Unload Payload at Hub Beta",
            "description": "Unload 4 units into Hub Beta inventory, maintaining total conservation",
            "prerequisites": ["G2"],
            "allowed_actions": [
                "unload_payload drone_alpha_1 hub_beta 4",
                "inspect_hub hub_beta",
                "inspect_drone drone_alpha_1",
                "dump_untracked_inventory drone_alpha_1 2",
            ],
            "target": {"entity_id": "drone_alpha_1", "prop": "payload_units", "value": 0},
        },
        {
            "goal_id": "G4",
            "title": "Dock Drone Alpha 1 for Rapid Recharging",
            "description": "Route Drone Alpha 1 to high-speed charging pad",
            "prerequisites": ["G3"],
            "allowed_actions": [
                "dock_recharge drone_alpha_1 hub_beta",
                "status_check drone_alpha_1",
                "poll_charger_bay hub_beta",
                "overload_drone drone_alpha_1 8",
            ],
            "target": {"entity_id": "drone_alpha_1", "prop": "route_status", "value": "RECHARGING"},
        },
        {
            "goal_id": "G5",
            "title": "Cross-Load Payload to Drone Beta 1 at Hub Beta",
            "description": "Load 3 inventory units from Hub Beta into Drone Beta 1",
            "prerequisites": ["G3", "G4"],
            "allowed_actions": [
                "load_payload hub_beta drone_beta_1 3",
                "inspect_drone drone_beta_1",
                "poll_hub_inventory hub_beta",
                "overload_drone drone_beta_1 10",
            ],
            "target": {"entity_id": "drone_beta_1", "prop": "payload_units", "value": 3},
        },
        {
            "goal_id": "G6",
            "title": "Dispatch Drone Beta 1 to Hub Gamma",
            "description": "Execute flight dispatch of Drone Beta 1 to Hub Gamma",
            "prerequisites": ["G5"],
            "allowed_actions": [
                "dispatch_flight drone_beta_1 hub_gamma",
                "hold_position drone_beta_1",
                "scan_radar_corridor fleet_coordinator",
                "force_drain_battery drone_beta_1 100",
            ],
            "target": {"entity_id": "drone_beta_1", "prop": "location", "value": "hub_gamma"},
        },
        {
            "goal_id": "G7",
            "title": "Unload Payload at Hub Gamma",
            "description": "Unload 3 units into Hub Gamma inventory",
            "prerequisites": ["G6"],
            "allowed_actions": [
                "unload_payload drone_beta_1 hub_gamma 3",
                "inspect_hub hub_gamma",
                "inspect_drone drone_beta_1",
                "dump_untracked_inventory drone_beta_1 1",
            ],
            "target": {"entity_id": "drone_beta_1", "prop": "payload_units", "value": 0},
        },
        {
            "goal_id": "G8",
            "title": "Certify Global Fleet Manifest & Inventory Balance",
            "description": "Perform multi-hub inventory reconciliation and certify fleet state",
            "prerequisites": ["G4", "G7"],
            "allowed_actions": [
                "certify_fleet fleet_coordinator",
                "audit_inventory fleet_coordinator",
                "poll_telemetry fleet_coordinator",
            ],
            "target": {"entity_id": "fleet_coordinator", "prop": "mission_certified", "value": True},
        },
    ]

    all_actions = [
        "load_payload hub_alpha drone_alpha_1 4",
        "inspect_drone drone_alpha_1",
        "poll_hub_inventory hub_alpha",
        "dump_untracked_inventory drone_alpha_1 3",
        "dispatch_flight drone_alpha_1 hub_beta",
        "hold_position drone_alpha_1",
        "check_weather drone_alpha_1",
        "force_drain_battery drone_alpha_1 100",
        "unload_payload drone_alpha_1 hub_beta 4",
        "inspect_hub hub_beta",
        "dump_untracked_inventory drone_alpha_1 2",
        "dock_recharge drone_alpha_1 hub_beta",
        "status_check drone_alpha_1",
        "poll_charger_bay hub_beta",
        "overload_drone drone_alpha_1 8",
        "load_payload hub_beta drone_beta_1 3",
        "inspect_drone drone_beta_1",
        "poll_hub_inventory hub_beta",
        "overload_drone drone_beta_1 10",
        "dispatch_flight drone_beta_1 hub_gamma",
        "hold_position drone_beta_1",
        "scan_radar_corridor fleet_coordinator",
        "force_drain_battery drone_beta_1 100",
        "unload_payload drone_beta_1 hub_gamma 3",
        "inspect_hub hub_gamma",
        "dump_untracked_inventory drone_beta_1 1",
        "certify_fleet fleet_coordinator",
        "audit_inventory fleet_coordinator",
        "poll_telemetry fleet_coordinator",
    ]

    return {
        "case_id": case_id,
        "domain": "fleet_supply_chain",
        "title": f"High-Stress Autonomous Fleet Supply Chain - Mission {case_num}",
        "mission_description": "Coordinate multi-hub payload transfers across 3 hubs, preserve total inventory conservation, and manage corridor congestion (T=150).",
        "nominal_constants": {"nominal_total_inventory": nominal_inventory},
        "initial_entities": initial_entities,
        "scheduled_events": scheduled_events,
        "subgoals": subgoals,
        "all_actions": all_actions,
        "max_turns": 150,
    }


def main() -> None:
    cases: List[Dict[str, Any]] = []

    # Domain A: 10 stress cases (1-10)
    for i in range(1, 11):
        cases.append(build_stress_case_domain_a(i))

    # Domain B: 10 stress cases (11-20)
    for i in range(11, 21):
        cases.append(build_stress_case_domain_b(i))

    # Domain C: 10 stress cases (21-30)
    for i in range(21, 31):
        cases.append(build_stress_case_domain_c(i))

    out_dir = Path(__file__).resolve().parent.parent / "definition" / "corpus-v2-stress"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "cases.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)

    print(f"Generated {len(cases)} stress cases into {out_file}")


if __name__ == "__main__":
    main()
