"""Deterministic Epistemic Reconciler Engine for MN-021.

Resolves observation discrepancies between peer agents across temporal windows [t_A, t_B],
distinguishing legitimate temporal state evolution (A -> p -> B) from unobserved anomalies,
and generating compact causal delta notices.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

try:
    from causal_dag import CausalEventDAG, CausalNode
except ImportError:
    from .causal_dag import CausalEventDAG, CausalNode


@dataclass
class EpistemicObservation:
    """An agent's private local observation of an entity state at a specific tick."""
    observation_id: str
    observer: str
    target_entity: str
    observed_tick: int
    observed_attributes: Dict[str, Any]


@dataclass
class ReconciliationResult:
    """Result of host-authoritative discrepancy reconciliation."""
    status: str  # NOMINAL_MATCH | TEMPORAL_EVOLUTION | CONTESTED_ANOMALY
    target_entity: str
    earlier_obs: EpistemicObservation
    later_obs: EpistemicObservation
    intervening_event: Optional[CausalNode] = None
    causal_edge_added: bool = False
    delta_notice_for_earlier: Optional[str] = None


class EpistemicReconciler:
    """Deterministic 3-step temporal-causal reconciliation engine."""

    def __init__(self):
        self._contested_entities: Dict[str, str] = {}
        self._reconciliation_history: List[ReconciliationResult] = []

    def is_entity_contested(self, entity_id: str) -> bool:
        """Check if an entity is currently marked with an unverified discrepancy."""
        return entity_id in self._contested_entities

    def clear_contested_status(self, entity_id: str):
        """Clear contested status following a successful ground truth cross-inspection."""
        self._contested_entities.pop(entity_id, None)

    def reconcile_observations(
        self,
        obs_1: EpistemicObservation,
        obs_2: EpistemicObservation,
        event_dag: CausalEventDAG,
    ) -> ReconciliationResult:
        """Execute 3-step deterministic reconciliation between two peer observations."""
        # Step 1: Order observations chronologically
        if obs_1.observed_tick <= obs_2.observed_tick:
            earlier, later = obs_1, obs_2
        else:
            earlier, later = obs_2, obs_1

        target = earlier.target_entity

        # Check for direct attribute equivalence
        diffs = self._find_attribute_diffs(earlier.observed_attributes, later.observed_attributes)
        if not diffs:
            result = ReconciliationResult(
                status="NOMINAL_MATCH",
                target_entity=target,
                earlier_obs=earlier,
                later_obs=later,
            )
            self._reconciliation_history.append(result)
            return result

        # Step 2: Temporal window slicing and event DAG traversal
        t_start = earlier.observed_tick
        t_end = later.observed_tick
        window_events = event_dag.get_events_for_entity_in_window(target, t_start, t_end)

        # Look for an event that accounts for the attribute mutation
        matching_event = None
        for evt in window_events:
            for diff_k in diffs.keys():
                if diff_k in evt.state_delta:
                    matching_event = evt
                    break
            if matching_event:
                break

        # Step 3: Classify discrepancy
        if matching_event:
            # Legitimate state evolution: both agents are correct in their respective timeframes
            delta_str = ", ".join(f"{k}:{v[1]}" for k, v in diffs.items())
            notice = (
                f"[UPDATE: {target} evolved ({delta_str}) "
                f"due to {matching_event.action_name} at t={matching_event.tick}]"
            )
            result = ReconciliationResult(
                status="TEMPORAL_EVOLUTION",
                target_entity=target,
                earlier_obs=earlier,
                later_obs=later,
                intervening_event=matching_event,
                causal_edge_added=True,
                delta_notice_for_earlier=notice,
            )
            # Remove from contested if previously flagged
            self.clear_contested_status(target)
        else:
            # Unaccounted discrepancy: flag as contested anomaly requiring cross-inspection
            self._contested_entities[target] = f"Observed diffs: {diffs} between t={t_start} and t={t_end}"
            result = ReconciliationResult(
                status="CONTESTED_ANOMALY",
                target_entity=target,
                earlier_obs=earlier,
                later_obs=later,
                delta_notice_for_earlier=f"[CONTESTED_ANOMALY: Discrepancy on {target}. ACTION: CROSS_INSPECT required.]",
            )

        self._reconciliation_history.append(result)
        return result

    @staticmethod
    def _find_attribute_diffs(
        dict_a: Dict[str, Any],
        dict_b: Dict[str, Any],
    ) -> Dict[str, Tuple[Any, Any]]:
        """Identify keys where values differ between two attribute snapshots."""
        diffs = {}
        all_keys = set(dict_a.keys()).union(set(dict_b.keys()))
        for k in all_keys:
            val_a = dict_a.get(k)
            val_b = dict_b.get(k)
            if val_a != val_b:
                diffs[k] = (val_a, val_b)
        return diffs
