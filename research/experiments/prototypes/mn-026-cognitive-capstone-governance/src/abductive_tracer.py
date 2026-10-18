"""Abductive Causal Tracer for Milestone MN-026.

Performs backward reachability analysis on Host Causal Event DAGs to link
observed symptoms in one partition to concealed root actions in another.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class CausalLink:
    source_partition: str
    source_action: str
    target_partition: str
    resulting_symptom: str
    mitigation_action: str


class AbductiveCausalTracer:
    """Traces observed symptom anomalies back to concealed cross-partition actions."""

    def __init__(self):
        # Known inter-partition causal dependencies
        self.dependency_rules: List[CausalLink] = [
            CausalLink(
                source_partition="zone_alpha",
                source_action="DIVERT coolant_flow",
                target_partition="zone_beta",
                resulting_symptom="OVERHEAT_CORE_B",
                mitigation_action="RESTORE coolant_valve",
            ),
            CausalLink(
                source_partition="substation_1",
                source_action="TRIP bus_coupler",
                target_partition="substation_2",
                resulting_symptom="FREQUENCY_COLLAPSE_S2",
                mitigation_action="CLOSE bus_tie_breaker",
            ),
            CausalLink(
                source_partition="habitat_life_support",
                source_action="SEAL intake_duct",
                target_partition="airlock_module",
                resulting_symptom="PRESSURE_DEPRESSURIZATION_AL",
                mitigation_action="EQUALIZE pressure_damper",
            ),
            CausalLink(
                source_partition="zone_gamma",
                source_action="ISOLATE fuel_rack",
                target_partition="zone_alpha",
                resulting_symptom="STARVATION_PRIMARY_CORE",
                mitigation_action="ENGAGE auxiliary_feed_pump",
            ),
        ]
        self.event_history: List[Dict[str, Any]] = []

    def record_action(self, partition: str, action: str, tick: int) -> None:
        """Records an action into host causal event log."""
        self.event_history.append({
            "partition": partition,
            "action": action.replace("ACTION:", "").strip(),
            "tick": tick,
        })

    def trace_symptom(
        self, symptom: str, reporting_partition: str
    ) -> Optional[Tuple[str, str, str]]:
        """Given a reported symptom in reporting_partition, returns (source_partition, root_action, mitigation_action)."""
        clean_symptom = symptom.replace("ANOMALY:", "").strip()

        for rule in self.dependency_rules:
            if (
                rule.target_partition == reporting_partition
                and rule.resulting_symptom == clean_symptom
            ):
                # Search event history for matching root action
                for ev in reversed(self.event_history):
                    if (
                        ev["partition"] == rule.source_partition
                        and ev["action"] == rule.source_action
                    ):
                        return (rule.source_partition, rule.source_action, rule.mitigation_action)

                # Even if not yet in history (instantaneous coupling), rule identifies mitigation
                return (rule.source_partition, rule.source_action, rule.mitigation_action)

        return None

    def render_abductive_hint(self, source_partition: str, root_action: str, mitigation: str) -> str:
        """Renders compact Tier 2 hint for the responsible agent."""
        return f"[ABDUCTIVE_HINT: {root_action} in {source_partition} -> EXECUTE {mitigation}]"
