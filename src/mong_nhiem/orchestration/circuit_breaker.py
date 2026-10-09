"""Defensive Circuit Breaker for Cognitive Loops.

Guarantees finite-state execution safety by monitoring:
1. Turn execution ceiling (max_turns).
2. Action cycle loops (consecutive identical actions or repeating cycles).
3. Negative action repetition (attempting known failed actions).
100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Set


class CircuitBreakerStatus(str, Enum):
    """Operational health status of the execution loop."""
    OK = "OK"
    TRIPPED_MAX_TURNS = "TRIPPED_MAX_TURNS"
    TRIPPED_CYCLE_DETECTED = "TRIPPED_CYCLE_DETECTED"
    TRIPPED_EMPTY_ACTION = "TRIPPED_EMPTY_ACTION"


class CircuitBreaker:
    """Monitors action streams and halts runaway cognitive thrashing."""

    def __init__(self, max_turns: int = 7, cycle_window: int = 2) -> None:
        self.max_turns = max_turns
        self.cycle_window = cycle_window
        self.turns_elapsed = 0
        self.action_history: List[str] = []
        self.rejected_actions: Set[str] = set()

    def record_action(self, action_key: str, is_rejected: bool = False) -> CircuitBreakerStatus:
        """Record turn action and verify loop invariants."""
        self.turns_elapsed += 1

        if not action_key or action_key.startswith("INVALID:"):
            return CircuitBreakerStatus.TRIPPED_EMPTY_ACTION

        if is_rejected:
            self.rejected_actions.add(action_key)

        # 1. Check max turns ceiling
        if self.turns_elapsed > self.max_turns:
            return CircuitBreakerStatus.TRIPPED_MAX_TURNS

        # 2. Check immediate consecutive duplicate action
        if self.action_history and self.action_history[-1] == action_key:
            return CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED

        # 3. Check cycle patterns within window (e.g. A -> B -> A -> B)
        self.action_history.append(action_key)
        n = len(self.action_history)
        if n >= 4:
            if self.action_history[-1] == self.action_history[-3] and self.action_history[-2] == self.action_history[-4]:
                return CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED

        return CircuitBreakerStatus.OK

    def is_rejected(self, action_key: str) -> bool:
        """Check if action was previously rejected."""
        return action_key in self.rejected_actions

    def reset(self) -> None:
        """Reset internal history."""
        self.turns_elapsed = 0
        self.action_history.clear()
        self.rejected_actions.clear()
