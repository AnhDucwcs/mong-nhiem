"""Standardized Benchmark Corpus v1 for Milestone MN-021 (N=80 Federated Scenarios).

Generates 80 standardized multi-agent scenarios across 3 domains:
- Domain A: Martian Biosphere Colony Life Support (N=27: 20 nominal, 7 shocks)
- Domain B: Subsea Hydrothermal Energy Grid (N=27: 20 nominal, 7 shocks)
- Domain C: Orbital Constellation Satellite Relay (N=26: 20 nominal, 6 shocks)
Total: 60 nominal (75.0%), 20 stochastic shocks (25.0%).
"""
from __future__ import annotations

from typing import Any, Dict, List


def generate_benchmark_corpus() -> List[Dict[str, Any]]:
    """Generate the full N=80 benchmark scenario corpus."""
    cases: List[Dict[str, Any]] = []

    # =========================================================================
    # DOMAIN A: Martian Biosphere Colony Life Support (N=27)
    # 20 Nominal Cases, 7 Stochastic Shock Cases
    # =========================================================================
    mb_shock_indices = {5, 9, 13, 17, 21, 24, 27}
    for i in range(1, 28):
        case_id = f"MB-{i:03d}"
        is_shock = i in mb_shock_indices

        initial_entities = {
            "power_grid": {
                "grid_power_available": 60 + (i % 5) * 5,
                "grid_power_consumed": 20,
                "solar_fouling_pct": 10,
            },
            "scrubber_unit": {
                "scrubber_state": "IDLE",
                "o2_level": 20.8,
                "co2_ppm": 520 + (i % 3) * 10,
            },
            "water_loop": {
                "water_line_pressure": 95 + (i % 4) * 5,
                "valve_state": "CLOSED",
                "pump_rpm": 1100,
            },
            "thermal_radiator": {
                "radiator_state": "STOWED",
                "coolant_temp_c": 24,
            },
        }

        agent1_goals = [
            {
                "phase": "STABILIZE_POWER",
                "target_entity": "power_grid",
                "target_state": {"grid_power_available": 75, "solar_fouling_pct": 5},
            },
            {
                "phase": "DEPLOY_RADIATOR",
                "target_entity": "thermal_radiator",
                "target_state": {"radiator_state": "DEPLOYED", "coolant_temp_c": 18},
            },
        ]

        agent2_goals = [
            {
                "phase": "PRESSURIZE_WATER",
                "target_entity": "water_loop",
                "target_state": {"valve_state": "OPEN", "water_line_pressure": 115},
            },
            {
                "phase": "ENGAGE_SCRUBBER",
                "target_entity": "scrubber_unit",
                "target_state": {"scrubber_state": "ACTIVE", "o2_level": 21.5},
            },
        ]

        shock_config = None
        if is_shock:
            shock_type = "dust_squall" if i % 2 == 1 else "scrubber_thermal_trip"
            target = "power_grid" if shock_type == "dust_squall" else "scrubber_unit"
            shock_config = {
                "has_shock": True,
                "trigger_tick": 3,
                "target_entity": target,
                "shock_type": shock_type,
            }
        else:
            shock_config = {"has_shock": False}

        cases.append({
            "case_id": case_id,
            "domain": "martian_biosphere",
            "initial_entities": initial_entities,
            "agent1_goals": agent1_goals,
            "agent2_goals": agent2_goals,
            "shock_config": shock_config,
        })

    # =========================================================================
    # DOMAIN B: Subsea Hydrothermal Energy Grid (N=27)
    # 20 Nominal Cases, 7 Stochastic Shock Cases
    # =========================================================================
    sh_shock_indices = {4, 8, 12, 16, 20, 23, 26}
    for i in range(1, 28):
        case_id = f"SH-{i:03d}"
        is_shock = i in sh_shock_indices

        initial_entities = {
            "turbine_generator": {
                "power_generation_kw": 210,
                "power_load_kw": 150 + (i % 4) * 5,
                "cavitation_index": 1.55,
            },
            "geothermal_core": {
                "core_temp_c": 290 + (i % 5) * 4,
                "loop_pressure_bar": 110,
                "bypass_valve": "CLOSED",
            },
            "cooling_manifold": {
                "cooling_valve_state": "CLOSED",
                "coolant_flow_lpm": 75,
            },
            "battery_subsea": {
                "charge_pct": 78,
                "bus_voltage": 48,
            },
        }

        agent1_goals = [
            {
                "phase": "REGULATE_TURBINE",
                "target_entity": "turbine_generator",
                "target_state": {"power_generation_kw": 230, "cavitation_index": 1.65},
            },
            {
                "phase": "COOL_CORE",
                "target_entity": "geothermal_core",
                "target_state": {"bypass_valve": "OPEN", "core_temp_c": 275},
            },
        ]

        agent2_goals = [
            {
                "phase": "OPEN_COOLING",
                "target_entity": "cooling_manifold",
                "target_state": {"cooling_valve_state": "OPEN", "coolant_flow_lpm": 95},
            },
            {
                "phase": "BALANCE_STORAGE",
                "target_entity": "battery_subsea",
                "target_state": {"charge_pct": 92, "bus_voltage": 50},
            },
        ]

        shock_config = None
        if is_shock:
            shock_type = "geothermal_surge" if i % 2 == 0 else "valve_cavitation_trip"
            target = "geothermal_core" if shock_type == "geothermal_surge" else "cooling_manifold"
            shock_config = {
                "has_shock": True,
                "trigger_tick": 4,
                "target_entity": target,
                "shock_type": shock_type,
            }
        else:
            shock_config = {"has_shock": False}

        cases.append({
            "case_id": case_id,
            "domain": "subsea_hydrothermal",
            "initial_entities": initial_entities,
            "agent1_goals": agent1_goals,
            "agent2_goals": agent2_goals,
            "shock_config": shock_config,
        })

    # =========================================================================
    # DOMAIN C: Orbital Constellation Satellite Relay (N=26)
    # 20 Nominal Cases, 6 Stochastic Shock Cases
    # =========================================================================
    oc_shock_indices = {4, 8, 12, 16, 20, 25}
    for i in range(1, 27):
        case_id = f"OC-{i:03d}"
        is_shock = i in oc_shock_indices

        initial_entities = {
            "power_subsystem": {
                "battery_soc_pct": 75 + (i % 4) * 3,
                "solar_panel_deployed": True,
                "charge_controller_state": "STANDBY",
            },
            "attitude_control": {
                "attitude_error_deg": 0.025,
                "reaction_wheels_rpm": 2400,
                "propellant_kg": 48.0,
            },
            "laser_terminal": {
                "laser_link_state": "STANDBY",
                "data_throughput_gbps": 0,
            },
            "comm_transponder": {
                "transponder_state": "STANDBY",
                "snr_db": 16.0 + (i % 3) * 0.5,
            },
        }

        agent1_goals = [
            {
                "phase": "CHARGE_STABILIZATION",
                "target_entity": "power_subsystem",
                "target_state": {"charge_controller_state": "ACTIVE", "battery_soc_pct": 88},
            },
            {
                "phase": "POINTING_ALIGNMENT",
                "target_entity": "attitude_control",
                "target_state": {"attitude_error_deg": 0.012, "reaction_wheels_rpm": 2200},
            },
        ]

        agent2_goals = [
            {
                "phase": "ESTABLISH_LASER_LINK",
                "target_entity": "laser_terminal",
                "target_state": {"laser_link_state": "ACTIVE", "data_throughput_gbps": 10},
            },
            {
                "phase": "ENABLE_TRANSPONDER",
                "target_entity": "comm_transponder",
                "target_state": {"transponder_state": "ACTIVE", "snr_db": 19.5},
            },
        ]

        shock_config = None
        if is_shock:
            shock_type = "solar_flare_tripping" if i % 2 == 0 else "gyro_attitude_drift"
            target = "power_subsystem" if shock_type == "solar_flare_tripping" else "attitude_control"
            shock_config = {
                "has_shock": True,
                "trigger_tick": 3,
                "target_entity": target,
                "shock_type": shock_type,
            }
        else:
            shock_config = {"has_shock": False}

        cases.append({
            "case_id": case_id,
            "domain": "orbital_constellation",
            "initial_entities": initial_entities,
            "agent1_goals": agent1_goals,
            "agent2_goals": agent2_goals,
            "shock_config": shock_config,
        })

    return cases
