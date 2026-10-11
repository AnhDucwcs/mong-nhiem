"""Host Memento Stack for Atomic Transactional Rollback for Stage 3."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class WorldCheckpoint:
    """Immutable snapshot of microworld state prior to action execution."""
    tick: int
    entities: Dict[str, Any]
    active_alerts: Dict[str, Any]


class MementoStack:
    """LIFO stack of pre-action checkpoints supporting atomic rollback."""

    def __init__(self, max_depth: int = 20) -> None:
        self.stack: List[WorldCheckpoint] = []
        self.max_depth = max_depth

    def push(self, tick: int, entities: Dict[str, Any], active_alerts: Optional[Dict[str, Any]] = None) -> None:
        cp = WorldCheckpoint(
            tick=tick,
            entities=copy.deepcopy(entities),
            active_alerts=copy.deepcopy(active_alerts or {}),
        )
        self.stack.append(cp)
        if len(self.stack) > self.max_depth:
            self.stack.pop(0)

    def pop(self) -> Optional[WorldCheckpoint]:
        if not self.stack:
            return None
        return self.stack.pop()

    def clear(self) -> None:
        self.stack.clear()
