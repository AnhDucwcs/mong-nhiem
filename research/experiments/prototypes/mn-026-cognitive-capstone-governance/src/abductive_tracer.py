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
        self, symptom: str, reporting_partition: str, visited: Optional[Set[str]] = None
    ) -> Optional[Tuple[str, str, str]]:
        """Given a reported symptom in reporting_partition, returns (source_partition, root_action, mitigation_action).
        Includes cycle detection to terminate feedback loops (A -> B -> A) cleanly.
        """
        if visited is None:
            visited = set()

        clean_symptom = symptom.replace("ANOMALY:", "").strip()
        state_key = f"{reporting_partition}:{clean_symptom}"
        if state_key in visited:
            # Feedback loop cycle detected: break recursion and retain earliest observed cause
            return None
        visited.add(state_key)

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

    def compute_confluence_attribution(
        self, factors: Dict[str, Tuple[float, float]]
    ) -> Dict[str, float]:
        """Computes marginal contribution weights for multi-parent confluence symptoms.
        
        factors: Dict mapping factor_name -> (marginal_derivative dY/dXi, delta_Xi)
        Returns: Dict mapping factor_name -> normalized contribution in [0.0, 1.0]
        """
        raw_contributions: Dict[str, float] = {}
        for factor, (d_y, delta_x) in factors.items():
            raw_contributions[factor] = abs(d_y * delta_x)
        
        total_contrib = sum(raw_contributions.values())
        if total_contrib == 0.0:
            return {k: 0.0 for k in factors}
        
        return {k: round(v / total_contrib, 4) for k, v in raw_contributions.items()}

    def render_confluence_hint(
        self,
        dominant_factor: str,
        trigger_factor: str,
        containment_action: str,
        root_fix_action: str,
    ) -> List[str]:
        """Renders 2-phase Tier 2 directive separating immediate containment from root fix."""
        return [
            f"[CONFLUENCE_DETECTED: DOMINANT={dominant_factor}, TRIGGER={trigger_factor}]",
            f"[PHASE 1 - CONTAINMENT: EXECUTE {containment_action}]",
            f"[PHASE 2 - ROOT_FIX: EXECUTE {root_fix_action}]",
        ]

