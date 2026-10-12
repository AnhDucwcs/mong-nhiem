"""Host Concurrency Arbiter & Optimistic Lease Manager for MN-021.

Manages mutual exclusion leases on contested physical entities, prevents write collisions,
and resolves resource contention cycles.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set


@dataclass
class LeaseRecord:
    """An active mutual exclusion lease on an entity."""
    entity_id: str
    owner_agent: str
    granted_tick: int
    ttl_ticks: int = 5


class ConcurrencyArbiter:
    """Host-authoritative arbiter managing mutual exclusion leases across agents."""

    def __init__(self):
        self._leases: Dict[str, LeaseRecord] = {}
        self._wait_graph: Dict[str, Set[str]] = {}

    def acquire_lease(
        self,
        agent_id: str,
        entity_id: str,
        current_tick: int,
        ttl_ticks: int = 5,
    ) -> bool:
        """Attempt to acquire an exclusive lease on an entity."""
        # Expire stale leases
        self._expire_stale_leases(current_tick)

        existing = self._leases.get(entity_id)
        if existing:
            if existing.owner_agent == agent_id:
                # Re-entrant renewal
                existing.granted_tick = current_tick
                return True
            else:
                # Contested: record wait-for edge
                if agent_id not in self._wait_graph:
                    self._wait_graph[agent_id] = set()
                self._wait_graph[agent_id].add(existing.owner_agent)
                return False

        # Grant lease
        self._leases[entity_id] = LeaseRecord(
            entity_id=entity_id,
            owner_agent=agent_id,
            granted_tick=current_tick,
            ttl_ticks=ttl_ticks,
        )
        if agent_id in self._wait_graph:
            self._wait_graph[agent_id].clear()
        return True

    def release_lease(self, agent_id: str, entity_id: str) -> bool:
        """Explicitly release an exclusive lease."""
        existing = self._leases.get(entity_id)
        if existing and existing.owner_agent == agent_id:
            del self._leases[entity_id]
            return True
        return False

    def release_all_agent_leases(self, agent_id: str):
        """Release all leases owned by an agent (e.g. upon episode completion)."""
        to_del = [e for e, l in self._leases.items() if l.owner_agent == agent_id]
        for e in to_del:
            del self._leases[e]
        self._wait_graph.pop(agent_id, None)

    def is_entity_leased(self, entity_id: str, current_tick: int) -> bool:
        """Check if an entity is currently under an active lease."""
        self._expire_stale_leases(current_tick)
        return entity_id in self._leases

    def get_lease_owner(self, entity_id: str, current_tick: int) -> Optional[str]:
        """Return the agent currently holding the lease on an entity."""
        self._expire_stale_leases(current_tick)
        existing = self._leases.get(entity_id)
        return existing.owner_agent if existing else None

    def get_contested_entities(self, calling_agent: str, current_tick: int) -> Set[str]:
        """Return set of entity IDs leased by other agents."""
        self._expire_stale_leases(current_tick)
        return {
            e for e, l in self._leases.items() if l.owner_agent != calling_agent
        }

    def detect_deadlock(self) -> bool:
        """Detect circular wait cycles in the multi-agent wait-for graph."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self._wait_graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for agent in list(self._wait_graph.keys()):
            if agent not in visited:
                if dfs(agent):
                    return True
        return False

    def _expire_stale_leases(self, current_tick: int):
        """Evict leases whose TTL has expired."""
        stale = [
            e for e, l in self._leases.items()
            if (current_tick - l.granted_tick) > l.ttl_ticks
        ]
        for e in stale:
            del self._leases[e]
