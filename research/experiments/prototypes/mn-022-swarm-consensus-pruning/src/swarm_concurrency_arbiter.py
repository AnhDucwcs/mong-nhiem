"""Swarm Concurrency Arbiter managing TTL multi-resource leases and lock stealing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class SwarmLease:
    resource_id: str
    holder_id: Optional[str] = None
    acquired_tick: int = 0
    ttl_ticks: int = 4
    expires_tick: int = 0
    version: int = 1
    state: str = "FREE"  # FREE, HELD, EXPIRED


class SwarmConcurrencyArbiter:
    """Host-authoritative arbiter for mutual-exclusion leases with discrete TTL."""

    def __init__(self, default_ttl: int = 4) -> None:
        self.default_ttl = default_ttl
        self.leases: Dict[str, SwarmLease] = {}
        self.conflict_intercepts: int = 0
        self.lock_steals: int = 0

    def register_resource(self, resource_id: str, version: int = 1) -> None:
        """Registers a managed physical resource."""
        if resource_id not in self.leases:
            self.leases[resource_id] = SwarmLease(
                resource_id=resource_id,
                holder_id=None,
                acquired_tick=0,
                ttl_ticks=self.default_ttl,
                expires_tick=0,
                version=version,
                state="FREE",
            )

    def acquire(
        self,
        resource_id: str,
        agent_id: str,
        current_tick: int,
        ttl_ticks: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """Attempts to acquire a mutual exclusion lease on resource_id."""
        if resource_id not in self.leases:
            self.register_resource(resource_id)

        lease = self.leases[resource_id]
        ttl = ttl_ticks if ttl_ticks is not None else self.default_ttl

        # Case 1: Lease is FREE
        if lease.holder_id is None or lease.state == "FREE":
            lease.holder_id = agent_id
            lease.acquired_tick = current_tick
            lease.ttl_ticks = ttl
            lease.expires_tick = current_tick + ttl
            lease.state = "HELD"
            lease.version += 1
            return True, "ACQUIRED"

        # Case 2: Held by the same agent (renew lease)
        if lease.holder_id == agent_id:
            lease.acquired_tick = current_tick
            lease.ttl_ticks = ttl
            lease.expires_tick = current_tick + ttl
            lease.state = "HELD"
            return True, "RENEWED"

        # Case 3: Held by another agent, but TTL has EXPIRED (Lock Stealing)
        if current_tick >= lease.expires_tick:
            old_holder = lease.holder_id
            lease.holder_id = agent_id
            lease.acquired_tick = current_tick
            lease.ttl_ticks = ttl
            lease.expires_tick = current_tick + ttl
            lease.state = "HELD"
            lease.version += 1
            self.lock_steals += 1
            return True, f"STOLEN_EXPIRED_FROM_{old_holder}"

        # Case 4: Contention locked by another agent
        self.conflict_intercepts += 1
        return False, f"LOCKED_BY_{lease.holder_id}_UNTIL_TICK_{lease.expires_tick}"

    def release(self, resource_id: str, agent_id: str) -> Tuple[bool, str]:
        """Releases the lease if held by agent_id."""
        if resource_id not in self.leases:
            return False, "RESOURCE_NOT_FOUND"

        lease = self.leases[resource_id]
        if lease.holder_id == agent_id:
            lease.holder_id = None
            lease.state = "FREE"
            lease.version += 1
            return True, "RELEASED"

        return False, f"NOT_HOLDER_CURRENT_HOLDER_{lease.holder_id}"

    def tick_cleanup(self, current_tick: int) -> List[str]:
        """Identifies and marks expired leases at the boundary of a discrete tick."""
        expired: List[str] = []
        for res_id, lease in self.leases.items():
            if lease.state == "HELD" and current_tick >= lease.expires_tick:
                lease.state = "EXPIRED"
                expired.append(res_id)
        return expired

    def get_lease_summary(self) -> Dict[str, Dict]:
        """Returns snapshot of all active leases."""
        return {
            res_id: {
                "holder": l.holder_id,
                "state": l.state,
                "expires_tick": l.expires_tick,
                "version": l.version,
            }
            for res_id, l in self.leases.items()
        }
