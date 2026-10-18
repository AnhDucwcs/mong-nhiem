"""Virtual Asymmetric Latency & Jitter Arbiter for Milestone MN-026.

Simulates variable cognitive latency across multi-role execution on a single SLM,
testing optimistic concurrency leases without multi-model overhead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class VirtualRoleConfig:
    role_name: str
    base_latency_ms: float
    jitter_range_ms: Tuple[float, float]
    priority: int


@dataclass
class ResourceLease:
    resource_id: str
    holder: str
    acquired_tick: int
    ttl: int


class VirtualJitterArbiter:
    """Manages resource leases and schedules multi-role actions under latency skew."""

    def __init__(self):
        self.role_configs: Dict[str, VirtualRoleConfig] = {
            "fast_reactive_scout": VirtualRoleConfig(
                role_name="fast_reactive_scout",
                base_latency_ms=100.0,
                jitter_range_ms=(80.0, 150.0),
                priority=1,
            ),
            "deliberative_actuator": VirtualRoleConfig(
                role_name="deliberative_actuator",
                base_latency_ms=800.0,
                jitter_range_ms=(600.0, 950.0),
                priority=2,
            ),
            "epistemic_arbiter": VirtualRoleConfig(
                role_name="epistemic_arbiter",
                base_latency_ms=500.0,
                jitter_range_ms=(400.0, 700.0),
                priority=3,
            ),
        }
        self.active_leases: Dict[str, ResourceLease] = {}
        self.collision_count = 0

    def compute_turn_latency(self, role_name: str, seed: int = 42) -> float:
        """Computes deterministic virtual latency for a role."""
        config = self.role_configs.get(role_name)
        if not config:
            return 200.0
        # Deterministic pseudorandom jitter
        low, high = config.jitter_range_ms
        factor = ((seed * 1103515245 + 12345) % 1000) / 1000.0
        return low + factor * (high - low)

    def acquire_lease(
        self, resource_id: str, agent_id: str, current_tick: int, ttl: int = 3
    ) -> bool:
        """Attempts to acquire a non-blocking optimistic concurrency lease."""
        if resource_id in self.active_leases:
            lease = self.active_leases[resource_id]
            # Check if active lease held by another agent has expired
            if lease.holder != agent_id and (current_tick - lease.acquired_tick) < lease.ttl:
                self.collision_count += 1
                return False

        self.active_leases[resource_id] = ResourceLease(
            resource_id=resource_id,
            holder=agent_id,
            acquired_tick=current_tick,
            ttl=ttl,
        )
        return True

    def release_lease(self, resource_id: str, agent_id: str) -> None:
        """Releases a held resource lease."""
        if resource_id in self.active_leases and self.active_leases[resource_id].holder == agent_id:
            del self.active_leases[resource_id]
