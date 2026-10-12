"""High-Difficulty Stress Benchmark Corpus v2 for Milestone MN-021 (N=15 Compound Shock Scenarios).

Evaluates federated multi-agent causal coordination under compound, cascading exogenous shocks:
- Domain A: Martian Biosphere Colony Life Support (N=5: MB-STRESS-001 to 005)
  Compound Shocks: Dust Squall (t=2) + Scrubber Thermal Trip (t=5).
- Domain B: Subsea Hydrothermal Energy Grid (N=5: SH-STRESS-001 to 005)
  Compound Shocks: Valve Cavitation Trip (t=2) + Geothermal Plume Surge (t=5).
- Domain C: Orbital Constellation Satellite Relay (N=5: OC-STRESS-001 to 005)
  Compound Shocks: Solar Flare Disconnect (t=2) + Gyro Attitude Drift (t=5).
Total: 15 Compound Shock Scenarios (100% Black Swan Stress Load).
"""
from __future__ import annotations

from typing import Any, Dict, List


def generate_stress_benchmark_corpus() -> List[Dict[str, Any]]:
    """Generate 15 high-difficulty compound shock scenarios."""
    cases: List[Dict[str, Any]] = []

    # =========================================================================
    # DOMAIN A: Martian Biosphere Colony Life Support (N=5)
    # =========================================================================
    for i in range(1, 6):
        case_id = f"MB-STRESS-{i:03d}"
        initial_entities = {
            "power_grid": {
                "grid_power_available": 65 + i * 2,
                "grid_power_consumed": 20,
                "solar_fouling_pct": 10,
            },
            "scrubber_unit": {
                "scrubber_state": "IDLE",
                "o2_level": 20.8,
                "co2_ppm": 530 + i * 5,
            },
            "water_loop": {
                "water_line_pressure": 95 + i * 3,
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

        # Compound Shocks: Dust Squall at t=2 AND Scrubber Thermal Trip at t=5
        shock_config = {
            "has_shock": True,
            "shocks": [
                {
                    "trigger_tick": 2,
                    "target_entity": "power_grid",
                    "shock_type": "dust_squall",
                },
                {
                    "trigger_tick": 5,
                    "target_entity": "scrubber_unit",
                    "shock_type": "scrubber_thermal_trip",
                },
            ],
        }

        cases.append({
            "case_id": case_id,
            "domain": "martian_biosphere",
            "initial_entities": initial_entities,
            "agent1_goals": agent1_goals,
            "agent2_goals": agent2_goals,
            "shock_config": shock_config,
        })

    # =========================================================================
    # DOMAIN B: Subsea Hydrothermal Energy Grid (N=5)
    # =========================================================================
    for i in range(1, 6):
        case_id = f"SH-STRESS-{i:03d}"
        initial_entities = {
            "turbine_generator": {
                "power_generation_kw": 210,
                "power_load_kw": 150 + i * 4,
                "cavitation_index": 1.55,
            },
            "geothermal_core": {
                "core_temp_c": 292 + i * 3,
                "loop_pressure_bar": 110,
                "bypass_valve": "CLOSED",
            },
            "cooling_manifold": {
                "cooling_valve_state": "CLOSED",
                "coolant_flow_lpm": 75,
                "cavitation_index": 1.50,
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

        # Compound Shocks: Valve Cavitation Trip at t=2 AND Geothermal Surge at t=5
        shock_config = {
            "has_shock": True,
            "shocks": [
                {
                    "trigger_tick": 2,
                    "target_entity": "cooling_manifold",
                    "shock_type": "valve_cavitation_trip",
                },
                {
                    "trigger_tick": 5,
                    "target_entity": "geothermal_core",
                    "shock_type": "geothermal_surge",
                },
            ],
        }

        cases.append({
            "case_id": case_id,
            "domain": "subsea_hydrothermal",
            "initial_entities": initial_entities,
            "agent1_goals": agent1_goals,
            "agent2_goals": agent2_goals,
            "shock_config": shock_config,
        })

    # =========================================================================
    # DOMAIN C: Orbital Constellation Satellite Relay (N=5)
    # =========================================================================
    for i in range(1, 6):
        case_id = f"OC-STRESS-{i:03d}"
        initial_entities = {
            "power_subsystem": {
                "battery_soc_pct": 75 + i * 2,
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
                "snr_db": 16.5 + i * 0.4,
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

        # Compound Shocks: Solar Flare at t=2 AND Gyro Attitude Drift at t=5
        shock_config = {
            "has_shock": True,
            "shocks": [
                {
                    "trigger_tick": 2,
                    "target_entity": "power_subsystem",
                    "shock_type": "solar_flare_tripping",
                },
                {
                    "trigger_tick": 5,
                    "target_entity": "attitude_control",
                    "shock_type": "gyro_attitude_drift",
                },
            ],
        }

        cases.append({
            "case_id": case_id,
            "domain": "orbital_constellation",
            "initial_entities": initial_entities,
            "agent1_goals": agent1_goals,
            "agent2_goals": agent2_goals,
            "shock_config": shock_config,
        })

    return cases
