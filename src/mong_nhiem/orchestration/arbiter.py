"""Host-authoritative multi-resource concurrency arbiter with optimistic TTL leases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class ResourceLease:
    """Represents a mutual-exclusion lease on a discrete world resource."""

    resource_id: str
    holder_id: Optional[str] = None
    acquired_tick: int = 0
    ttl_ticks: int = 4
    expires_tick: int = 0
    version: int = 1
    state: str = "FREE"  # FREE, HELD, EXPIRED


class MultiResourceArbiter:
    """Host arbiter managing resource leases, TTL expirations, and goal-conditioned sorting."""

    def __init__(self, default_ttl: int = 4):
        self.default_ttl = default_ttl
        self.leases: Dict[str, ResourceLease] = {}
        self.conflict_intercepts: int = 0
        self.lock_steals: int = 0

    def register_resource(self, resource_id: str, version: int = 1) -> None:
        """Registers a managed physical resource."""
        if resource_id not in self.leases:
            self.leases[resource_id] = ResourceLease(
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
        """Attempts to acquire or renew a mutual exclusion lease on resource_id.
        
        Returns:
            (success: bool, status_message: str)
        """
        if resource_id not in self.leases:
            self.register_resource(resource_id)

        lease = self.leases[resource_id]
        ttl = ttl_ticks if ttl_ticks is not None else self.default_ttl

        # Case 1: Lease is free
        if lease.holder_id is None or lease.state == "FREE":
            lease.holder_id = agent_id
            lease.acquired_tick = current_tick
            lease.ttl_ticks = ttl
            lease.expires_tick = current_tick + ttl
            lease.state = "HELD"
            lease.version += 1
            return True, "ACQUIRED"

        # Case 2: Held by the requesting agent (renewal)
        if lease.holder_id == agent_id:
            lease.acquired_tick = current_tick
            lease.ttl_ticks = ttl
            lease.expires_tick = current_tick + ttl
            lease.state = "HELD"
            return True, "RENEWED"

        # Case 3: Held by another agent, but TTL has expired (Lock Stealing)
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
        """Identifies and marks expired leases at tick boundaries."""
        expired: List[str] = []
        for res_id, lease in self.leases.items():
            if lease.state == "HELD" and current_tick >= lease.expires_tick:
                lease.state = "EXPIRED"
                expired.append(res_id)
        return expired

    def get_held_resources(self, agent_id: str) -> Set[str]:
        """Returns all resources currently held by agent_id."""
        return {
            res_id
            for res_id, lease in self.leases.items()
            if lease.holder_id == agent_id and lease.state == "HELD"
        }

    def get_valid_affordances(
        self,
        agent_id: str,
        assigned_goal: str = "",
        domain_name: str = "",
        state: Optional[Dict[str, Any]] = None,
        all_resources: Optional[List[str]] = None,
        allow_unleased_act: bool = False,
    ) -> List[str]:
        """Generates dynamic valid affordances for an agent.
        
        Applies Goal-Conditioned Affordance Sorting and Completion-Aware Release Ordering.
        """
        affordances: List[str] = []
        resources_list = all_resources or list(self.leases.keys())
        held_leases = self.get_held_resources(agent_id)
        current_state = state or {}

        # 1. Action and release affordances for held resources
        for res in sorted(held_leases):
            val = current_state.get(res)
            is_done = False
            if val == 0 or val in ("DELIVERED", "COMPLETED", "RESOLVED"):
                is_done = True

            if is_done:
                affordances.append(f"ACTION: RELEASE {res}")
            else:
                act_verb = "ACT"
                if domain_name == "smart_microgrid":
                    act_verb = "ACT {res} STABILIZE"
                elif domain_name == "fleet_logistics":
                    act_verb = "ACT {res} TRANSFER"
                elif domain_name == "cluster_scheduling":
                    act_verb = "ACT {res} SCHEDULE"
                else:
                    act_verb = f"ACT {res}"

                if act_verb.startswith("ACT"):
                    affordances.append(f"ACTION: {act_verb.format(res=res)}")
                affordances.append(f"ACTION: RELEASE {res}")

        # 2. Goal-Conditioned Affordance Sorting for unheld resources
        target_res = [res for res in resources_list if res in assigned_goal]
        other_res = [res for res in resources_list if res not in assigned_goal]
        ordered_resources = sorted(target_res) + sorted(other_res)

        for res in ordered_resources:
            if res not in held_leases:
                affordances.append(f"ACTION: LEASE {res}")
                if allow_unleased_act:
                    affordances.append(f"ACTION: ACT {res}")

        # 3. Fallback Wait
        affordances.append("ACTION: WAIT")
        return affordances

    def get_lease_summary(self) -> Dict[str, Dict[str, Any]]:
        """Returns snapshot dictionary of all managed leases."""
        return {
            res_id: {
                "holder": l.holder_id,
                "state": l.state,
                "expires_tick": l.expires_tick,
                "version": l.version,
            }
            for res_id, l in self.leases.items()
        }
