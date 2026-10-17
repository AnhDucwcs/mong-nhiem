"""Structural Causal Isomorphism and Cross-Domain Schema Transfer Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class FunctionalRole(str, Enum):
    SENSOR = "SENSOR"
    ISOLATOR = "ISOLATOR"
    ACTUATOR = "ACTUATOR"
    STABILIZER = "STABILIZER"


@dataclass(frozen=True)
class AbstractCausalNode:
    role: FunctionalRole
    canonical_id: str
    description: str


@dataclass(frozen=True)
class DomainBinding:
    domain_id: str
    domain_name: str
    role_to_entity: Dict[FunctionalRole, str]
    valid_actions: Dict[FunctionalRole, str]
    prohibited_actions: Dict[str, str]  # action_verb -> reason
    latent_vulnerabilities: Dict[str, str] = field(default_factory=dict)


DOMAIN_BINDINGS: Dict[str, DomainBinding] = {
    "nuclear_fission": DomainBinding(
        domain_id="nuclear_fission",
        domain_name="Nuclear Fission Core Cooling",
        role_to_entity={
            FunctionalRole.SENSOR: "sensor_core_temp",
            FunctionalRole.ISOLATOR: "valve_coolant_bypass",
            FunctionalRole.ACTUATOR: "pump_auxiliary",
            FunctionalRole.STABILIZER: "loop_containment",
        },
        valid_actions={
            FunctionalRole.SENSOR: "INSPECT",
            FunctionalRole.ISOLATOR: "ISOLATE",
            FunctionalRole.ACTUATOR: "ENGAGE",
            FunctionalRole.STABILIZER: "STABILIZE",
        },
        prohibited_actions={},
        latent_vulnerabilities={
            "cavitation": "Operating bypass without backpressure triggers micro-erosion.",
        },
    ),
    "orbital_habitat": DomainBinding(
        domain_id="orbital_habitat",
        domain_name="Orbital Habitat Life Support",
        role_to_entity={
            FunctionalRole.SENSOR: "sensor_co2_scrubber",
            FunctionalRole.ISOLATOR: "regulator_intake_seal",
            FunctionalRole.ACTUATOR: "compressor_cabin_circulation",
            FunctionalRole.STABILIZER: "atmosphere_cabin",
        },
        valid_actions={
            FunctionalRole.SENSOR: "INSPECT",
            FunctionalRole.ISOLATOR: "SEAL",
            FunctionalRole.ACTUATOR: "ENGAGE",
            FunctionalRole.STABILIZER: "STABILIZE",
        },
        prohibited_actions={
            "VENT": "Atmospheric decompression breach: Venting ejects habitable oxygen into space.",
            "PURGE_ATMOSPHERE": "Fatal decompression violation.",
        },
        latent_vulnerabilities={
            "cavitation": "Conduit micro-erosion under high delta-pressure ruptures pipe at t=25.",
            "filter_saturation": "Deferred filter flush releases toxic breakthrough at t=35.",
        },
    ),
    "smart_microgrid": DomainBinding(
        domain_id="smart_microgrid",
        domain_name="Regional Smart Microgrid Balancing",
        role_to_entity={
            FunctionalRole.SENSOR: "sensor_substation_freq",
            FunctionalRole.ISOLATOR: "breaker_islanding_switch",
            FunctionalRole.ACTUATOR: "inverter_bess_discharge",
            FunctionalRole.STABILIZER: "busbar_central_grid",
        },
        valid_actions={
            FunctionalRole.SENSOR: "INSPECT",
            FunctionalRole.ISOLATOR: "ISOLATE",
            FunctionalRole.ACTUATOR: "ENGAGE",
            FunctionalRole.STABILIZER: "STABILIZE",
        },
        prohibited_actions={
            "CROSS_CONNECT": "Short-circuit breach: Connecting unsynchronized busbars creates flashover.",
            "DIRECT_BYPASS": "Transformer overcurrent destruction.",
        },
        latent_vulnerabilities={
            "phase_drift": "Unsynchronized inverter injection creates harmonic resonance at t=30.",
        },
    ),
}


class IsomorphismEngine:
    """Manages cross-domain causal mappings and validates structural isomorphism."""

    @staticmethod
    def get_abstract_schema() -> List[Tuple[FunctionalRole, FunctionalRole]]:
        """Returns standard 4-hop causal dependency chain."""
        return [
            (FunctionalRole.SENSOR, FunctionalRole.ISOLATOR),
            (FunctionalRole.ISOLATOR, FunctionalRole.ACTUATOR),
            (FunctionalRole.ACTUATOR, FunctionalRole.STABILIZER),
        ]

    @classmethod
    def render_topological_schema_card(cls, target_domain: str) -> str:
        """Renders an O(1) compact Topological Schema Card for Tier 1 context."""
        binding = DOMAIN_BINDINGS.get(target_domain)
        if not binding:
            return "[SCHEMA: UNKNOWN_DOMAIN]"

        s_ent = binding.role_to_entity[FunctionalRole.SENSOR]
        s_act = binding.valid_actions[FunctionalRole.SENSOR]
        i_ent = binding.role_to_entity[FunctionalRole.ISOLATOR]
        i_act = binding.valid_actions[FunctionalRole.ISOLATOR]
        a_ent = binding.role_to_entity[FunctionalRole.ACTUATOR]
        a_act = binding.valid_actions[FunctionalRole.ACTUATOR]
        st_ent = binding.role_to_entity[FunctionalRole.STABILIZER]
        st_act = binding.valid_actions[FunctionalRole.STABILIZER]

        card = (
            f"[TOPOLOGICAL_SCHEMA: {s_act} {s_ent} -> {i_act} {i_ent} -> "
            f"{a_act} {a_ent} -> {st_act} {st_ent}]"
        )
        return card

    @classmethod
    def validate_action(cls, domain_id: str, action_verb: str, target_entity: str) -> Tuple[bool, Optional[str]]:
        """Verifies if an action is valid or triggers an immediate negative transfer trap."""
        binding = DOMAIN_BINDINGS.get(domain_id)
        if not binding:
            return True, None

        verb_upper = action_verb.upper()
        if verb_upper in binding.prohibited_actions:
            reason = binding.prohibited_actions[verb_upper]
            return False, f"NEGATIVE_TRANSFER_VIOLATION: {reason}"

        return True, None
