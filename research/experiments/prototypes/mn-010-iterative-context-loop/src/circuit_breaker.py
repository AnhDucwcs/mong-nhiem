"""Circuit breaker subsystem enforcing boundedness and cycle prevention for MN-010."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Set

from protocol import ActionType, AgentAction


class CircuitBreakerStatus(str, Enum):
    OK = "OK"
    TRIPPED_MAX_TURNS = "TRIPPED_MAX_TURNS"
    TRIPPED_CYCLE_DETECTED = "TRIPPED_CYCLE_DETECTED"
    TRIPPED_EMPTY_TARGET = "TRIPPED_EMPTY_TARGET"


@dataclass
class CircuitBreaker:
    """Enforces turn ceiling and prevents circular retrieval loops."""
    max_turns: int = 3
    turn_count: int = 0
    visited_targets: Set[str] = field(default_factory=set)
    is_tripped: bool = False
    trip_reason: str | None = None

    def validate_action(self, action: AgentAction) -> tuple[bool, CircuitBreakerStatus, str | None]:
        """Validate whether an action can be executed without violating safety boundaries."""
        if self.is_tripped:
            return False, CircuitBreakerStatus.TRIPPED_MAX_TURNS, self.trip_reason

        # Turn ceiling check
        if self.turn_count >= self.max_turns:
            reason = f"Max turns ceiling reached ({self.max_turns})"
            return False, CircuitBreakerStatus.TRIPPED_MAX_TURNS, reason

        if action.action_type == ActionType.FETCH:
            normalized_target = action.argument.strip().lower()
            if not normalized_target:
                reason = "FETCH directive contains empty target identifier"
                return False, CircuitBreakerStatus.TRIPPED_EMPTY_TARGET, reason
            if normalized_target in self.visited_targets:
                reason = f"Cycle detected: target '{action.argument}' has already been fetched"
                return False, CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED, reason

        return True, CircuitBreakerStatus.OK, None

    def record_step(self, action: AgentAction) -> None:
        """Record an executed step and update internal tracking state."""
        self.turn_count += 1
        if action.action_type == ActionType.FETCH:
            self.visited_targets.add(action.argument.strip().lower())

    def trip(self, status: CircuitBreakerStatus, reason: str) -> None:
        """Manually trip the circuit breaker."""
        self.is_tripped = True
        self.trip_reason = reason

    def reset(self) -> None:
        """Reset internal state for a fresh execution run."""
        self.turn_count = 0
        self.visited_targets.clear()
        self.is_tripped = False
        self.trip_reason = None
