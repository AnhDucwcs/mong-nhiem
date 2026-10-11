"""Immutable Causal Event Provenance Logger.

Records atomic lifecycle and state transition events with explicit causal DAG links,
providing the empirical provenance substrate for Stage 3 counterfactual causal induction.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CausalEvent:
    """Atomic state transition or schema lifecycle event with causal DAG provenance."""
    event_id: str
    tick: int
    event_type: str  # 'ACTION', 'EMERGE', 'MUTATE_SCHEMA', 'DECAY', 'RETIRE'
    entity_id: str
    pre_state: Dict[str, Any]
    post_state: Dict[str, Any]
    causal_parents: List[str] = field(default_factory=list)  # IDs of events directly triggering this event
    triggering_action: Optional[str] = None
    delta_signature: Dict[str, Any] = field(default_factory=dict)
    event_hash: str = ""

    def compute_hash(self, prev_hash: str = "") -> str:
        """Compute tamper-evident SHA-256 fingerprint chained to predecessor."""
        data = {
            "event_id": self.event_id,
            "tick": self.tick,
            "event_type": self.event_type,
            "entity_id": self.entity_id,
            "pre_state": self.pre_state,
            "post_state": self.post_state,
            "causal_parents": sorted(self.causal_parents),
            "triggering_action": self.triggering_action,
            "delta_signature": self.delta_signature,
            "prev_hash": prev_hash,
        }
        encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "tick": self.tick,
            "event_type": self.event_type,
            "entity_id": self.entity_id,
            "pre_state": copy.deepcopy(self.pre_state),
            "post_state": copy.deepcopy(self.post_state),
            "causal_parents": list(self.causal_parents),
            "triggering_action": self.triggering_action,
            "delta_signature": copy.deepcopy(self.delta_signature),
            "event_hash": self.event_hash,
        }


class CausalEventLog:
    """Thread-safe append-only DAG-linked event stream for causal reasoning."""

    def __init__(self) -> None:
        self.events: List[CausalEvent] = []
        self._events_by_id: Dict[str, CausalEvent] = {}
        self._events_by_entity: Dict[str, List[str]] = {}
        self._last_hash: str = "0" * 64
        self._event_counter: int = 0

    def record_event(
        self,
        tick: int,
        event_type: str,
        entity_id: str,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        causal_parents: Optional[List[str]] = None,
        triggering_action: Optional[str] = None,
        delta_signature: Optional[Dict[str, Any]] = None,
    ) -> CausalEvent:
        """Record and append a causal event to the immutable provenance DAG."""
        self._event_counter += 1
        event_id = f"CEVT-{tick:04d}-{self._event_counter:04d}"

        # If no explicit parents supplied, link to the most recent event for this entity
        parents = list(causal_parents) if causal_parents else []
        if not parents and entity_id in self._events_by_entity and self._events_by_entity[entity_id]:
            parents.append(self._events_by_entity[entity_id][-1])

        event = CausalEvent(
            event_id=event_id,
            tick=tick,
            event_type=event_type,
            entity_id=entity_id,
            pre_state=copy.deepcopy(pre_state),
            post_state=copy.deepcopy(post_state),
            causal_parents=parents,
            triggering_action=triggering_action,
            delta_signature=copy.deepcopy(delta_signature or {}),
        )
        event.event_hash = event.compute_hash(self._last_hash)
        self._last_hash = event.event_hash

        self.events.append(event)
        self._events_by_id[event_id] = event
        if entity_id not in self._events_by_entity:
            self._events_by_entity[entity_id] = []
        self._events_by_entity[entity_id].append(event_id)

        return event

    def get_event(self, event_id: str) -> Optional[CausalEvent]:
        return self._events_by_id.get(event_id)

    def get_entity_history(self, entity_id: str) -> List[CausalEvent]:
        ids = self._events_by_entity.get(entity_id, [])
        return [self._events_by_id[eid] for eid in ids]

    def get_causal_chain(self, event_id: str, max_depth: int = 10) -> List[CausalEvent]:
        """Walk up the causal parent DAG to trace root causality."""
        visited = set()
        chain = []
        queue = [event_id]

        depth = 0
        while queue and depth < max_depth:
            curr_id = queue.pop(0)
            if curr_id in visited or curr_id not in self._events_by_id:
                continue
            visited.add(curr_id)
            ev = self._events_by_id[curr_id]
            chain.append(ev)
            queue.extend(ev.causal_parents)
            depth += 1

        return chain

    def export_causal_traces(self) -> List[Dict[str, Any]]:
        """Serialize complete provenance DAG for Stage 3 causal rule induction."""
        return [ev.to_dict() for ev in self.events]
