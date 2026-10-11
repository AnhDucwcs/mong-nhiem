"""Transactional Memento Stack for Atomic Rollback on Invariant Breaches."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class WorldMemento:
    """Immutable state snapshot at a specific execution step."""
    step_id: int
    entities: Dict[str, Any]
    current_tick: int
    metadata: Dict[str, Any]


class MementoStack:
    """Stack managing transactional state checkpoints and rollback."""

    def __init__(self, max_depth: int = 20):
        self.max_depth = max_depth
        self._stack: List[WorldMemento] = []

    def push(self, step_id: int, entities: Dict[str, Any], current_tick: int, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Push a new deep-copied checkpoint onto the stack."""
        snapshot = WorldMemento(
            step_id=step_id,
            entities=copy.deepcopy(entities),
            current_tick=current_tick,
            metadata=copy.deepcopy(metadata or {}),
        )
        self._stack.append(snapshot)
        if len(self._stack) > self.max_depth:
            self._stack.pop(0)

    def pop(self) -> Optional[WorldMemento]:
        """Pop and return the top checkpoint."""
        if not self._stack:
            return None
        return self._stack.pop()

    def peek(self) -> Optional[WorldMemento]:
        """Inspect the current top checkpoint without removing it."""
        if not self._stack:
            return None
        return self._stack[-1]

    def clear(self) -> None:
        """Reset the memento stack."""
        self._stack.clear()

    @property
    def depth(self) -> int:
        """Current depth of the checkpoint stack."""
        return len(self._stack)
