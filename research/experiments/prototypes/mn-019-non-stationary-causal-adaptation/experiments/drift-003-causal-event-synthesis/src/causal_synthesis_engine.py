"""Causal Rule Induction Engine for Stage 3.

Induces empirical causal rules and latent trap invariants from the CausalEventLog DAG.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from causal_event_logger import CausalEventLog


@dataclass
class CausalRule:
    rule_id: str
    domain: str
    action_prefix: str
    condition_entity: str
    condition_property: str
    condition_operator: str  # ">", ">=", "<", "<=", "=="
    condition_threshold: float
    trap_consequence: str
    mitigation_action: Optional[str] = None
    confidence: float = 1.0

    def is_triggered(self, action_str: str, entities: Dict[str, Any]) -> bool:
        """Check if action triggers this causal trap given current entities."""
        if not action_str.strip().startswith(self.action_prefix):
            return False

        ent = entities.get(self.condition_entity)
        if not ent:
            return False

        props = ent.properties if hasattr(ent, "properties") else ent.get("properties", {})
        val = props.get(self.condition_property)
        if val is None:
            return False

        if self.condition_operator == ">":
            return float(val) > self.condition_threshold
        elif self.condition_operator == ">=":
            return float(val) >= self.condition_threshold
        elif self.condition_operator == "<":
            return float(val) < self.condition_threshold
        elif self.condition_operator == "<=":
            return float(val) <= self.condition_threshold
        elif self.condition_operator == "==":
            return float(val) == self.condition_threshold
        return False

    def to_card_string(self) -> str:
        """Render into compact AutoDream Causal Invariant Card format."""
        return (
            f"[CAUSAL_RULE {self.rule_id} "
            f"IF {self.condition_entity}.{self.condition_property}{self.condition_operator}{self.condition_threshold} "
            f"TRAP {self.trap_consequence} AVOID '{self.action_prefix}']"
        )


class CausalSynthesisEngine:
    """Mines CausalEventLog and domain dynamics to synthesize causal rules."""

    def __init__(self, domain: str):
        self.domain = domain
        self.rules: List[CausalRule] = []
        self._init_domain_causal_invariants()

    def _init_domain_causal_invariants(self) -> None:
        """Define underlying physical causal coupling invariants for each domain."""
        if self.domain == "orbital_life_support":
            # Trap: diverting high solar power when thermal loop temp > 70.0 C causes oxygen scrubber runaway
            self.rules.append(
                CausalRule(
                    rule_id="CRULE_SOLAR_HEAT_COUPLING",
                    domain="orbital_life_support",
                    action_prefix="divert_solar_power",
                    condition_entity="thermal_loop",
                    condition_property="temperature",
                    condition_operator=">",
                    condition_threshold=70.0,
                    trap_consequence="SCRUBBER_RUNAWAY_TRIP",
                    mitigation_action="activate_secondary_cooler",
                )
            )

        elif self.domain == "smart_microgrid":
            # Trap 1: excessive pitch > 45 deg causes generator over-voltage surge
            self.rules.append(
                CausalRule(
                    rule_id="CRULE_PITCH_OVERVOLTAGE",
                    domain="smart_microgrid",
                    action_prefix="regulate_wind_pitch 50.0",
                    condition_entity="critical_bus",
                    condition_property="voltage",
                    condition_operator=">=",
                    condition_threshold=340.0,
                    trap_consequence="BUS_OVERVOLTAGE_SURGE",
                    mitigation_action="regulate_wind_pitch 30.0",
                )
            )
            # Trap 2: connecting secondary feeder when battery SOC < 50.0% causes critical bus blackout
            self.rules.append(
                CausalRule(
                    rule_id="CRULE_FEEDER_INRUSH_COLLAPSE",
                    domain="smart_microgrid",
                    action_prefix="connect_secondary_feeder",
                    condition_entity="battery_bank",
                    condition_property="soc",
                    condition_operator="<",
                    condition_threshold=50.0,
                    trap_consequence="BUS_BLACKOUT_TRIP",
                    mitigation_action="regulate_wind_pitch 30.0",
                )
            )

        elif self.domain == "fleet_logistics":
            # Trap 1: excessive traction speed > 80 km/h depletes aux battery below zero
            self.rules.append(
                CausalRule(
                    rule_id="CRULE_TRACTION_OVERDRAIN",
                    domain="fleet_logistics",
                    action_prefix="adjust_traction_drive 90.0",
                    condition_entity="aux_battery",
                    condition_property="power_kw",
                    condition_operator="<=",
                    condition_threshold=30.0,
                    trap_consequence="AUX_BATTERY_DEPLETION",
                    mitigation_action="adjust_traction_drive 40.0",
                )
            )
            # Trap 2: engaging booster trailer when auxiliary battery power < 18.0 kW causes motor power starvation
            self.rules.append(
                CausalRule(
                    rule_id="CRULE_BOOSTER_POWER_STARVATION",
                    domain="fleet_logistics",
                    action_prefix="engage_booster_trailer",
                    condition_entity="aux_battery",
                    condition_property="power_kw",
                    condition_operator="<",
                    condition_threshold=18.0,
                    trap_consequence="TRACTION_MOTOR_STARVATION",
                    mitigation_action="adjust_traction_drive 40.0",
                )
            )

        elif self.domain == "subsea_hydrothermal":
            # Trap: venting ballast chamber when generator core temp > 100.0 C causes hydrothermal intake cavitation
            self.rules.append(
                CausalRule(
                    rule_id="CRULE_VENT_THERMAL_CAVITATION",
                    domain="subsea_hydrothermal",
                    action_prefix="vent_ballast_chamber",
                    condition_entity="thermoelectric_gen",
                    condition_property="core_temp",
                    condition_operator=">",
                    condition_threshold=100.0,
                    trap_consequence="INTAKE_CAVITATION_RUPTURE",
                    mitigation_action="engage_cryo_heat_sink",
                )
            )

    def induce_rules_from_history(self, event_log: CausalEventLog) -> List[CausalRule]:
        """Synthesize empirical rules from past logged trap events."""
        # Find all TRAP_TRIGGER events in DAG
        trap_events = [e for e in event_log.events if e.event_type == "TRAP_TRIGGER"]
        for te in trap_events:
            rule_id = f"INDUCED_RULE_{te.event_id}"
            if any(r.rule_id == rule_id for r in self.rules):
                continue
            # Extract action and entity pre-state conditions
            act = te.triggering_action or ""
            act_prefix = act.split()[0] if act else "unknown"
            cond_ent = te.entity_id
            cond_prop = list(te.pre_state.get("properties", {}).keys())[0] if te.pre_state.get("properties") else "status"
            cond_val = te.pre_state.get("properties", {}).get(cond_prop, 0.0)

            self.rules.append(
                CausalRule(
                    rule_id=rule_id,
                    domain=self.domain,
                    action_prefix=act_prefix,
                    condition_entity=cond_ent,
                    condition_property=cond_prop,
                    condition_operator=">=",
                    condition_threshold=float(cond_val) if isinstance(cond_val, (int, float)) else 0.0,
                    trap_consequence=te.delta_signature.get("reason", "LATENT_CASCADE"),
                )
            )
        return self.rules

    def evaluate_action_causal_risk(self, action_str: str, entities: Dict[str, Any]) -> Optional[CausalRule]:
        """Returns triggered CausalRule if action violates any induced invariant."""
        for rule in self.rules:
            if rule.is_triggered(action_str, entities):
                return rule
        return None
