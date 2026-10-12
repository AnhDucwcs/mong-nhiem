"""Vector clock primitive for decentralized multi-agent causal tracking."""

from __future__ import annotations

from typing import Dict, List, Optional


class VectorClock:
    """Represents a discrete Vector Clock across M concurrent distributed agents."""

    def __init__(self, clock: Optional[Dict[str, int]] = None):
        self.clock: Dict[str, int] = dict(clock) if clock else {}

    def increment(self, agent_id: str) -> None:
        """Increments the local clock counter for the given agent."""
        self.clock[agent_id] = self.clock.get(agent_id, 0) + 1

    def get(self, agent_id: str) -> int:
        """Returns the clock value for an agent."""
        return self.clock.get(agent_id, 0)

    def merge(self, other: VectorClock) -> VectorClock:
        """Returns a new VectorClock with element-wise maximum across both clocks."""
        all_keys = set(self.clock.keys()).union(other.clock.keys())
        new_clock = {
            k: max(self.clock.get(k, 0), other.clock.get(k, 0))
            for k in all_keys
        }
        return VectorClock(new_clock)

    def is_causally_dependent(self, other: VectorClock) -> bool:
        """Returns True if self happened strictly before or concurrent with other.
        
        Specifically: self <= other if for all k, self[k] <= other[k].
        """
        all_keys = set(self.clock.keys()).union(other.clock.keys())
        return all(self.clock.get(k, 0) <= other.clock.get(k, 0) for k in all_keys)

    def is_strictly_less(self, other: VectorClock) -> bool:
        """Returns True if self < other (self <= other and self != other)."""
        if not self.is_causally_dependent(other):
            return False
        return any(self.clock.get(k, 0) < other.clock.get(k, 0) for k in set(self.clock.keys()).union(other.clock.keys()))

    def is_concurrent(self, other: VectorClock) -> bool:
        """Returns True if neither clock causally dominates the other (concurrent branches)."""
        return not self.is_causally_dependent(other) and not other.is_causally_dependent(self)

    def snapshot(self) -> Dict[str, int]:
        """Returns a copy of the underlying vector clock dictionary."""
        return dict(self.clock)

    def __repr__(self) -> str:
        items = ", ".join(f"{k}:{v}" for k, v in sorted(self.clock.items()))
        return f"VectorClock({{{items}}})"
