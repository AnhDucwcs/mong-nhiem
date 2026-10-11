"""Cryptographic Causal Event Logger and DAG Provenance Tracker for Stage 3."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CausalEvent:
    event_id: str
    tick: int
    event_type: str  # "ACTION", "EMERGE", "MUTATE_SCHEMA", "RETIRE", "TRAP_TRIGGER"
    entity_id: str
    pre_state: Dict[str, Any]
    post_state: Dict[str, Any]
    delta_signature: Dict[str, Any] = field(default_factory=dict)
    triggering_action: Optional[str] = None
    causal_parent_hashes: List[str] = field(default_factory=list)
    event_hash: str = ""

    def compute_hash(self) -> str:
        payload = {
            "event_id": self.event_id,
            "tick": self.tick,
            "event_type": self.event_type,
            "entity_id": self.entity_id,
            "pre_state": self.pre_state,
            "post_state": self.post_state,
            "delta_signature": self.delta_signature,
            "triggering_action": self.triggering_action,
            "causal_parent_hashes": sorted(self.causal_parent_hashes),
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class CausalEventLog:
    """DAG-based immutable event log for counterfactual causal rule induction."""

    def __init__(self):
        self.events: List[CausalEvent] = []
        self.events_by_hash: Dict[str, CausalEvent] = {}
        self.events_by_entity: Dict[str, List[CausalEvent]] = {}
        self.latest_hash_per_entity: Dict[str, str] = {}

    def record_event(
        self,
        tick: int,
        event_type: str,
        entity_id: str,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        triggering_action: Optional[str] = None,
        delta_signature: Optional[Dict[str, Any]] = None,
    ) -> CausalEvent:
        event_id = f"EVT-{len(self.events) + 1:04d}"
        parents: List[str] = []
        if entity_id in self.latest_hash_per_entity:
            parents.append(self.latest_hash_per_entity[entity_id])

        # Compute delta signature if not provided
        if delta_signature is None:
            delta_signature = {}
            for k, v in post_state.get("properties", {}).items():
                old_v = pre_state.get("properties", {}).get(k)
                if old_v != v:
                    delta_signature[k] = {"from": old_v, "to": v}

        evt = CausalEvent(
            event_id=event_id,
            tick=tick,
            event_type=event_type,
            entity_id=entity_id,
            pre_state=pre_state,
            post_state=post_state,
            delta_signature=delta_signature,
            triggering_action=triggering_action,
            causal_parent_hashes=parents,
        )
        evt.event_hash = evt.compute_hash()

        self.events.append(evt)
        self.events_by_hash[evt.event_hash] = evt
        self.latest_hash_per_entity[entity_id] = evt.event_hash

        if entity_id not in self.events_by_entity:
            self.events_by_entity[entity_id] = []
        self.events_by_entity[entity_id].append(evt)

        return evt

    def get_causal_chain(self, event_hash: str) -> List[CausalEvent]:
        """Traverse ancestors in the causal DAG backwards from event_hash."""
        chain: List[CausalEvent] = []
        visited = set()
        queue = [event_hash]

        while queue:
            curr_h = queue.pop(0)
            if curr_h in visited or curr_h not in self.events_by_hash:
                continue
            visited.add(curr_h)
            evt = self.events_by_hash[curr_h]
            chain.append(evt)
            queue.extend(evt.causal_parent_hashes)

        return chain

    def to_list(self) -> List[Dict[str, Any]]:
        return [asdict(e) for e in self.events]
