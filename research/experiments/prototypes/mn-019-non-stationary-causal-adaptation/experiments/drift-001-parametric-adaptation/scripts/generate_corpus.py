"""Deterministic Generator for 60-Case Parametric Drift Benchmark Corpus.

Generates 60 standardized test cases across 4 heterogeneous domains (15 each),
stratified into 30 In-Distribution (ID) and 30 Out-of-Distribution (OOD) scenarios.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List


def generate_orbital_cases(start_idx: int = 1) -> List[Dict[str, Any]]:
    cases = []
    for i in range(15):
        case_num = start_idx + i
        is_ood = i >= 7  # 7 ID (1-7), 8 OOD (8-15)
        case_id = f"DRIFT001-CASE-{case_num:03d}"

        # Parametric drift settings
        drift_type = "coupled_exponential" if is_ood else ("linear_decay" if i % 2 == 0 else "step_shock")
        rate = 0.04 + (i * 0.005)
        start_tick = 3 if is_ood else 5

        drift_rules = [
            {
                "target_entity_id": "solar_array",
                "property_name": "efficiency",
                "drift_type": "exponential_decay" if is_ood else "linear_decay",
                "rate": rate,
                "start_tick": start_tick,
                "floor_value": 0.2,
                "coupled_entities": ["cryo_battery"] if is_ood else [],
            },
            {
                "target_entity_id": "thermal_loop",
                "property_name": "coolant_flow",
                "drift_type": "step_shock" if is_ood else "linear_decay",
                "rate": 0.5 if is_ood else 0.7,
                "start_tick": 2 if is_ood else 6,
                "floor_value": 0.3,
                "coupled_entities": [],
            }
        ]

        # Initial entities
        init_entities = {
            "solar_array": {
                "entity_id": "solar_array",
                "entity_type": "solar_panel",
                "version": 1,
                "properties": {"output_kw": 50.0 + (i * 2.0)},
            },
            "cryo_battery": {
                "entity_id": "cryo_battery",
                "entity_type": "battery",
                "version": 1,
                "properties": {"charge_kwh": 10.0 + (i * 1.0)},
            },
            "thermal_loop": {
                "entity_id": "thermal_loop",
                "entity_type": "cooling",
                "version": 1,
                "properties": {"temperature": 68.0 + (i * 1.5)},
            },
            "o2_scrubber": {
                "entity_id": "o2_scrubber",
                "entity_type": "life_support",
                "version": 1,
                "properties": {"o2_pressure": 19.5 + (i * 0.2)},
            },
        }

        # Sub-goals
        subgoals = [
            {
                "subgoal_id": "G1_CHARGE",
                "description": "Charge cryo battery to safe reserve",
                "target_entity": "cryo_battery",
                "target_property": "charge_kwh",
                "operator": ">=",
                "target_value": round(init_entities["cryo_battery"]["properties"]["charge_kwh"] + 3.0, 1),
                "candidate_actions": [
                    "divert_solar_power cryo_battery 60.0",
                    "divert_solar_power cryo_battery 100.0",  # Inviable under drift trap
                ],
            },
            {
                "subgoal_id": "G2_COOL",
                "description": "Stabilize thermal loop temperature below 60.0 C",
                "target_entity": "thermal_loop",
                "target_property": "temperature",
                "operator": "<=",
                "target_value": 60.0,
                "candidate_actions": [
                    "purge_cabin_heat 40.0",  # Trap under coolant drift
                    "engage_auxiliary_cryo_pump",  # Safe compensatory
                ],
            },
            {
                "subgoal_id": "G3_O2",
                "description": "Maintain cabin O2 pressure >= 21.0 kPa",
                "target_entity": "o2_scrubber",
                "target_property": "o2_pressure",
                "operator": ">=",
                "target_value": 21.0,
                "candidate_actions": [
                    "boost_scrubber_oxygen 5.0",
                    "boost_scrubber_oxygen 15.0",  # High-draw trap
                ],
            },
        ]

        cases.append({
            "case_id": case_id,
            "domain": "orbital_life_support",
            "difficulty": "out_of_distribution" if is_ood else "in_distribution",
            "initial_entities": init_entities,
            "drift_rules": drift_rules,
            "nominal_constants": {},
            "subgoals": subgoals,
        })
    return cases


def generate_microgrid_cases(start_idx: int = 16) -> List[Dict[str, Any]]:
    cases = []
    for i in range(15):
        case_num = start_idx + i
        is_ood = i >= 8  # 8 ID (16-23), 7 OOD (24-30)
        case_id = f"DRIFT001-CASE-{case_num:03d}"

        drift_rules = [
            {
                "target_entity_id": "battery_bank",
                "property_name": "internal_resistance",
                "drift_type": "exponential_decay" if is_ood else "linear_decay",
                "rate": 0.06 + (i * 0.005),
                "start_tick": 2 if is_ood else 4,
                "coupled_entities": ["critical_bus"] if is_ood else [],
            },
            {
                "target_entity_id": "wind_turbine",
                "property_name": "shear_stability",
                "drift_type": "harmonic_oscillation" if is_ood else "linear_decay",
                "rate": 0.03 if is_ood else 0.005,
                "start_tick": 1,
                "amplitude": 0.3 if is_ood else 0.0,
                "frequency": 0.2,
                "coupled_entities": [],
            }
        ]

        init_entities = {
            "battery_bank": {
                "entity_id": "battery_bank",
                "entity_type": "storage",
                "version": 1,
                "properties": {"soc": 75.0 + (i * 1.0)},
            },
            "wind_turbine": {
                "entity_id": "wind_turbine",
                "entity_type": "generator",
                "version": 1,
                "properties": {"output_kw": 20.0 + (i * 1.5)},
            },
            "critical_bus": {
                "entity_id": "critical_bus",
                "entity_type": "substation",
                "version": 1,
                "properties": {"voltage": 370.0 + (i * 0.8)},
            },
        }

        subgoals = [
            {
                "subgoal_id": "G1_VOLTAGE",
                "description": "Regulate critical bus voltage to 380.0 V",
                "target_entity": "critical_bus",
                "target_property": "voltage",
                "operator": ">=",
                "target_value": 380.0,
                "candidate_actions": [
                    "discharge_battery 30.0",  # High-draw trap
                    "engage_static_compensator",  # Compensatory
                    "regulate_wind_pitch 15.0",
                ],
            },
            {
                "subgoal_id": "G2_WIND_GEN",
                "description": "Achieve wind turbine output >= 35.0 kW",
                "target_entity": "wind_turbine",
                "target_property": "output_kw",
                "operator": ">=",
                "target_value": 35.0,
                "candidate_actions": [
                    "regulate_wind_pitch 20.0",
                    "regulate_wind_pitch 30.0",
                ],
            },
        ]

        cases.append({
            "case_id": case_id,
            "domain": "smart_microgrid",
            "difficulty": "out_of_distribution" if is_ood else "in_distribution",
            "initial_entities": init_entities,
            "drift_rules": drift_rules,
            "nominal_constants": {},
            "subgoals": subgoals,
        })
    return cases


def generate_fleet_cases(start_idx: int = 31) -> List[Dict[str, Any]]:
    cases = []
    for i in range(15):
        case_num = start_idx + i
        is_ood = i >= 8  # 8 ID (31-38), 7 OOD (39-45)
        case_id = f"DRIFT001-CASE-{case_num:03d}"

        drift_rules = [
            {
                "target_entity_id": "reefer_unit",
                "property_name": "insulation_r_value",
                "drift_type": "exponential_decay" if is_ood else "linear_decay",
                "rate": 0.05 + (i * 0.004),
                "start_tick": 2 if is_ood else 4,
                "floor_value": 0.25,
                "coupled_entities": ["aux_battery"] if is_ood else [],
            },
            {
                "target_entity_id": "traction_motor",
                "property_name": "bearing_friction",
                "drift_type": "step_shock" if is_ood else "linear_decay",
                "rate": 1.7 if is_ood else 1.3,
                "start_tick": 3,
                "coupled_entities": [],
            }
        ]

        init_entities = {
            "reefer_unit": {
                "entity_id": "reefer_unit",
                "entity_type": "refrigeration",
                "version": 1,
                "properties": {"cargo_temp": -16.0 - (i * 0.2)},
            },
            "aux_battery": {
                "entity_id": "aux_battery",
                "entity_type": "battery",
                "version": 1,
                "properties": {"power_kw": 25.0 + (i * 1.0)},
            },
            "traction_motor": {
                "entity_id": "traction_motor",
                "entity_type": "drivetrain",
                "version": 1,
                "properties": {"speed_kph": 30.0 + (i * 1.0)},
            },
            "coolant_pack": {
                "entity_id": "coolant_pack",
                "entity_type": "passive_cooling",
                "version": 1,
                "properties": {"charges": 3},
            },
        }

        subgoals = [
            {
                "subgoal_id": "G1_CHILL",
                "description": "Chill reefer cargo temperature <= -20.0 C",
                "target_entity": "reefer_unit",
                "target_property": "cargo_temp",
                "operator": "<=",
                "target_value": -20.0,
                "candidate_actions": [
                    "chill_reefer_compartment 5.0",
                    "activate_emergency_cooling_pack",  # Compensatory
                ],
            },
            {
                "subgoal_id": "G2_TRANSIT",
                "description": "Reach transit speed >= 50.0 km/h without depleting power",
                "target_entity": "traction_motor",
                "target_property": "speed_kph",
                "operator": ">=",
                "target_value": 50.0,
                "candidate_actions": [
                    "adjust_traction_drive 50.0",
                    "adjust_traction_drive 80.0",  # High-friction trap
                ],
            },
        ]

        cases.append({
            "case_id": case_id,
            "domain": "fleet_logistics",
            "difficulty": "out_of_distribution" if is_ood else "in_distribution",
            "initial_entities": init_entities,
            "drift_rules": drift_rules,
            "nominal_constants": {},
            "subgoals": subgoals,
        })
    return cases


def generate_subsea_cases(start_idx: int = 46) -> List[Dict[str, Any]]:
    cases = []
    for i in range(15):
        case_num = start_idx + i
        is_ood = i >= 7  # 7 ID (46-52), 8 OOD (53-60)
        case_id = f"DRIFT001-CASE-{case_num:03d}"

        drift_rules = [
            {
                "target_entity_id": "thermoelectric_gen",
                "property_name": "heat_sink_fouling",
                "drift_type": "exponential_decay" if is_ood else "linear_decay",
                "rate": 0.05 + (i * 0.005),
                "start_tick": 2 if is_ood else 5,
                "floor_value": 0.3,
                "coupled_entities": ["depth_ballast"] if is_ood else [],
            },
            {
                "target_entity_id": "depth_ballast",
                "property_name": "chamber_pressure",
                "drift_type": "step_shock" if is_ood else "linear_decay",
                "rate": 1.5 if is_ood else 1.2,
                "start_tick": 3,
                "coupled_entities": [],
            }
        ]

        init_entities = {
            "thermoelectric_gen": {
                "entity_id": "thermoelectric_gen",
                "entity_type": "generator",
                "version": 1,
                "properties": {"core_temp": 95.0 + (i * 1.5)},
            },
            "depth_ballast": {
                "entity_id": "depth_ballast",
                "entity_type": "ballast",
                "version": 1,
                "properties": {"chamber_pressure": 220.0 + (i * 2.0)},
            },
            "salinity_sensor": {
                "entity_id": "salinity_sensor",
                "entity_type": "sensor",
                "version": 1,
                "properties": {"bias_ppm": 50.0 + (i * 5.0)},
            },
        }

        subgoals = [
            {
                "subgoal_id": "G1_COOL_CORE",
                "description": "Cool thermoelectric core <= 90.0 C",
                "target_entity": "thermoelectric_gen",
                "target_property": "core_temp",
                "operator": "<=",
                "target_value": 90.0,
                "candidate_actions": [
                    "throttle_hydrothermal_intake 50.0",  # Thermal runaway trap under fouling
                    "engage_cryo_heat_sink",  # Compensatory
                ],
            },
            {
                "subgoal_id": "G2_BALLAST",
                "description": "Vent ballast chamber pressure <= 200.0 bar",
                "target_entity": "depth_ballast",
                "target_property": "chamber_pressure",
                "operator": "<=",
                "target_value": 200.0,
                "candidate_actions": [
                    "vent_ballast_chamber 30.0",
                    "vent_ballast_chamber 20.0",
                ],
            },
            {
                "subgoal_id": "G3_CALIBRATE",
                "description": "Flush salinity sensor to zero bias",
                "target_entity": "salinity_sensor",
                "target_property": "bias_ppm",
                "operator": "==",
                "target_value": 0.0,
                "candidate_actions": [
                    "flush_salinity_sensor",
                ],
            },
        ]

        cases.append({
            "case_id": case_id,
            "domain": "subsea_hydrothermal",
            "difficulty": "out_of_distribution" if is_ood else "in_distribution",
            "initial_entities": init_entities,
            "drift_rules": drift_rules,
            "nominal_constants": {},
            "subgoals": subgoals,
        })
    return cases


def main():
    all_cases = []
    all_cases.extend(generate_orbital_cases(start_idx=1))
    all_cases.extend(generate_microgrid_cases(start_idx=16))
    all_cases.extend(generate_fleet_cases(start_idx=31))
    all_cases.extend(generate_subsea_cases(start_idx=46))

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "definition"))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "cases.json")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_cases, f, indent=2)

    id_count = sum(1 for c in all_cases if c["difficulty"] == "in_distribution")
    ood_count = sum(1 for c in all_cases if c["difficulty"] == "out_of_distribution")
    print(f"Generated {len(all_cases)} test cases: {id_count} ID, {ood_count} OOD.")
    print(f"Saved to: {out_file}")


if __name__ == "__main__":
    main()
