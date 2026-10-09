"""Deterministic LIFO Memento Stack for Host Backtracking.

Preserves immutable state snapshots to enable rollback recovery from
dead-end trajectories, resource locks, and negative constraint violations.
100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Memento:
    """Immutable state snapshot captured at execution turn t."""
    turn_index: int
    state: Dict[str, Any]
    action_key: str = ""


class MementoStack:
    """Bounded LIFO stack for deterministic environment state restoration."""

    def __init__(self, max_depth: int = 5) -> None:
        self.max_depth = max_depth
        self._stack: List[Memento] = []

    def push(self, turn_index: int, state: Dict[str, Any], action_key: str = "") -> None:
        """Capture deep copy of state snapshot."""
        snapshot = copy.deepcopy(state)
        memento = Memento(
            turn_index=turn_index,
            state=snapshot,
            action_key=action_key,
        )
        self._stack.append(memento)
        if len(self._stack) > self.max_depth:
            self._stack.pop(0)

    def pop(self) -> Optional[Memento]:
        """Pop and return most recent memento."""
        if not self._stack:
            return None
        return self._stack.pop()

    def peek(self) -> Optional[Memento]:
        """Inspect top of stack without popping."""
        if not self._stack:
            return None
        return self._stack[-1]

    def can_pop(self) -> bool:
        """Return True if at least one memento is available to restore."""
        return len(self._stack) > 0

    def clear(self) -> None:
        """Reset stack."""
        self._stack.clear()

    def __len__(self) -> int:
        return len(self._stack)
