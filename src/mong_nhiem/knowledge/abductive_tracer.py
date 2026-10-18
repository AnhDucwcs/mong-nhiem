"""Host Abductive Causal Tracer and Confluence Decomposer.

Performs backward reachability analysis on causal dependency graphs, linking observed
symptoms to concealed root causes with cycle termination and marginal sensitivity attribution.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class CausalDependency:
    """Represents a directed causal link between an intervention and a downstream symptom."""

    source_partition: str
    source_action: str
    target_partition: str
    resulting_symptom: str
    mitigation_action: str


class AbductiveCausalTracer:
    """Traces observed symptom anomalies back to concealed cross-partition actions."""

    def __init__(
        self, dependencies: Optional[List[CausalDependency]] = None
    ) -> None:
        self.dependencies: List[CausalDependency] = (
            list(dependencies) if dependencies is not None else []
        )
        self.event_history: List[Dict[str, Any]] = []

    def register_dependency(self, dependency: CausalDependency) -> None:
        """Registers a cross-partition causal dependency rule."""
        self.dependencies.append(dependency)

    def record_action(self, partition: str, action: str, tick: int) -> None:
        """Records an executed action into the host event history."""
        clean_action = action.replace("ACTION:", "").strip()
        self.event_history.append({
            "partition": partition,
            "action": clean_action,
            "tick": tick,
        })

    def trace_symptom(
        self,
        symptom: str,
        reporting_partition: str,
        visited: Optional[Set[str]] = None,
    ) -> Optional[Tuple[str, str, str]]:
        """Given a reported symptom in reporting_partition, returns (source_partition, root_action, mitigation_action).

        Includes cycle detection via visited set to cleanly terminate feedback loops (A -> B -> A).
        """
        if visited is None:
            visited = set()

        clean_symptom = symptom.replace("ANOMALY:", "").strip()
        state_key = f"{reporting_partition}:{clean_symptom}"

        if state_key in visited:
            # Feedback loop cycle detected: break recursion to prevent infinite loops
            return None
        visited.add(state_key)

        for dep in self.dependencies:
            if (
                dep.target_partition == reporting_partition
                and dep.resulting_symptom == clean_symptom
            ):
                # Search event history in reverse for the causal intervention
                for ev in reversed(self.event_history):
                    if (
                        ev["partition"] == dep.source_partition
                        and ev["action"] == dep.source_action
                    ):
                        return (dep.source_partition, dep.source_action, dep.mitigation_action)

                # If not found in history, return dependency structural mapping
                return (dep.source_partition, dep.source_action, dep.mitigation_action)

        return None

    def compute_confluence_attribution(
        self, factors: Dict[str, Tuple[float, float]]
    ) -> Dict[str, float]:
        """Computes marginal contribution weights for multi-parent confluence symptoms.

        Args:
            factors: Dict mapping factor_name -> (marginal_derivative dY/dXi, delta_Xi)

        Returns:
            Dict mapping factor_name -> normalized contribution weight in [0.0, 1.0]
        """
        raw_contributions: Dict[str, float] = {}
        for factor, (d_y, delta_x) in factors.items():
            raw_contributions[factor] = abs(d_y * delta_x)

        total_contrib = sum(raw_contributions.values())
        if total_contrib == 0.0:
            return {k: 0.0 for k in factors}

        return {k: round(v / total_contrib, 4) for k, v in raw_contributions.items()}

    def render_abductive_hint(
        self, source_partition: str, root_action: str, mitigation: str
    ) -> str:
        """Renders compact Tier 2 hint for the responsible agent."""
        return f"[ABDUCTIVE_HINT: {root_action} in {source_partition} -> EXECUTE {mitigation}]"

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
