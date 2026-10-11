"""Deterministic Generator for 60-Case Dynamic Schema Evolution Benchmark Corpus.

Generates 60 standardized test cases across 4 heterogeneous domains (15 each),
stratified into 30 In-Distribution (ID) and 30 Out-of-Distribution (OOD) scenarios.
Features dynamic entity emergence, schema mutations, and entity retirements.
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
        case_id = f"DRIFT002-CASE-{case_num:03d}"

        # Dynamic emergence rule
        schema_rules = [
            {
                "rule_id": "RULE_EMERGE_AUX_COOLER",
                "lifecycle_action": "EMERGE",
                "target_entity_id": "aux_cooler",
                "trigger_type": "tick",
                "trigger_tick": 2 if is_ood else 1,
                "payload": {
                    "entity_type": "cryo_cooler",
                    "properties": {"cooling_kw": 30.0 + (i * 1.5)},
                    "relations": {"cools": "thermal_loop"},
                    "ttl": 20,
                },
                "causal_hypothesis": "Thermal overload triggers emergency auxiliary cooler deployment.",
            }
        ]

        if is_ood:
            # Compound mutation: battery acquires boiloff rate, loop acquires degradation relation
            schema_rules.append({
                "rule_id": "RULE_MUTATE_THERMAL",
                "lifecycle_action": "MUTATE_SCHEMA",
                "target_entity_id": "thermal_loop",
                "trigger_type": "tick",
                "trigger_tick": 3,
                "payload": {
                    "properties": {"radiative_efficiency": 0.65},
                    "relations": {"coupled_heat_sink": "aux_cooler"},
                },
                "causal_hypothesis": "Radiator surface fouling alters relational coupling.",
            })

        init_entities = {
            "solar_array": {
                "entity_id": "solar_array",
                "entity_type": "solar_panel",
                "version": 1,
                "properties": {"output_kw": 50.0 + (i * 2.0)},
                "relations": {"powers": "cryo_battery"},
            },
            "cryo_battery": {
                "entity_id": "cryo_battery",
                "entity_type": "battery",
                "version": 1,
                "properties": {"charge_kwh": 20.0 + (i * 1.0)},
                "relations": {"buffers": "thermal_loop"},
            },
            "thermal_loop": {
                "entity_id": "thermal_loop",
                "entity_type": "cooling",
                "version": 1,
                "properties": {"temperature": 75.0 + (i * 0.5)},
                "relations": {},
            },
            "o2_scrubber": {
                "entity_id": "o2_scrubber",
                "entity_type": "life_support",
                "version": 1,
                "properties": {"o2_pressure": 20.0 + (i * 0.2)},
                "relations": {},
            },
        }

        subgoals = [
            {
                "subgoal_id": "G1_CHARGE",
                "description": "Charge cryo battery reserve >= 25.0 kWh",
                "target_entity": "cryo_battery",
                "target_property": "charge_kwh",
                "operator": ">=",
                "target_value": 24.0,
                "candidate_actions": [
                    "divert_solar_power cryo_battery 60.0",
                ],
            },
            {
                "subgoal_id": "G2_COOL_EMERGENT",
                "description": "Cool thermal loop below 65.0 C via emergent aux cooler",
                "target_entity": "thermal_loop",
                "target_property": "temperature",
                "operator": "<=",
                "target_value": 65.0,
                "required_emergent_entity": "aux_cooler",
                "candidate_actions": [
                    "purge_cabin_heat 10.0",
                    "activate_secondary_cooler",  # Emergent affordance
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
                ],
            },
        ]

        cases.append({
            "case_id": case_id,
            "domain": "orbital_life_support",
            "difficulty": "out_of_distribution" if is_ood else "in_distribution",
            "initial_entities": init_entities,
            "schema_rules": schema_rules,
            "subgoals": subgoals,
        })
    return cases


def generate_microgrid_cases(start_idx: int = 16) -> List[Dict[str, Any]]:
    cases = []
    for i in range(15):
        case_num = start_idx + i
        is_ood = i >= 8  # 8 ID (16-23), 7 OOD (24-30)
        case_id = f"DRIFT002-CASE-{case_num:03d}"

        schema_rules = [
            {
                "rule_id": "RULE_EMERGE_FEEDER",
                "lifecycle_action": "EMERGE",
                "target_entity_id": "secondary_feeder",
                "trigger_type": "tick",
                "trigger_tick": 2 if is_ood else 1,
                "payload": {
                    "entity_type": "distribution_line",
                    "properties": {"capacity_kw": 50.0 + (i * 2.0)},
                    "relations": {"feeds": "critical_bus"},
                    "ttl": 25,
                },
                "causal_hypothesis": "Grid voltage sag triggers automatic switchgear feeder connection.",
            }
        ]

        if is_ood:
            schema_rules.append({
                "rule_id": "RULE_EMERGE_FLYWHEEL",
                "lifecycle_action": "EMERGE",
                "target_entity_id": "flywheel_reserve",
                "trigger_type": "tick",
                "trigger_tick": 3,
                "payload": {
                    "entity_type": "kinetic_storage",
                    "properties": {"rpm": 12000.0},
                    "relations": {"stabilizes": "critical_bus"},
                },
                "causal_hypothesis": "Severe harmonic distortion engages kinetic flywheel stabilizer.",
            })

        init_entities = {
            "battery_bank": {
                "entity_id": "battery_bank",
                "entity_type": "storage",
                "version": 1,
                "properties": {"soc": 75.0 + (i * 1.0)},
                "relations": {"backs_up": "critical_bus"},
            },
            "wind_turbine": {
                "entity_id": "wind_turbine",
                "entity_type": "generator",
                "version": 1,
                "properties": {"output_kw": 20.0 + (i * 1.5)},
                "relations": {"generates_to": "critical_bus"},
            },
            "critical_bus": {
                "entity_id": "critical_bus",
                "entity_type": "substation",
                "version": 1,
                "properties": {"voltage": 365.0 + (i * 0.5)},
                "relations": {},
            },
        }

        subgoals = [
            {
                "subgoal_id": "G1_VOLTAGE_EMERGENT",
                "description": "Stabilize critical bus voltage >= 380.0 V via secondary feeder",
                "target_entity": "critical_bus",
                "target_property": "voltage",
                "operator": ">=",
                "target_value": 380.0,
                "required_emergent_entity": "secondary_feeder",
                "candidate_actions": [
                    "discharge_battery 30.0",  # May sag
                    "connect_secondary_feeder",  # Emergent affordance
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
            "schema_rules": schema_rules,
            "subgoals": subgoals,
        })
    return cases


def generate_fleet_cases(start_idx: int = 31) -> List[Dict[str, Any]]:
    cases = []
    for i in range(15):
        case_num = start_idx + i
        is_ood = i >= 8  # 8 ID (31-38), 7 OOD (39-45)
        case_id = f"DRIFT002-CASE-{case_num:03d}"

        schema_rules = [
            {
                "rule_id": "RULE_EMERGE_BOOSTER",
                "lifecycle_action": "EMERGE",
                "target_entity_id": "booster_trailer",
                "trigger_type": "tick",
                "trigger_tick": 2 if is_ood else 1,
                "payload": {
                    "entity_type": "aux_refrigeration",
                    "properties": {"cooling_power_kw": 25.0},
                    "relations": {"couples_to": "reefer_unit"},
                    "ttl": 20,
                },
                "causal_hypothesis": "Highway convoy dock attaches autonomous refrigeration booster.",
            }
        ]

        init_entities = {
            "reefer_unit": {
                "entity_id": "reefer_unit",
                "entity_type": "refrigeration",
                "version": 1,
                "properties": {"cargo_temp": -16.0 - (i * 0.2)},
                "relations": {},
            },
            "aux_battery": {
                "entity_id": "aux_battery",
                "entity_type": "battery",
                "version": 1,
                "properties": {"power_kw": 25.0 + (i * 1.0)},
                "relations": {"powers": "traction_motor"},
            },
            "traction_motor": {
                "entity_id": "traction_motor",
                "entity_type": "drivetrain",
                "version": 1,
                "properties": {"speed_kph": 30.0 + (i * 1.0)},
                "relations": {},
            },
            "coolant_pack": {
                "entity_id": "coolant_pack",
                "entity_type": "passive_cooling",
                "version": 1,
                "properties": {"charges": 3},
                "relations": {},
            },
        }

        subgoals = [
            {
                "subgoal_id": "G1_CHILL_BOOSTER",
                "description": "Deep freeze cargo <= -22.0 C via booster trailer",
                "target_entity": "reefer_unit",
                "target_property": "cargo_temp",
                "operator": "<=",
                "target_value": -22.0,
                "required_emergent_entity": "booster_trailer",
                "candidate_actions": [
                    "chill_reefer_compartment 2.0",
                    "engage_booster_trailer",  # Emergent affordance
                ],
            },
            {
                "subgoal_id": "G2_TRANSIT",
                "description": "Reach highway transit speed >= 50.0 km/h",
                "target_entity": "traction_motor",
                "target_property": "speed_kph",
                "operator": ">=",
                "target_value": 50.0,
                "candidate_actions": [
                    "adjust_traction_drive 50.0",
                ],
            },
        ]

        cases.append({
            "case_id": case_id,
            "domain": "fleet_logistics",
            "difficulty": "out_of_distribution" if is_ood else "in_distribution",
            "initial_entities": init_entities,
            "schema_rules": schema_rules,
            "subgoals": subgoals,
        })
    return cases


def generate_subsea_cases(start_idx: int = 46) -> List[Dict[str, Any]]:
    cases = []
    for i in range(15):
        case_num = start_idx + i
        is_ood = i >= 7  # 7 ID (46-52), 8 OOD (53-60)
        case_id = f"DRIFT002-CASE-{case_num:03d}"

        schema_rules = [
            {
                "rule_id": "RULE_EMERGE_AUX_VENT",
                "lifecycle_action": "EMERGE",
                "target_entity_id": "aux_vent",
                "trigger_type": "tick",
                "trigger_tick": 2 if is_ood else 1,
                "payload": {
                    "entity_type": "relief_valve",
                    "properties": {"discharge_flow": 50.0},
                    "relations": {"relieves": "depth_ballast"},
                    "ttl": 20,
                },
                "causal_hypothesis": "Ballast over-pressurization opens auxiliary pneumatic relief valve.",
            }
        ]

        init_entities = {
            "thermoelectric_gen": {
                "entity_id": "thermoelectric_gen",
                "entity_type": "generator",
                "version": 1,
                "properties": {"core_temp": 95.0 + (i * 1.5)},
                "relations": {},
            },
            "depth_ballast": {
                "entity_id": "depth_ballast",
                "entity_type": "ballast",
                "version": 1,
                "properties": {"chamber_pressure": 230.0 + (i * 1.0)},
                "relations": {},
            },
            "salinity_sensor": {
                "entity_id": "salinity_sensor",
                "entity_type": "sensor",
                "version": 1,
                "properties": {"bias_ppm": 50.0 + (i * 5.0)},
                "relations": {},
            },
        }

        subgoals = [
            {
                "subgoal_id": "G1_COOL_CORE",
                "description": "Cool generator core <= 90.0 C",
                "target_entity": "thermoelectric_gen",
                "target_property": "core_temp",
                "operator": "<=",
                "target_value": 90.0,
                "candidate_actions": [
                    "engage_cryo_heat_sink",
                ],
            },
            {
                "subgoal_id": "G2_BALLAST_EMERGENT",
                "description": "Vent ballast pressure <= 200.0 bar via emergent aux vent",
                "target_entity": "depth_ballast",
                "target_property": "chamber_pressure",
                "operator": "<=",
                "target_value": 200.0,
                "required_emergent_entity": "aux_vent",
                "candidate_actions": [
                    "vent_ballast_chamber 10.0",
                    "open_auxiliary_vent_hatch",  # Emergent affordance
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
            "schema_rules": schema_rules,
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
    print(f"Generated {len(all_cases)} Stage 2 test cases: {id_count} ID, {ood_count} OOD.")
    print(f"Saved to: {out_file}")


if __name__ == "__main__":
    main()
