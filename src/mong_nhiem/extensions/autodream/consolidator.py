"""AutoDream episodic consolidation and frontier branch pruning primitives."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple


class FrontierBranchPruner:
    """Collapses O(M^2) full distributed gossip histories into O(M) frontier heads."""

    def __init__(self, frontier_window: int = 4):
        self.frontier_window = frontier_window
        self.frontier_hashes: Set[str] = set()
        self.total_raw_events: int = 0
        self.pruned_events_count: int = 0

    def update_frontier(
        self,
        new_event_hash: str,
        parent_hashes: List[str],
    ) -> None:
        """Updates frontier by adding the new node and removing its direct causal parents."""
        self.total_raw_events += 1
        self.frontier_hashes.difference_update(parent_hashes)
        self.frontier_hashes.add(new_event_hash)

    def prune_frontier(
        self,
        nodes: Dict[str, Any],
        current_tick: int,
    ) -> List[Any]:
        """Prunes finalized historical branches older than current_tick - frontier_window.
        
        Args:
            nodes: Map of event_hash -> event object (must have .tick and .signature/event_id).
            current_tick: Current simulation/environment tick.
            
        Returns:
            Sorted list of active frontier events within the active window (O(M)).
        """
        min_active_tick = max(0, current_tick - self.frontier_window)
        active_nodes: List[Any] = []

        for fhash in list(self.frontier_hashes):
            node = nodes.get(fhash)
            if node is not None:
                tick = getattr(node, "tick", getattr(node, "get", lambda k, d=0: d)("tick", 0))
                if tick >= min_active_tick:
                    active_nodes.append(node)

        self.pruned_events_count = max(0, len(nodes) - len(active_nodes))
        return sorted(
            active_nodes,
            key=lambda n: (
                getattr(n, "tick", getattr(n, "get", lambda k, d=0: d)("tick", 0)),
                str(getattr(n, "event_id", getattr(n, "get", lambda k, d="": d)("event_id", ""))),
            ),
        )

    def get_compaction_metrics(self) -> Dict[str, float]:
        """Calculates historical compaction efficiency metrics."""
        raw = max(1, self.total_raw_events)
        retained = max(1, len(self.frontier_hashes))
        compaction = max(0.0, (raw - retained) / raw)
        return {
            "total_raw_events": float(raw),
            "active_frontier_nodes": float(retained),
            "pruned_events_count": float(self.pruned_events_count),
            "compaction_ratio": round(compaction, 4),
        }


class AutoDreamConsolidator:
    """Synthesizes raw episodic interaction sequences into consolidated semantic state cards."""

    def __init__(self, target_compaction_ratio: float = 0.70):
        self.target_compaction_ratio = target_compaction_ratio

    @staticmethod
    def calculate_compaction_ratio(raw_count: int, consolidated_count: int) -> float:
        """Computes compaction ratio (1 - consolidated / raw)."""
        if raw_count <= 0:
            return 0.0
        return max(0.0, (raw_count - consolidated_count) / raw_count)

    def consolidate_episodes(
        self,
        event_log: List[Dict[str, Any]],
        terminal_status_filter: Optional[Set[str]] = None,
    ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, float]]:
        """Consolidates an event stream into the latest authoritative entity state.
        
        Reduces fine-grained mutation steps into the latest ground-truth entity snapshot,
        achieving >= 70% compaction on long-horizon multi-turn traces.
        
        Args:
            event_log: Chronological list of events with keys: 'target', 'action_type', 'payload', 'tick', 'status'.
            terminal_status_filter: Set of event statuses to process (defaults to COMMITTED / SUCCESS).
            
        Returns:
            (consolidated_entity_states, compaction_metrics)
        """
        valid_statuses = terminal_status_filter or {"COMMITTED", "SUCCESS", "EXECUTED"}
        consolidated: Dict[str, Dict[str, Any]] = {}
        processed_count = 0

        for event in event_log:
            status = event.get("status", "COMMITTED")
            if status not in valid_statuses:
                continue

            processed_count += 1
            target = event.get("target") or "system"
            action_type = event.get("action_type", "MUTATE")
            payload = event.get("payload", {})
            tick = event.get("tick", 0)

            if target not in consolidated:
                consolidated[target] = {
                    "entity_id": target,
                    "last_action": action_type,
                    "last_tick": tick,
                    "version": 1,
                    "properties": {},
                }
            else:
                consolidated[target]["last_action"] = action_type
                consolidated[target]["last_tick"] = tick
                consolidated[target]["version"] += 1

            if isinstance(payload, dict):
                consolidated[target]["properties"].update(payload)

        raw_count = len(event_log)
        out_count = len(consolidated)
        compaction = self.calculate_compaction_ratio(raw_count, out_count)

        metrics = {
            "raw_event_count": float(raw_count),
            "consolidated_entity_count": float(out_count),
            "compaction_ratio": round(compaction, 4),
            "target_compaction_met": float(compaction >= self.target_compaction_ratio),
        }
        return consolidated, metrics
