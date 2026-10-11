"""Standardized Benchmark Corpus v1 for Milestone MN-020 (N=60 Multi-Agent Scenarios)."""
from __future__ import annotations

from typing import Any, Dict, List


def generate_benchmark_corpus(n_per_domain: int = 20) -> List[Dict[str, Any]]:
    """Generate 60 standardized multi-agent benchmark scenarios across 3 domains."""
    cases: List[Dict[str, Any]] = []
    case_idx = 1

    # =========================================================================
    # DOMAIN 1: Collaborative Smart Microgrid Balancing (N=20)
    # =========================================================================
    for i in range(n_per_domain):
        init_entities = {
            "wind_turbine": {
                "entity_type": "generator",
                "properties": {"pitch_deg": 10.0, "output_kw": 85.0},
            },
            "critical_bus": {
                "entity_type": "bus",
                "properties": {"voltage": 354.0},
            },
            "battery_bank": {
                "entity_type": "storage",
                "properties": {"soc": 40.0, "charge_rate": 0.0},
            },
            "industrial_feeder": {
                "entity_type": "feeder",
                "properties": {"load_kw": 80.0},
            },
            "statcom": {
                "entity_type": "compensator",
                "properties": {"is_engaged": False},
            },
        }

        # Agent 1: Regulate battery storage and wind turbine pitch
        subgoals_a1 = [
            {
                "description": "Engage battery bank to absorb excess bus power",
                "target_entity": "battery_bank",
                "target_properties": {"soc": 52.5},
                "target_entities": ["battery_bank", "critical_bus"],
                "candidates": ["charge_battery_storage 25.0"],
            },
            {
                "description": "Feather wind turbine pitch to reduce over-generation",
                "target_entity": "wind_turbine",
                "target_properties": {"pitch_deg": 30.0},
                "target_entities": ["wind_turbine", "critical_bus"],
                "candidates": ["regulate_wind_pitch 30.0", "regulate_wind_pitch 50.0"],
            },
        ]

        # Agent 2: Contested battery discharge or feeder shedding
        subgoals_a2 = [
            {
                "description": "Shed non-critical industrial feeder load",
                "target_entity": "industrial_feeder",
                "target_properties": {"load_kw": 40.0},
                "target_entities": ["battery_bank", "industrial_feeder", "critical_bus"],
                "candidates": ["discharge_battery_storage 30.0", "shed_industrial_feeder 40.0"],
            },
            {
                "description": "Engage static compensator for bus voltage lock",
                "target_entity": "critical_bus",
                "target_properties": {"voltage": 340.0},
                "target_entities": ["statcom", "critical_bus"],
                "candidates": ["engage_static_compensator"],
            },
        ]

        cases.append({
            "case_id": f"MN020-CASE-{case_idx:03d}",
            "domain": "collaborative_microgrid",
            "initial_entities": init_entities,
            "subgoals_agent1": subgoals_a1,
            "subgoals_agent2": subgoals_a2,
        })
        case_idx += 1

    # =========================================================================
    # DOMAIN 2: Concurrent Orbital Maintenance & Docking (N=20)
    # =========================================================================
    for i in range(n_per_domain):
        init_entities = {
            "rcs_thruster": {
                "entity_type": "propulsion",
                "properties": {"fuel_kg": 50.0},
            },
            "docking_adapter": {
                "entity_type": "mechanism",
                "properties": {"alignment_err_deg": 15.0, "is_locked": False},
            },
            "solar_array": {
                "entity_type": "power",
                "properties": {"gimbal_deg": 10.0, "efficiency": 0.70},
            },
            "power_bus": {
                "entity_type": "bus",
                "properties": {"bus_power_kw": 25.0},
            },
            "thermal_radiator": {
                "entity_type": "thermal",
                "properties": {"temp_c": 65.0},
            },
        }

        # Agent 1: Maneuver attitude before locking
        subgoals_a1 = [
            {
                "description": "Fire RCS thruster to eliminate attitude alignment error",
                "target_entity": "docking_adapter",
                "target_properties": {"alignment_err_deg": 0.0},
                "target_entities": ["docking_adapter", "rcs_thruster"],
                "candidates": ["fire_rcs_attitude 30.0", "fire_rcs_attitude 10.0"],
            },
            {
                "description": "Lock docking latch mechanism",
                "target_entity": "docking_adapter",
                "target_properties": {"is_locked": True},
                "target_entities": ["docking_adapter"],
                "candidates": ["lock_docking_latch"],
            },
        ]

        # Agent 2: Align solar gimbal and purge thermal load (competing for docking_adapter)
        subgoals_a2 = [
            {
                "description": "Align solar array gimbal for peak solar collection",
                "target_entity": "solar_array",
                "target_properties": {"gimbal_deg": 45.0},
                "target_entities": ["docking_adapter", "solar_array", "power_bus"],
                "candidates": ["lock_docking_latch", "align_solar_gimbal 45.0"],
            },
            {
                "description": "Purge thermal radiator loop to prevent heat soak",
                "target_entity": "thermal_radiator",
                "target_properties": {"temp_c": 45.0},
                "target_entities": ["thermal_radiator"],
                "candidates": ["purge_coolant_loop 20.0"],
            },
        ]

        cases.append({
            "case_id": f"MN020-CASE-{case_idx:03d}",
            "domain": "concurrent_orbital_maintenance",
            "initial_entities": init_entities,
            "subgoals_agent1": subgoals_a1,
            "subgoals_agent2": subgoals_a2,
        })
        case_idx += 1

    # =========================================================================
    # DOMAIN 3: Joint Fleet Logistics (N=20)
    # =========================================================================
    for i in range(n_per_domain):
        init_entities = {
            "convoy_a": {
                "entity_type": "vehicle",
                "properties": {"dist_km": 0.0, "battery_soc": 80.0},
            },
            "reefer_b": {
                "entity_type": "cargo",
                "properties": {"temp_c": -5.0},
            },
            "charging_hub": {
                "entity_type": "station",
                "properties": {"active_load_kw": 50.0},
            },
        }

        # Agent 1: Reserve fast charger and advance haul convoy
        subgoals_a1 = [
            {
                "description": "Reserve charging hub capacity for fleet turnaround",
                "target_entity": "charging_hub",
                "target_properties": {"active_load_kw": 170.0},
                "target_entities": ["charging_hub"],
                "candidates": ["queue_fast_charger 120.0"],
            },
            {
                "description": "Advance haul convoy along route segment",
                "target_entity": "convoy_a",
                "target_properties": {"dist_km": 30.0},
                "target_entities": ["convoy_a"],
                "candidates": ["route_haul_convoy 30.0"],
            },
        ]

        # Agent 2: Chill reefer cargo and handle secondary chilling cycle
        subgoals_a2 = [
            {
                "description": "Charge reefer auxiliary power at hub or deep freeze cargo",
                "target_entity": "reefer_b",
                "target_properties": {"temp_c": -18.0},
                "target_entities": ["charging_hub", "reefer_b"],
                "candidates": ["queue_fast_charger 120.0", "refrigerate_cargo_bay -18.0"],
            },
            {
                "description": "Deep freeze perishable reefer cargo hold",
                "target_entity": "reefer_b",
                "target_properties": {"temp_c": -18.0},
                "target_entities": ["reefer_b"],
                "candidates": ["refrigerate_cargo_bay -18.0"],
            },
        ]

        cases.append({
            "case_id": f"MN020-CASE-{case_idx:03d}",
            "domain": "joint_fleet_logistics",
            "initial_entities": init_entities,
            "subgoals_agent1": subgoals_a1,
            "subgoals_agent2": subgoals_a2,
        })
        case_idx += 1

    return cases
