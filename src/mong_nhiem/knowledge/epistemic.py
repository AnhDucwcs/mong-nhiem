"""Epistemic discrepancy reconciliation across asynchronous agent observations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .causal_dag import CausalEventDAG, CausalNode


@dataclass
class EpistemicObservation:
    """An agent's local observation of an entity state at a specific tick."""

    observation_id: str
    observer: str
    target_entity: str
    observed_tick: int
    observed_attributes: Dict[str, Any]


@dataclass
class ReconciliationResult:
    """Result of host-authoritative temporal discrepancy reconciliation."""

    status: str  # NOMINAL_MATCH | TEMPORAL_EVOLUTION | CONTESTED_ANOMALY
    target_entity: str
    earlier_obs: EpistemicObservation
    later_obs: EpistemicObservation
    intervening_event: Optional[CausalNode] = None
    causal_edge_added: bool = False
    delta_notice_for_earlier: Optional[str] = None


class EpistemicReconciler:
    """Reconciles disparate agent observations over temporal windows [t_A, t_B]."""

    def __init__(self):
        self._contested_entities: Dict[str, str] = {}
        self._reconciliation_history: List[ReconciliationResult] = []

    def is_entity_contested(self, entity_id: str) -> bool:
        """Returns True if the entity is currently flagged with an unresolved anomaly."""
        return entity_id in self._contested_entities

    def clear_contested_status(self, entity_id: str) -> None:
        """Clears contested flag following ground truth cross-inspection or sync."""
        self._contested_entities.pop(entity_id, None)

    @staticmethod
    def find_attribute_diffs(
        dict_a: Dict[str, Any],
        dict_b: Dict[str, Any],
    ) -> Dict[str, Tuple[Any, Any]]:
        """Identifies differing key-value pairs between two attribute snapshots."""
        diffs = {}
        all_keys = set(dict_a.keys()).union(dict_b.keys())
        for k in all_keys:
            val_a = dict_a.get(k)
            val_b = dict_b.get(k)
            if val_a != val_b:
                diffs[k] = (val_a, val_b)
        return diffs

    def reconcile_observations(
        self,
        obs_1: EpistemicObservation,
        obs_2: EpistemicObservation,
        event_dag: CausalEventDAG,
    ) -> ReconciliationResult:
        """Executes 3-step deterministic reconciliation between two peer observations."""
        if obs_1.observed_tick <= obs_2.observed_tick:
            earlier, later = obs_1, obs_2
        else:
            earlier, later = obs_2, obs_1

        target = earlier.target_entity
        diffs = self.find_attribute_diffs(earlier.observed_attributes, later.observed_attributes)

        if not diffs:
            result = ReconciliationResult(
                status="NOMINAL_MATCH",
                target_entity=target,
                earlier_obs=earlier,
                later_obs=later,
            )
            self._reconciliation_history.append(result)
            return result

        t_start = earlier.observed_tick
        t_end = later.observed_tick
        window_events = event_dag.get_events_for_entity_in_window(target, t_start, t_end)

        matching_event: Optional[CausalNode] = None
        for evt in window_events:
            for diff_k in diffs.keys():
                if diff_k in evt.state_delta:
                    matching_event = evt
                    break
            if matching_event:
                break

        if matching_event:
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
            self.clear_contested_status(target)
        else:
            self._contested_entities[target] = f"Diffs: {diffs} between t={t_start} and t={t_end}"
            result = ReconciliationResult(
                status="CONTESTED_ANOMALY",
                target_entity=target,
                earlier_obs=earlier,
                later_obs=later,
                delta_notice_for_earlier=f"[CONTESTED_ANOMALY: Discrepancy on {target}. ACTION: CROSS_INSPECT required.]",
            )

        self._reconciliation_history.append(result)
        return result
