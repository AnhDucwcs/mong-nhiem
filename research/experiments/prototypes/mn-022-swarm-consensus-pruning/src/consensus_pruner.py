"""Consensus Pruning Engine maintaining Vector Clock DAG and O(M) frontier compaction."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class SwarmEventNode:
    event_id: str
    tick: int
    agent_id: str
    action_type: str
    target: str
    vector_clock: Dict[str, int]
    parent_hashes: List[str]
    payload: Dict[str, Any]
    status: str  # COMMITTED, REJECTED
    node_hash: str = ""

    def compute_hash(self) -> str:
        body = {
            "tick": self.tick,
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "target": self.target,
            "vector_clock": dict(sorted(self.vector_clock.items())),
            "parent_hashes": sorted(self.parent_hashes),
        }
        encoded = json.dumps(body, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]


class ConsensusPruner:
    """Manages multi-agent Vector Clock causal DAG and prunes stable prefixes."""

    def __init__(self, agent_ids: List[str], frontier_window: int = 4) -> None:
        self.agent_ids = agent_ids
        self.frontier_window = frontier_window
        self.nodes: Dict[str, SwarmEventNode] = {}
        self.frontier_hashes: Set[str] = set()
        self.vector_clocks: Dict[str, Dict[str, int]] = {
            aid: {a: 0 for a in agent_ids} for aid in agent_ids
        }
        self.total_raw_events: int = 0
        self.pruned_events_count: int = 0

    def tick_agent_clock(self, agent_id: str) -> Dict[str, int]:
        """Increments agent's own component of the vector clock."""
        if agent_id in self.vector_clocks:
            self.vector_clocks[agent_id][agent_id] += 1
            return dict(self.vector_clocks[agent_id])
        return {agent_id: 1}

    def merge_clock(self, recipient_id: str, incoming_clock: Dict[str, int]) -> None:
        """Merges incoming vector clock into recipient's vector clock."""
        if recipient_id not in self.vector_clocks:
            self.vector_clocks[recipient_id] = {a: 0 for a in self.agent_ids}
        rec = self.vector_clocks[recipient_id]
        for aid, val in incoming_clock.items():
            rec[aid] = max(rec.get(aid, 0), val)

    def record_event(
        self,
        event_id: str,
        tick: int,
        agent_id: str,
        action_type: str,
        target: str,
        payload: Dict[str, Any],
        status: str = "COMMITTED",
    ) -> SwarmEventNode:
        """Records a committed event into the causal DAG and updates frontier."""
        self.total_raw_events += 1
        clock = self.tick_agent_clock(agent_id)
        parent_hashes = list(self.frontier_hashes)

        node = SwarmEventNode(
            event_id=event_id,
            tick=tick,
            agent_id=agent_id,
            action_type=action_type,
            target=target,
            vector_clock=clock,
            parent_hashes=parent_hashes,
            payload=payload,
            status=status,
        )
        node.node_hash = node.compute_hash()
        self.nodes[node.node_hash] = node

        # Update frontier: new node replaces its direct parents in frontier
        self.frontier_hashes.difference_update(parent_hashes)
        self.frontier_hashes.add(node.node_hash)
        return node

    def prune_frontier(self, current_tick: int) -> List[SwarmEventNode]:
        """Prunes finalized historical branches older than current_tick - frontier_window.
        
        Returns active frontier nodes for prompt delivery (O(M)).
        """
        min_active_tick = max(0, current_tick - self.frontier_window)
        active_nodes: List[SwarmEventNode] = []

        # Identify nodes that are either in current frontier or recent enough
        for nhash in list(self.frontier_hashes):
            node = self.nodes.get(nhash)
            if node and node.tick >= min_active_tick:
                active_nodes.append(node)

        # Count how many historical nodes are pruned from active context
        self.pruned_events_count = max(0, len(self.nodes) - len(active_nodes))
        return sorted(active_nodes, key=lambda n: (n.tick, n.event_id))

    def get_compaction_metrics(self) -> Dict[str, float]:
        """Computes compaction efficiency metrics."""
        raw = max(1, self.total_raw_events)
        retained = max(1, len(self.frontier_hashes))
        compaction = max(0.0, (raw - retained) / raw)
        return {
            "total_raw_events": float(raw),
            "active_frontier_nodes": float(retained),
            "compaction_ratio": round(compaction, 4),
        }
