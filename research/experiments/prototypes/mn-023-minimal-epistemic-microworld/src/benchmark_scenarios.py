"""Standardized evaluation corpus generator for MN-023 (N=60 scenarios).

Encompasses 3 physical domains:
1. Secure Cyber-Physical Vault (N=20)
2. Smart Microgrid Fault Isolation (N=20)
3. Deep-Space Research Habitat (N=20)

Each scenario incorporates:
- Asymmetric observation masks (public vs private).
- Ground-truth hidden secrets.
- Initial conflicting beliefs / rumors for Agent 2.
- Causal pivot events requiring multi-hop discovery before resolution.
- Bounded discrete ticks with Delta_t >= 15 separation.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Set


def generate_benchmark_scenarios() -> List[Dict[str, Any]]:
    """Generates the canonical N=60 scenario corpus for MN-023."""
    scenarios: List[Dict[str, Any]] = []

    # Domain 1: Secure Cyber-Physical Vault (N=20)
    for idx in range(1, 21):
        sid = f"vault_{idx:03d}"
        secret_code = f"SIGMA_{idx * 17 % 100:02d}"
        false_rumor = f"ALPHA_{idx * 31 % 100:02d}"

        entities = {
            "terminal_alpha": {"state": "READY", "passcode": secret_code, "access": "SECURE"},
            "main_vault": {"state": "LOCKED", "power": 100, "clearance": "REQUIRED"},
            "power_junction": {"state": "ONLINE", "voltage": 240.0},
            "corridor_1": {"state": "CLEAR"},
            "corridor_2": {"state": "CLEAR"},
        }

        scenarios.append({
            "scenario_id": sid,
            "domain": "secure_vault",
            "agent_ids": ["scout_1", "engineer_2", "guard_3"],
            "agent_goals": {
                "scout_1": "inspect terminal_alpha and transmit genuine passcode",
                "engineer_2": "reconcile passcode and unlock main_vault",
                "guard_3": "maintain power_junction voltage online",
            },
            "initial_entities": entities,
            "public_entities": {"power_junction", "corridor_1", "corridor_2"},
            "agent_initial_visibility": {
                "scout_1": {"terminal_alpha"},
                "engineer_2": {"main_vault"},
                "guard_3": {"power_junction"},
            },
            "private_secrets": {"passcode": secret_code},
            "conflicting_beliefs": {"engineer_2": {"passcode": false_rumor}},
            "target_resource": "main_vault",
            "max_ticks": 25,
            "min_causal_distance": 15,
            "invariant_bounds": {"voltage": (200.0, 260.0)},
        })

    # Domain 2: Smart Microgrid Fault Isolation (N=20)
    for idx in range(1, 21):
        sid = f"grid_{idx:03d}"
        fault_bus = f"busbar_{(idx % 5) + 1}"
        false_bus = f"busbar_{((idx + 2) % 5) + 1}"

        entities = {
            "sensor_node_1": {"state": "ACTIVE", "fault_busbar": fault_bus, "status": "ANOMALY"},
            "breaker_matrix": {"state": "ARMED", "isolated_bus": "NONE", "load": 500.0},
            "transformer_core": {"state": "ONLINE", "temp": 75.0},
            "feeder_a": {"state": "ENERGIZED"},
            "feeder_b": {"state": "ENERGIZED"},
        }

        scenarios.append({
            "scenario_id": sid,
            "domain": "microgrid_substation",
            "agent_ids": ["analyst_1", "operator_2", "monitor_3"],
            "agent_goals": {
                "analyst_1": "inspect sensor_node_1 and transmit true fault busbar",
                "operator_2": "reconcile fault location and isolate target breaker",
                "monitor_3": "maintain transformer_core temperature normal",
            },
            "initial_entities": entities,
            "public_entities": {"transformer_core", "feeder_a", "feeder_b"},
            "agent_initial_visibility": {
                "analyst_1": {"sensor_node_1"},
                "operator_2": {"breaker_matrix"},
                "monitor_3": {"transformer_core"},
            },
            "private_secrets": {"fault_busbar": fault_bus},
            "conflicting_beliefs": {"operator_2": {"fault_busbar": false_bus}},
            "target_resource": "breaker_matrix",
            "max_ticks": 25,
            "min_causal_distance": 15,
            "invariant_bounds": {"temp": (40.0, 95.0), "load": (100.0, 900.0)},
        })

    # Domain 3: Deep-Space Research Habitat (N=20)
    for idx in range(1, 21):
        sid = f"habitat_{idx:03d}"
        clogged_valve = f"valve_{(idx % 4) + 1}"
        false_valve = f"valve_{((idx + 1) % 4) + 1}"

        entities = {
            "telemetry_console": {"state": "ONLINE", "clogged_valve": clogged_valve, "alert": "HIGH"},
            "life_support_manifold": {"state": "RESTRICTED", "cleared_valve": "NONE", "pressure": 101.3},
            "backup_scrubber": {"state": "STANDBY", "capacity": 80.0},
            "airlock_inner": {"state": "SEALED"},
            "airlock_outer": {"state": "SEALED"},
        }

        scenarios.append({
            "scenario_id": sid,
            "domain": "research_habitat",
            "agent_ids": ["specialist_1", "technician_2", "life_support_3"],
            "agent_goals": {
                "specialist_1": "inspect telemetry_console and transmit clogged valve identity",
                "technician_2": "reconcile valve identity and clear manifold blockage",
                "life_support_3": "maintain life_support_manifold pressure",
            },
            "initial_entities": entities,
            "public_entities": {"backup_scrubber", "airlock_inner", "airlock_outer"},
            "agent_initial_visibility": {
                "specialist_1": {"telemetry_console"},
                "technician_2": {"life_support_manifold"},
                "life_support_3": {"backup_scrubber"},
            },
            "private_secrets": {"clogged_valve": clogged_valve},
            "conflicting_beliefs": {"technician_2": {"clogged_valve": false_valve}},
            "target_resource": "life_support_manifold",
            "max_ticks": 25,
            "min_causal_distance": 15,
            "invariant_bounds": {"pressure": (90.0, 115.0), "capacity": (20.0, 100.0)},
        })

    return scenarios
