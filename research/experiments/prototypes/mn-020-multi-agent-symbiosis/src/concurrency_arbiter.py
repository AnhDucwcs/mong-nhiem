"""Host-Authoritative Concurrency Arbiter and Entity Lease Manager.

Provides optimistic locking, deterministic lease expiration, wait-for cycle deadlock
detection, and discrete inter-agent signalling without unconstrained text chat.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class EntityLease:
    entity_id: str
    holder_id: str
    acquired_tick: int
    ttl: int  # Ticks until automatic lease expiration

    def is_expired(self, current_tick: int) -> bool:
        return current_tick >= (self.acquired_tick + self.ttl)


@dataclass
class AgentSignal:
    sender_id: str
    receiver_id: str
    signal_type: str  # "YIELD_REQUEST", "LEASE_GRANTED", "PHASE_SYNC", "HAZARD_ALERT"
    target_entity: Optional[str] = None
    tick: int = 0


class ConcurrencyArbiter:
    """Arbiter managing shared entity leases, race protection, and discrete signalling."""

    def __init__(self, default_ttl: int = 4):
        self.default_ttl = default_ttl
        self.leases: Dict[str, EntityLease] = {}
        self.signals_inbox: Dict[str, List[AgentSignal]] = {}
        self.contested_attempts_count = 0
        self.leases_granted_count = 0
        self.deadlock_cycles_detected = 0

    def request_lease(
        self,
        actor_id: str,
        entity_id: str,
        current_tick: int,
        ttl: Optional[int] = None,
    ) -> bool:
        """Attempt to acquire a mutually exclusive lease on an entity."""
        ttl = ttl or self.default_ttl

        # Check existing lease
        existing = self.leases.get(entity_id)
        if existing:
            if existing.is_expired(current_tick):
                # Expired lease automatically yields
                del self.leases[entity_id]
            elif existing.holder_id == actor_id:
                # Renew lease
                existing.acquired_tick = current_tick
                existing.ttl = ttl
                return True
            else:
                # Contested: owned by another actor
                self.contested_attempts_count += 1
                return False

        # Grant new lease
        self.leases[entity_id] = EntityLease(
            entity_id=entity_id,
            holder_id=actor_id,
            acquired_tick=current_tick,
            ttl=ttl,
        )
        self.leases_granted_count += 1
        return True

    def release_lease(self, actor_id: str, entity_id: str) -> bool:
        """Explicitly release an entity lease."""
        existing = self.leases.get(entity_id)
        if existing and existing.holder_id == actor_id:
            del self.leases[entity_id]
            return True
        return False

    def can_mutate(self, actor_id: str, entity_id: str, current_tick: int) -> bool:
        """Check if actor is permitted to dispatch write operations on entity."""
        existing = self.leases.get(entity_id)
        if not existing or existing.is_expired(current_tick):
            return True  # Uncontested entity
        return existing.holder_id == actor_id

    def get_lease_holder(self, entity_id: str, current_tick: int) -> Optional[str]:
        """Return the current active lease holder, or None if free."""
        existing = self.leases.get(entity_id)
        if existing and not existing.is_expired(current_tick):
            return existing.holder_id
        return None

    def tick_maintenance(self, current_tick: int) -> List[str]:
        """Prune expired leases and return list of expired entity IDs."""
        expired = []
        for eid, lease in list(self.leases.items()):
            if lease.is_expired(current_tick):
                expired.append(eid)
                del self.leases[eid]
        return expired

    def detect_wait_for_deadlocks(self, wait_for_edges: Dict[str, str]) -> List[List[str]]:
        """Detect cycles in wait-for graph: {waiting_actor: holder_actor}."""
        cycles = []
        visited = set()

        for start_node in wait_for_edges:
            if start_node in visited:
                continue
            path = []
            curr = start_node
            while curr in wait_for_edges:
                if curr in path:
                    # Cycle detected
                    idx = path.index(curr)
                    cycle = path[idx:]
                    cycles.append(cycle)
                    self.deadlock_cycles_detected += 1
                    break
                path.append(curr)
                curr = wait_for_edges[curr]
            visited.update(path)

        return cycles

    def send_signal(
        self,
        sender_id: str,
        receiver_id: str,
        signal_type: str,
        target_entity: Optional[str] = None,
        tick: int = 0,
    ) -> None:
        """Post a discrete structured signal to receiver's inbox."""
        sig = AgentSignal(
            sender_id=sender_id,
            receiver_id=receiver_id,
            signal_type=signal_type,
            target_entity=target_entity,
            tick=tick,
        )
        self.signals_inbox.setdefault(receiver_id, []).append(sig)

    def retrieve_signals_for(self, receiver_id: str) -> List[AgentSignal]:
        """Pop all pending signals for an agent."""
        return self.signals_inbox.pop(receiver_id, [])
