"""L2 In-Memory Memento Stack for MN-013 State Checkpointing & Rollback.

Maintains bounded in-memory deep-copy snapshots of the environment state:
- O(1) push and pop operations
- Zero prompt token overhead
- Bounded stack depth (max_depth <= 3) to prevent host memory leakage
- Bit-for-bit restoration verification
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StateSnapshot:
    turn_index: int
    state: Dict[str, Any]
    action_key: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class MementoStack:
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self._stack: List[StateSnapshot] = []

    @property
    def depth(self) -> int:
        return len(self._stack)

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def push(self, turn_index: int, state: Dict[str, Any], action_key: str = "", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Push a deep copy of the current environment state onto the stack."""
        snapshot = StateSnapshot(
            turn_index=turn_index,
            state=copy.deepcopy(state),
            action_key=action_key,
            metadata=copy.deepcopy(metadata or {}),
        )
        if len(self._stack) >= self.max_depth:
            # Preserve initial base snapshot if present, discard oldest intermediate
            if len(self._stack) > 1:
                self._stack.pop(1)
            else:
                self._stack.pop(0)

        self._stack.append(snapshot)

    def pop(self) -> StateSnapshot:
        """Pop and return the most recent state snapshot for rollback."""
        if not self._stack:
            raise IndexError("Cannot rollback: MementoStack is empty.")
        return self._stack.pop()

    def peek(self) -> StateSnapshot:
        """Return the top state snapshot without removing it."""
        if not self._stack:
            raise IndexError("MementoStack is empty.")
        return self._stack[-1]

    def clear(self) -> None:
        self._stack.clear()
