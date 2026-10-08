"""Circuit breaker and execution guard for MN-013."""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Set


class CircuitBreakerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    TRIPPED_MAX_TURNS = "TRIPPED_MAX_TURNS"
    TRIPPED_CYCLE_DETECTED = "TRIPPED_CYCLE_DETECTED"
    TRIPPED_REJECTION_LIMIT = "TRIPPED_REJECTION_LIMIT"


class CircuitBreaker:
    def __init__(self, max_turns: int = 7, max_consecutive_rejections: int = 3):
        self.max_turns = max_turns
        self.max_consecutive_rejections = max_consecutive_rejections
        self.turn_count = 0
        self.consecutive_rejections = 0
        self.action_history: List[str] = []
        self.rejected_actions_set: Set[str] = set()

    def record_action(self, action_key: str, is_rejected: bool = False) -> CircuitBreakerStatus:
        self.turn_count += 1
        self.action_history.append(action_key)

        if is_rejected:
            self.consecutive_rejections += 1
            self.rejected_actions_set.add(action_key)
            if self.consecutive_rejections >= self.max_consecutive_rejections:
                return CircuitBreakerStatus.TRIPPED_REJECTION_LIMIT
        else:
            self.consecutive_rejections = 0

        # Cycle detection: check if same action repeated consecutively
        if len(self.action_history) >= 2 and self.action_history[-1] == self.action_history[-2]:
            return CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED

        if self.turn_count >= self.max_turns:
            return CircuitBreakerStatus.TRIPPED_MAX_TURNS

        return CircuitBreakerStatus.ACTIVE
