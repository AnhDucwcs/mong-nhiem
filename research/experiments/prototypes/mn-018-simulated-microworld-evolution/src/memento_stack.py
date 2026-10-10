"""Host-Authoritative Memento Rollback and Negative Action Steering Stack.

Maintains state checkpoints, executes deterministic rollbacks upon invariant
violations or fatal preconditions, and injects bounded Negative Action Directives.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from microworld_engine import MicroworldEngine


@dataclass
class MementoCheckpoint:
    """A checkpoint of world state prior to risky or transactional mutations."""
    tick: int
    snapshot: Dict[str, Any]
    action_attempted: str = ""
    failure_reason: str = ""


class MementoStack:
    """Stack of world snapshots enabling atomic rollback and negative steering."""

    def __init__(self, max_depth: int = 10) -> None:
        self.max_depth = max_depth
        self.checkpoints: List[MementoCheckpoint] = []
        self.negative_actions: List[str] = []
        self.rollbacks_executed: int = 0

    def push(self, engine: MicroworldEngine, action_attempted: str = "") -> None:
        """Capture and push snapshot of current engine state."""
        cp = MementoCheckpoint(
            tick=engine.clock.current_tick,
            snapshot=engine.create_snapshot(),
            action_attempted=action_attempted,
        )
        self.checkpoints.append(cp)
        if len(self.checkpoints) > self.max_depth:
            self.checkpoints.pop(0)

    def rollback_latest(self, engine: MicroworldEngine, reason: str = "") -> Optional[MementoCheckpoint]:
        """Roll back world engine to the most recent checkpoint and record negative directive."""
        if not self.checkpoints:
            return None

        cp = self.checkpoints.pop()
        cp.failure_reason = reason
        engine.restore_snapshot(cp.snapshot)
        self.rollbacks_executed += 1

        if cp.action_attempted:
            self.negative_actions.append(cp.action_attempted)

        return cp

    def record_negative_action(self, action_str: str) -> None:
        """Record an action as prohibited for subsequent turns."""
        if action_str not in self.negative_actions:
            self.negative_actions.append(action_str)

    def get_negative_actions(self) -> List[str]:
        """Return list of banned actions."""
        return list(self.negative_actions)

    def render_negative_directives(self) -> str:
        """Render bounded negative action directives strictly <= 64 tokens."""
        if not self.negative_actions:
            return ""
        recent = self.negative_actions[-3:]  # Limit to 3 most recent to stay bounded
        banned_str = "; ".join(recent)
        return f"[NEGATIVE DIRECTIVE: DO NOT REPEAT FAILED ACTIONS: {banned_str}]"
