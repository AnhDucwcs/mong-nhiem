"""Circuit Breaker Subsystem for MN-012 Stateful Tool Execution.

Guarantees safety invariants:
- Hard turn ceiling (max_turns <= 5)
- Repeated tool invocation cycle detection
- Consecutive mutation rejection threshold
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Set


class CircuitBreakerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    TRIPPED_MAX_TURNS = "TRIPPED_MAX_TURNS"
    TRIPPED_CYCLE_DETECTED = "TRIPPED_CYCLE_DETECTED"
    TRIPPED_REJECTION_LIMIT = "TRIPPED_REJECTION_LIMIT"


@dataclass
class CircuitBreaker:
    max_turns: int = 5
    max_consecutive_rejections: int = 2
    current_turn: int = 0
    consecutive_rejections: int = 0
    visited_signatures: Set[str] = field(default_factory=set)
    status: CircuitBreakerStatus = CircuitBreakerStatus.ACTIVE

    def reset(self) -> None:
        self.current_turn = 0
        self.consecutive_rejections = 0
        self.visited_signatures.clear()
        self.status = CircuitBreakerStatus.ACTIVE

    def check_turn(self) -> CircuitBreakerStatus:
        """Verify turn boundary before model forward pass."""
        if self.current_turn >= self.max_turns:
            self.status = CircuitBreakerStatus.TRIPPED_MAX_TURNS
            return self.status
        return CircuitBreakerStatus.ACTIVE

    def record_action(self, action_signature: str, is_rejected: bool = False) -> CircuitBreakerStatus:
        """Record an executed action, checking cycle detection and consecutive rejection bounds."""
        self.current_turn += 1

        # Check consecutive rejections
        if is_rejected:
            self.consecutive_rejections += 1
            if self.consecutive_rejections >= self.max_consecutive_rejections:
                self.status = CircuitBreakerStatus.TRIPPED_REJECTION_LIMIT
                return self.status
        else:
            self.consecutive_rejections = 0

        # Check cycle detection (duplicate successful action signature)
        sig = action_signature.strip().lower()
        if not is_rejected and sig in self.visited_signatures:
            self.status = CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED
            return self.status

        if not is_rejected:
            self.visited_signatures.add(sig)

        if self.current_turn >= self.max_turns:
            self.status = CircuitBreakerStatus.TRIPPED_MAX_TURNS
            return self.status

        return CircuitBreakerStatus.ACTIVE
