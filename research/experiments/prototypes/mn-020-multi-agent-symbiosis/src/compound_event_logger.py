"""Cryptographic Multi-Actor Compound Event Logger and DAG Provenance Tracker."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CompoundCausalEvent:
    event_id: str
    tick: int
    event_type: str  # "ACTION", "COMPOUND_ACTION", "LEASE_ACQUIRE", "LEASE_RELEASE", "SIGNAL", "CONCURRENCY_BLOCKED", "TICK_DECAY"
    actor_id: str   # "agent_1", "agent_2", "host", "environment", "human_supervisor"
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
            "actor_id": self.actor_id,
            "entity_id": self.entity_id,
            "pre_state": self.pre_state,
            "post_state": self.post_state,
            "delta_signature": self.delta_signature,
            "triggering_action": self.triggering_action,
            "causal_parent_hashes": sorted(self.causal_parent_hashes),
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class CompoundEventLogger:
    """DAG-based immutable multi-actor provenance logger."""

    def __init__(self):
        self.events: List[CompoundCausalEvent] = []
        self.events_by_hash: Dict[str, CompoundCausalEvent] = {}
        self.events_by_entity: Dict[str, List[CompoundCausalEvent]] = {}
        self.events_by_actor: Dict[str, List[CompoundCausalEvent]] = {}
        self.latest_hash_per_entity: Dict[str, str] = {}
        self.latest_hash_per_actor: Dict[str, str] = {}

    def record_event(
        self,
        tick: int,
        event_type: str,
        actor_id: str,
        entity_id: str,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        triggering_action: Optional[str] = None,
        delta_signature: Optional[Dict[str, Any]] = None,
    ) -> CompoundCausalEvent:
        event_id = f"EVT-{len(self.events) + 1:04d}"
        parents: List[str] = []

        # Parent links: latest event on this entity + latest event by this actor
        if entity_id in self.latest_hash_per_entity:
            parents.append(self.latest_hash_per_entity[entity_id])
        if actor_id in self.latest_hash_per_actor:
            actor_parent = self.latest_hash_per_actor[actor_id]
            if actor_parent not in parents:
                parents.append(actor_parent)

        if delta_signature is None:
            delta_signature = {}
            for k, post_v in post_state.items():
                pre_v = pre_state.get(k)
                if pre_v != post_v:
                    delta_signature[k] = {"from": pre_v, "to": post_v}

        event = CompoundCausalEvent(
            event_id=event_id,
            tick=tick,
            event_type=event_type,
            actor_id=actor_id,
            entity_id=entity_id,
            pre_state=pre_state,
            post_state=post_state,
            delta_signature=delta_signature,
            triggering_action=triggering_action,
            causal_parent_hashes=parents,
        )
        event.event_hash = event.compute_hash()

        self.events.append(event)
        self.events_by_hash[event.event_hash] = event
        self.events_by_entity.setdefault(entity_id, []).append(event)
        self.events_by_actor.setdefault(actor_id, []).append(event)
        self.latest_hash_per_entity[entity_id] = event.event_hash
        self.latest_hash_per_actor[actor_id] = event.event_hash

        return event

    def record_compound_action(
        self,
        tick: int,
        primary_actor: str,
        secondary_actor: str,
        shared_entity: str,
        primary_action: str,
        secondary_action: str,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
    ) -> CompoundCausalEvent:
        """Record joint emergent event triggered by interleaved concurrent actions."""
        return self.record_event(
            tick=tick,
            event_type="COMPOUND_ACTION",
            actor_id=f"{primary_actor}+{secondary_actor}",
            entity_id=shared_entity,
            pre_state=pre_state,
            post_state=post_state,
            triggering_action=f"{primary_action} & {secondary_action}",
        )

    def verify_dag_integrity(self) -> bool:
        """Cryptographically verify all event hashes and causal parent references."""
        for evt in self.events:
            if evt.compute_hash() != evt.event_hash:
                return False
            for parent_h in evt.causal_parent_hashes:
                if parent_h not in self.events_by_hash:
                    return False
        return True
