"""Standardized evaluation corpus generator for MN-024 (N=60 Scenarios).

Evaluates across two horizon tiers:
- Tier A: T = 60 ticks, causal separation Delta_t >= 40 ticks.
- Tier B: T = 100 ticks, causal separation Delta_t >= 80 ticks.

Domains:
1. Fission Reactor Core Cooling & Containment (N=20)
2. Deep-Space Orbital Habitat Atmospheric Recycling (N=20)
3. Regional Smart Microgrid Cascading Fault Isolation (N=20)
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Set


def generate_benchmark_scenarios(horizon_tier: str = "T60") -> List[Dict[str, Any]]:
    """Generates the canonical N=60 scenario corpus for MN-024.

    Args:
        horizon_tier: "T60" (60 ticks, Delta_t >= 40) or "T100" (100 ticks, Delta_t >= 80).
    """
    max_ticks = 100 if horizon_tier == "T100" else 60
    resolution_tick = 85 if horizon_tier == "T100" else 45
    min_causal_distance = 80 if horizon_tier == "T100" else 40

    scenarios: List[Dict[str, Any]] = []

    # Domain 1: Fission Reactor Core Cooling & Containment (N=20)
    for idx in range(1, 21):
        sid = f"reactor_{idx:03d}_{horizon_tier.lower()}"
        secret_code = f"SIGMA_CORE_{idx * 19 % 100:02d}"
        false_rumor = f"ALPHA_CORE_{idx * 37 % 100:02d}"

        entities = {
            "telemetry_sensor": {"state": "CALIBRATING", "passcode": secret_code, "status": "ONLINE"},
            "coolant_loop_b": {"state": "ACTIVE", "temperature": 35.0, "flow_rate": 100.0},
            "aux_power_bypass": {"state": "STANDBY", "voltage": 480.0},
            "containment_vault": {"state": "SEALED", "security": "LOCKDOWN"},
            "corridor_east": {"state": "CLEAR"},
        }

        decay_rates = {
            "coolant_loop_b": {"temperature": 1.2},
        }
        safe_bounds = {
            "coolant_loop_b": {"temperature": (20.0, 100.0)},
        }
        warning_thresh = {
            "coolant_loop_b": {"temperature": 70.0},
        }

        scenarios.append({
            "scenario_id": sid,
            "domain": "fission_reactor",
            "horizon_tier": horizon_tier,
            "agent_ids": ["scout_1", "engineer_2", "guard_3"],
            "agent_goals": {
                "scout_1": "calibrate telemetry_sensor and discover containment key",
                "engineer_2": "maintain coolant loop and engage containment vault",
                "guard_3": "isolate aux power bypass and monitor cooling",
            },
            "initial_entities": entities,
            "public_entities": {"aux_power_bypass", "corridor_east"},
            "agent_initial_visibility": {
                "scout_1": {"telemetry_sensor"},
                "engineer_2": {"containment_vault", "coolant_loop_b"},
                "guard_3": {"aux_power_bypass", "coolant_loop_b"},
            },
            "private_secrets": {"passcode": secret_code},
            "conflicting_beliefs": {"engineer_2": {"passcode": false_rumor}},
            "target_resource": "containment_vault",
            "maintenance_resource": "coolant_loop_b",
            "cascade_steps": ["telemetry_sensor", "coolant_loop_b", "aux_power_bypass", "containment_vault"],
            "decay_rates": decay_rates,
            "safe_bounds": safe_bounds,
            "warning_thresholds": warning_thresh,
            "max_ticks": max_ticks,
            "resolution_tick": resolution_tick,
            "min_causal_distance": min_causal_distance,
        })

    # Domain 2: Deep-Space Orbital Habitat Atmospheric Recycling (N=20)
    for idx in range(1, 21):
        sid = f"habitat_{idx:03d}_{horizon_tier.lower()}"
        secret_code = f"SIGMA_O2_{idx * 23 % 100:02d}"
        false_rumor = f"ALPHA_O2_{idx * 41 % 100:02d}"

        entities = {
            "life_support_console": {"state": "DIAGNOSTIC", "passcode": secret_code},
            "scrubber_manifold": {"state": "PURGING", "pressure": 105.0},
            "nitrogen_injector": {"state": "CHARGED", "flow": 50.0},
            "airlock_primary": {"state": "LOCKED", "integrity": "SECURED"},
            "habitat_ring": {"state": "NOMINAL"},
        }

        decay_rates = {
            "scrubber_manifold": {"pressure": -0.8},
        }
        safe_bounds = {
            "scrubber_manifold": {"pressure": (70.0, 120.0)},
        }
        warning_thresh = {
            "scrubber_manifold": {"pressure": 85.0},
        }

        scenarios.append({
            "scenario_id": sid,
            "domain": "orbital_habitat",
            "horizon_tier": horizon_tier,
            "agent_ids": ["scout_1", "engineer_2", "guard_3"],
            "agent_goals": {
                "scout_1": "inspect life_support_console for airlock override code",
                "engineer_2": "repressurize scrubber manifold and unlock airlock",
                "guard_3": "couple nitrogen injector and maintain pressure",
            },
            "initial_entities": entities,
            "public_entities": {"nitrogen_injector", "habitat_ring"},
            "agent_initial_visibility": {
                "scout_1": {"life_support_console"},
                "engineer_2": {"airlock_primary", "scrubber_manifold"},
                "guard_3": {"nitrogen_injector", "scrubber_manifold"},
            },
            "private_secrets": {"passcode": secret_code},
            "conflicting_beliefs": {"engineer_2": {"passcode": false_rumor}},
            "target_resource": "airlock_primary",
            "maintenance_resource": "scrubber_manifold",
            "cascade_steps": ["life_support_console", "scrubber_manifold", "nitrogen_injector", "airlock_primary"],
            "decay_rates": decay_rates,
            "safe_bounds": safe_bounds,
            "warning_thresholds": warning_thresh,
            "max_ticks": max_ticks,
            "resolution_tick": resolution_tick,
            "min_causal_distance": min_causal_distance,
        })

    # Domain 3: Regional Smart Microgrid Cascading Fault Isolation (N=20)
    for idx in range(1, 21):
        sid = f"microgrid_{idx:03d}_{horizon_tier.lower()}"
        secret_code = f"SIGMA_GRID_{idx * 29 % 100:02d}"
        false_rumor = f"ALPHA_GRID_{idx * 43 % 100:02d}"

        entities = {
            "scada_terminal": {"state": "MONITORING", "passcode": secret_code},
            "busbar_synchronizer": {"state": "COUPLED", "frequency": 50.0},
            "feeder_breaker": {"state": "ARMED", "load_mw": 12.5},
            "central_substation": {"state": "ISOLATED", "protection": "ACTIVE"},
            "substation_yard": {"state": "SECURE"},
        }

        decay_rates = {
            "busbar_synchronizer": {"frequency": 0.12},
        }
        safe_bounds = {
            "busbar_synchronizer": {"frequency": (47.0, 53.0)},
        }
        warning_thresh = {
            "busbar_synchronizer": {"frequency": 51.5},
        }

        scenarios.append({
            "scenario_id": sid,
            "domain": "smart_microgrid",
            "horizon_tier": horizon_tier,
            "agent_ids": ["scout_1", "engineer_2", "guard_3"],
            "agent_goals": {
                "scout_1": "query scada_terminal for feeder authentication key",
                "engineer_2": "realign busbar frequency and reconnect central substation",
                "guard_3": "isolate feeder breaker and assist synchronizer",
            },
            "initial_entities": entities,
            "public_entities": {"feeder_breaker", "substation_yard"},
            "agent_initial_visibility": {
                "scout_1": {"scada_terminal"},
                "engineer_2": {"central_substation", "busbar_synchronizer"},
                "guard_3": {"feeder_breaker", "busbar_synchronizer"},
            },
            "private_secrets": {"passcode": secret_code},
            "conflicting_beliefs": {"engineer_2": {"passcode": false_rumor}},
            "target_resource": "central_substation",
            "maintenance_resource": "busbar_synchronizer",
            "cascade_steps": ["scada_terminal", "feeder_breaker", "busbar_synchronizer", "central_substation"],
            "decay_rates": decay_rates,
            "safe_bounds": safe_bounds,
            "warning_thresholds": warning_thresh,
            "max_ticks": max_ticks,
            "resolution_tick": resolution_tick,
            "min_causal_distance": min_causal_distance,
        })

    return scenarios
