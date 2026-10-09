"""Circuit Breaker for MN-014.

Guarantees safety bounds (max 7 turns) and detects identical action cycles.
"""
from __future__ import annotations

from enum import Enum
from typing import List


class CircuitBreakerStatus(str, Enum):
    OK = "OK"
    TRIPPED_MAX_TURNS = "TRIPPED_MAX_TURNS"
    TRIPPED_CYCLE_DETECTED = "TRIPPED_CYCLE_DETECTED"
    TRIPPED_REJECTION_LIMIT = "TRIPPED_REJECTION_LIMIT"


class CircuitBreaker:
    """Enforces turn budget limits and detects repetitive action cycles."""

    def __init__(self, max_turns: int = 7, max_consecutive_rejections: int = 3):
        self.max_turns = max_turns
        self.max_consecutive_rejections = max_consecutive_rejections
        self.turn_count = 0
        self.consecutive_rejections = 0
        self.history: List[str] = []

    def record_action(self, action_key: str, is_rejected: bool = False) -> CircuitBreakerStatus:
        self.turn_count += 1
        if self.turn_count > self.max_turns:
            return CircuitBreakerStatus.TRIPPED_MAX_TURNS

        if is_rejected:
            self.consecutive_rejections += 1
            if self.consecutive_rejections >= self.max_consecutive_rejections:
                return CircuitBreakerStatus.TRIPPED_REJECTION_LIMIT
        else:
            self.consecutive_rejections = 0

        # Cycle detection: identical action consecutively executed
        if self.history and self.history[-1] == action_key:
            return CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED

        self.history.append(action_key)
        return CircuitBreakerStatus.OK

    def reset(self) -> None:
        self.turn_count = 0
        self.consecutive_rejections = 0
        self.history.clear()
