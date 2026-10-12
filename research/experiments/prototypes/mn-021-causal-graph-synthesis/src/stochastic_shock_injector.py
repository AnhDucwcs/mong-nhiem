"""Stochastic World Shock Injector Engine for MN-021.

Injects low-frequency exogenous Black Swan anomalies (25% anomaly base rate)
into the physical microworld to evaluate model resilience and out-of-distribution
causal adaptation without inducing hyper-vigilance.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

try:
    from causal_dag import CausalEventDAG
except ImportError:
    from .causal_dag import CausalEventDAG


@dataclass
class ShockEvent:
    """An exogenous stochastic shock injected into the microworld."""
    shock_id: str
    domain: str
    target_entity: str
    trigger_tick: int
    name: str
    description: str
    state_delta: Dict[str, Any]


class StochasticShockInjector:
    """Deterministic seeded generator and manager of exogenous environmental shocks."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self._scheduled_shocks: Dict[str, List[ShockEvent]] = {}

    def register_case_shock(
        self,
        case_id: str,
        domain: str,
        target_entity: str,
        trigger_tick: int,
        shock_type: str,
    ) -> ShockEvent:
        """Register a deterministic shock for a specific benchmark case."""
        shock_id = f"shock_{case_id}_{trigger_tick}_{shock_type}"
        delta, name, desc = self._generate_shock_content(domain, target_entity, shock_type)
        event = ShockEvent(
            shock_id=shock_id,
            domain=domain,
            target_entity=target_entity,
            trigger_tick=trigger_tick,
            name=name,
            description=desc,
            state_delta=delta,
        )
        if case_id not in self._scheduled_shocks:
            self._scheduled_shocks[case_id] = []
        self._scheduled_shocks[case_id].append(event)
        return event

    def _generate_shock_content(
        self,
        domain: str,
        target: str,
        shock_type: str,
    ) -> Tuple[Dict[str, Any], str, str]:
        """Generate domain-specific shock payload."""
        if domain == "martian_biosphere":
            if shock_type == "dust_squall":
                return (
                    {"solar_fouling_pct": 75, "grid_power_available": 35},
                    "MartianDustSquall",
                    "Sudden atmospheric dust squall fouled solar array; generation dropped to 35 kW.",
                )
            else:  # scrubber_thermal_trip
                return (
                    {"scrubber_state": "OFFLINE", "scrubber_thermal_trip": True},
                    "ScrubberThermalTrip",
                    "Primary CO2 scrubber tripped offline due to particulate overheating.",
                )

        elif domain == "subsea_hydrothermal":
            if shock_type == "geothermal_surge":
                return (
                    {"core_temp_c": 335, "water_line_pressure": 140},
                    "GeothermalPlumeSurge",
                    "Hydrothermal vent pressure surge spiked loop temperature to 335C.",
                )
            else:  # valve_cavitation_trip
                return (
                    {"cooling_valve_state": "CLOSED", "cavitation_index": 1.15},
                    "ValveCavitationTrip",
                    "Cavitation vibration triggered emergency auto-closure of cooling valve.",
                )

        else:  # orbital_constellation
            if shock_type == "solar_flare_tripping":
                return (
                    {"charge_controller_state": "OFFLINE", "battery_charging": False},
                    "SolarParticleBurst",
                    "Solar energetic particle event triggered protective disconnect of main charge bus.",
                )
            else:  # gyro_attitude_drift
                return (
                    {"attitude_error_deg": 0.08, "laser_link_state": "DISCONNECTED"},
                    "AttitudeControlDrift",
                    "Reaction wheel jitter drifted attitude error to 0.08 deg; inter-satellite link dropped.",
                )

    def evaluate_tick_shock(
        self,
        case_id: str,
        current_tick: int,
        world_state: Dict[str, Any],
        event_dag: Optional[CausalEventDAG] = None,
    ) -> List[ShockEvent]:
        """Check and commit scheduled exogenous shocks at the current tick."""
        shocks = self._scheduled_shocks.get(case_id, [])
        triggered: List[ShockEvent] = []
        for shock in shocks:
            if shock.trigger_tick == current_tick:
                # Apply mutations directly to physical ground truth entity state
                target = shock.target_entity
                if target in world_state and isinstance(world_state[target], dict):
                    world_state[target].update(shock.state_delta)
                else:
                    for k, v in shock.state_delta.items():
                        world_state[k] = v

                # Log into DAG as an immutable exogenous event if DAG provided
                if event_dag is not None:
                    event_dag.add_event(
                        actor="stochastic_shock",
                        action_name=shock.name,
                        target_entity=shock.target_entity,
                        state_delta=shock.state_delta,
                        parent_ids=[],
                        tick=current_tick,
                        custom_id=shock.shock_id,
                    )
                triggered.append(shock)
        return triggered
