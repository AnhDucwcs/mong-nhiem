"""Host-side Memento State Checkpoint Stack for MN-014.

Maintains bounded in-memory state snapshots (S_0, S_1, ..., S_t) with O(1) push/pop.
Decoupled completely from LLM context (0 prompt tokens).
"""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class MementoSnapshot:
    turn_index: int
    state: Dict[str, Any]
    action_key: str
    timestamp: float


class MementoStack:
    """Bounded LIFO stack for environment state snapshots (RAM-only)."""

    def __init__(self, max_depth: int = 3):
        if max_depth <= 0:
            raise ValueError(f"max_depth must be positive, got {max_depth}")
        self.max_depth = max_depth
        self._stack: List[MementoSnapshot] = []

    def push(self, turn_index: int, state: Dict[str, Any], action_key: str) -> None:
        """Push a deep-copy snapshot of current environment state."""
        snapshot = MementoSnapshot(
            turn_index=turn_index,
            state=copy.deepcopy(state),
            action_key=action_key,
            timestamp=time.time(),
        )
        if len(self._stack) >= self.max_depth:
            self._stack.pop(0)  # Evict oldest snapshot to preserve bounded memory
        self._stack.append(snapshot)

    def pop(self) -> MementoSnapshot:
        """Pop and return the most recent state snapshot."""
        if not self._stack:
            raise IndexError("Cannot pop from an empty MementoStack")
        return self._stack.pop()

    def peek(self) -> Optional[MementoSnapshot]:
        """Return the top snapshot without removing it."""
        return self._stack[-1] if self._stack else None

    @property
    def depth(self) -> int:
        return len(self._stack)

    def clear(self) -> None:
        self._stack.clear()
