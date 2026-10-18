"""Virtual Asymmetric Latency and Jitter Arbiter.

Coordinates multi-role cognitive execution on a single SLM instance under virtual
latency skew and optimistic non-blocking leases without concurrent multi-model VRAM overhead.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class VirtualRoleProfile:
    """Configures deterministic virtual latency bounds for a specialized agent role."""

    role_name: str
    base_latency_ms: float
    jitter_range_ms: Tuple[float, float]
    priority: int = 1


@dataclass
class LeaseRecord:
    """Mutual-exclusion lock on a discrete world resource."""

    resource_id: str
    holder: str
    acquired_tick: int
    ttl: int


class VirtualJitterArbiter:
    """Manages resource leases and schedules multi-role virtual execution on a single SLM."""

    def __init__(
        self,
        roles: Optional[Dict[str, VirtualRoleProfile]] = None,
        default_ttl: int = 3,
    ) -> None:
        self.roles: Dict[str, VirtualRoleProfile] = (
            dict(roles) if roles is not None else {}
        )
        self.default_ttl = default_ttl
        self.active_leases: Dict[str, LeaseRecord] = {}
        self.collision_count: int = 0

    def register_role(self, profile: VirtualRoleProfile) -> None:
        """Registers a virtual role profile."""
        self.roles[profile.role_name] = profile

    def compute_turn_latency(self, role_name: str, seed: int = 42) -> float:
        """Computes deterministic pseudorandom virtual latency for a role."""
        config = self.roles.get(role_name)
        if not config:
            return 200.0

        low, high = config.jitter_range_ms
        factor = ((seed * 1103515245 + 12345) % 1000) / 1000.0
        return low + factor * (high - low)

    def acquire_lease(
        self,
        resource_id: str,
        agent_id: str,
        current_tick: int,
        ttl: Optional[int] = None,
    ) -> bool:
        """Attempts to acquire an optimistic concurrency lease.

        Returns:
            True if acquired, False if locked by another active unexpired holder.
        """
        lease_ttl = ttl if ttl is not None else self.default_ttl

        if resource_id in self.active_leases:
            lease = self.active_leases[resource_id]
            # Check if active lease held by another agent has not expired
            if lease.holder != agent_id and (current_tick - lease.acquired_tick) < lease.ttl:
                self.collision_count += 1
                return False

        self.active_leases[resource_id] = LeaseRecord(
            resource_id=resource_id,
            holder=agent_id,
            acquired_tick=current_tick,
            ttl=lease_ttl,
        )
        return True

    def release_lease(self, resource_id: str, agent_id: str) -> bool:
        """Releases a held resource lease."""
        if (
            resource_id in self.active_leases
            and self.active_leases[resource_id].holder == agent_id
        ):
            del self.active_leases[resource_id]
            return True
        return False

    def is_locked(self, resource_id: str, current_tick: int) -> bool:
        """Checks if a resource is currently held under an active unexpired lease."""
        if resource_id not in self.active_leases:
            return False
        lease = self.active_leases[resource_id]
        return (current_tick - lease.acquired_tick) < lease.ttl
