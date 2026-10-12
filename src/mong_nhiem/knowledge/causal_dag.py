"""Multi-Parent Causal Event Directed Acyclic Graph (DAG) Subsystem."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class CausalNode:
    """A single immutable event node within the Causal DAG."""

    event_id: str
    parent_ids: List[str]
    tick: int
    actor: str
    action_name: str
    target_entity: str
    state_delta: Dict[str, Any]
    parent_hash: str
    node_hash: str = ""

    def __post_init__(self):
        if not self.node_hash:
            self.node_hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Computes deterministic SHA-256 cryptographic fingerprint."""
        payload = {
            "event_id": self.event_id,
            "parent_ids": sorted(self.parent_ids),
            "tick": self.tick,
            "actor": self.actor,
            "action_name": self.action_name,
            "target_entity": self.target_entity,
            "state_delta": self.state_delta,
            "parent_hash": self.parent_hash,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes node to dictionary."""
        return asdict(self)


class CausalEventDAG:
    """Host-authoritative Multi-Parent Causal Event DAG."""

    def __init__(self):
        self._nodes: Dict[str, CausalNode] = {}
        self._children: Dict[str, List[str]] = {}
        self._entity_index: Dict[str, List[str]] = {}
        self._event_counter = 0

    def add_event(
        self,
        actor: str,
        action_name: str,
        target_entity: str,
        state_delta: Optional[Dict[str, Any]] = None,
        parent_ids: Optional[List[str]] = None,
        tick: int = 0,
        custom_id: Optional[str] = None,
    ) -> CausalNode:
        """Appends an immutable event node into the causal DAG, chaining parent hashes."""
        parents = sorted(parent_ids or [])
        for pid in parents:
            if pid not in self._nodes:
                raise KeyError(f"Parent event '{pid}' does not exist in CausalEventDAG.")

        self._event_counter += 1
        event_id = custom_id or f"evt_{self._event_counter:04d}_{action_name.lower()}"

        if not parents:
            parent_hash = "0" * 64
        else:
            parent_hashes = [self._nodes[pid].node_hash for pid in parents]
            combined = ":".join(sorted(parent_hashes)).encode("utf-8")
            parent_hash = hashlib.sha256(combined).hexdigest()

        node = CausalNode(
            event_id=event_id,
            parent_ids=parents,
            tick=tick,
            actor=actor,
            action_name=action_name,
            target_entity=target_entity,
            state_delta=state_delta or {},
            parent_hash=parent_hash,
        )

        self._nodes[event_id] = node
        self._children[event_id] = []
        for pid in parents:
            self._children[pid].append(event_id)

        if target_entity not in self._entity_index:
            self._entity_index[target_entity] = []
        self._entity_index[target_entity].append(event_id)

        return node

    def get_event(self, event_id: str) -> Optional[CausalNode]:
        """Retrieves a node by its event ID."""
        return self._nodes.get(event_id)

    def get_events_for_entity(self, entity_id: str) -> List[CausalNode]:
        """Retrieves all events affecting an entity in chronological order."""
        event_ids = self._entity_index.get(entity_id, [])
        return [self._nodes[eid] for eid in event_ids]

    def get_events_for_entity_in_window(
        self,
        entity_id: str,
        t_start: int,
        t_end: int,
    ) -> List[CausalNode]:
        """Retrieves events affecting an entity within the closed temporal window [t_start, t_end]."""
        events = self.get_events_for_entity(entity_id)
        return [e for e in events if t_start <= e.tick <= t_end]

    def get_k_hop_ancestors(self, event_id: str, k_hops: int = 2) -> List[CausalNode]:
        """Extracts k-hop causal ancestors of a specific event node."""
        if event_id not in self._nodes:
            return []

        visited: Set[str] = set()
        queue = [(event_id, 0)]
        result_ids: List[str] = []

        while queue:
            curr_id, depth = queue.pop(0)
            if curr_id not in visited and curr_id != event_id:
                visited.add(curr_id)
                result_ids.append(curr_id)

            if depth < k_hops:
                node = self._nodes.get(curr_id)
                if node:
                    for pid in node.parent_ids:
                        if pid not in visited:
                            queue.append((pid, depth + 1))

        nodes = [self._nodes[eid] for eid in result_ids]
        return sorted(nodes, key=lambda x: (x.tick, x.event_id))

    def get_topological_order(self) -> List[CausalNode]:
        """Returns all nodes in valid topological causal order."""
        in_degree: Dict[str, int] = {eid: len(n.parent_ids) for eid, n in self._nodes.items()}
        zero_in = [eid for eid, deg in in_degree.items() if deg == 0]
        topo_ids: List[str] = []

        while zero_in:
            curr = zero_in.pop(0)
            topo_ids.append(curr)
            for child in self._children.get(curr, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    zero_in.append(child)

        return [self._nodes[eid] for eid in topo_ids]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the entire DAG for audit logging and provenance verification."""
        return {
            "total_nodes": len(self._nodes),
            "nodes": [n.to_dict() for n in self._nodes.values()],
        }

    def __len__(self) -> int:
        return len(self._nodes)
