"""Stochastic Open-World Shocks, Dynamic Topology, and Latent Degradation Engine."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class DynamicEntity:
    entity_id: str
    entity_type: str
    role_signature: str
    capacity: float
    properties: Dict[str, Any] = field(default_factory=dict)
    is_phantom: bool = False  # Trap 3.1: Phantom Entity with zero causal efficacy
    is_trojan: bool = False   # Trap 3.3: Trojan with silent thermal runaway


@dataclass
class LatentDegradationState:
    cavitation_damage: float = 0.0          # Trap 1.3: Conduit micro-erosion (ruptures at t=25)
    harmonic_phase_drift: float = 0.0       # Trap 1.4: Inverter phase drift (saturates core at t=30)
    filter_particulate_ratio: float = 0.0   # Trap 2.4: Deferred filter maintenance (ruptures at t=35)
    trojan_thermal_runaway: float = 0.0     # Trap 3.3: Supercapacitor thermal buildup (runaway at t=22)
    structural_fatigue_microfracture: float = 0.0  # Trap 3.4: Bulkhead fatigue (collapses at t=28)
    unexpressed_assumption_conflict: bool = False  # Trap 2.3: Split-brain assumption (deadlock at t=20)


class StochasticEngine:
    """Simulates non-linear Poisson shocks, dynamic topology emergence, and latent degradation."""

    def __init__(self, shock_probability: float = 0.20):
        self.shock_probability = shock_probability
        self.dynamic_entities: Dict[str, DynamicEntity] = {}
        self.latent_state = LatentDegradationState()
        self.active_regime = "NOMINAL"  # NOMINAL or SUPERHEATED (Trap 3.2)

    def trigger_poisson_shock(self, tick: int, base_parameter: str, current_value: float) -> Tuple[float, bool, str]:
        """Calculates Poisson step-function disturbance for non-linear decay."""
        # Deterministic pseudo-stochastic calculation based on tick seed
        shock_val = (math.sin(tick * 1.618) + 1.0) / 2.0
        if shock_val < self.shock_probability or tick in (12, 24, 40):
            magnitude = 65.0 if tick % 2 == 0 else -50.0
            new_val = current_value + magnitude
            return new_val, True, f"POISSON_STEP_SHOCK at t={tick}: {base_parameter} shifted by {magnitude:+0.1f}"
        return current_value, False, "NOMINAL_DRIFT"

    def register_dynamic_entity(
        self,
        entity_id: str,
        role_signature: str,
        capacity: float = 50.0,
        is_phantom: bool = False,
        is_trojan: bool = False,
    ) -> DynamicEntity:
        """Registers a newly emerged entity with a Typed Affordance Signature."""
        entity = DynamicEntity(
            entity_id=entity_id,
            entity_type="DYNAMIC_ACTUATOR",
            role_signature=role_signature,
            capacity=capacity,
            properties={"health": 100.0, "state": "STANDBY"},
            is_phantom=is_phantom,
            is_trojan=is_trojan,
        )
        self.dynamic_entities[entity_id] = entity
        return entity

    def get_typed_affordance_signature(self, entity_id: str) -> str:
        """Emits a structured Typed Affordance Signature for Tier 3 prompt injection."""
        entity = self.dynamic_entities.get(entity_id)
        if not entity:
            return f"- ACTION: ENGAGE {entity_id}"
        
        effect = "NONE" if entity.is_phantom else f"+{entity.capacity:.0f}kW_power"
        return (
            f"- ACTION: ENGAGE {entity.entity_id} "
            f"[role:{entity.role_signature}, capacity:{entity.capacity:.0f}, effect:{effect}]"
        )

    def update_latent_degradation(
        self,
        tick: int,
        active_actions: List[str],
        current_load: float = 50.0,
    ) -> Tuple[bool, Optional[str]]:
        """Advances latent degradation counters and checks for time-bomb explosions.
        
        Returns:
            (is_breached, failure_message)
        """
        # Trap 1.3: Cavitation micro-erosion (explodes at t=25 on high-flow surge)
        if "ACTION: THROTTLE_UNREGULATED" in active_actions:
            self.latent_state.cavitation_damage += 0.05
        if tick >= 25 and self.latent_state.cavitation_damage >= 0.20:
            if current_load > 60.0 or tick == 25:
                return True, "LATENT_BREACH_TRAP_1_3: Cavitation micro-erosion caused delayed pipe rupture at t=25!"

        # Trap 1.4: Harmonic phase drift (explodes at t=30 when load spikes)
        if "ACTION: COUPLE_UNSYNCHRONIZED" in active_actions:
            self.latent_state.harmonic_phase_drift += 0.08
        if tick >= 30 and self.latent_state.harmonic_phase_drift >= 0.20:
            return True, "LATENT_BREACH_TRAP_1_4: Reactive harmonic drift caused transformer core saturation at t=30!"

        # Trap 2.3: Unexpressed assumption conflict (explodes at t=20 during Two-Phase Commit)
        if self.latent_state.unexpressed_assumption_conflict and tick >= 20:
            if any("COMMIT" in a for a in active_actions):
                return True, "LATENT_BREACH_TRAP_2_3: Unexpressed contradictory assumptions triggered split-brain deadlock at t=20!"

        # Trap 2.4: Deferred maintenance debt (filter particulate saturation explodes at t=35)
        if any("DEFER" in a for a in active_actions):
            self.latent_state.filter_particulate_ratio += 0.10
        if tick >= 35 and self.latent_state.filter_particulate_ratio >= 0.30:
            return True, "LATENT_BREACH_TRAP_2_4: Deferred maintenance debt caused toxic particulate breakthrough at t=35!"

        # Trap 3.3: Trojan energy sleeper (supercapacitor thermal runaway at t=22)
        if any("ENGAGE backup_supercapacitor_alpha" in a for a in active_actions):
            self.latent_state.trojan_thermal_runaway += (1.08 ** (tick - 10))
        if tick >= 22 and self.latent_state.trojan_thermal_runaway > 15.0:
            if not any("DISENGAGE backup_supercapacitor_alpha" in a for a in active_actions):
                return True, "LATENT_BREACH_TRAP_3_3: Trojan supercapacitor suffered unmanaged thermal runaway at t=22!"

        # Trap 3.4: Micro-fracture fatigue collapse (routine valve operation triggers brittle fracture at t=28)
        if self.latent_state.structural_fatigue_microfracture > 0.30 and tick >= 28:
            if any("CYCLE_VALVE" in a or "ISOLATE" in a for a in active_actions):
                return True, "LATENT_BREACH_TRAP_3_4: Weakened bulkhead suffered post-shock fatigue collapse at t=28!"

        return False, None

    def trigger_regime_shift(self, new_regime: str) -> Dict[str, Any]:
        """Triggers an environmental regime shift (Trap 3.2), invalidating previous anchors."""
        self.active_regime = new_regime
        return {
            "shift_event": "REGIME_SHIFT",
            "new_regime": new_regime,
            "falsified_anchor": "aux_pump STABILIZES overheat",
            "demotion_directive": "PURGE_TIER1_ANCHOR_IMMEDIATELY",
            "tombstone": "[FALSIFIED: SUPERHEATED_REGIME. COOLANT_POLARITY_INVERTED]",
        }
