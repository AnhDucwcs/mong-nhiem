"""Host Reflex Circuit Breaker with Hysteresis Band.

Executes immediate automated cutoff/scram under critical redline excursions
and enforces strict hysteresis to prevent state chattering/oscillation.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ReflexState(str, Enum):
    """Operational state of the reflex interlock breaker."""

    NORMAL = "NORMAL"
    TRIPPED = "TRIPPED"
    RECOVERED = "RECOVERED"


@dataclass(frozen=True)
class RedlineRule:
    """Threshold rule governing automated emergency scram and hysteresis recovery."""

    metric_key: str
    threshold: float
    comparison: str  # ">=", "<=", ">", "<"
    failsafe_action: str
    reset_threshold: Optional[float] = None
    reset_action: str = "RESET_BREAKER"


class ReflexCircuitBreaker:
    """Fast-path automated reflex circuit breaker intercepting redline threshold excursions."""

    def __init__(self, rules: Optional[List[RedlineRule]] = None) -> None:
        self.rules: List[RedlineRule] = list(rules) if rules is not None else []
        self.state: ReflexState = ReflexState.NORMAL
        self.active_failsafe_action: Optional[str] = None
        self.tripped_rule: Optional[RedlineRule] = None
        self.trip_history: List[Dict[str, Any]] = []

    def register_rule(self, rule: RedlineRule) -> None:
        """Registers a new redline safety rule."""
        self.rules.append(rule)

    def _eval_condition(self, value: float, threshold: float, op: str) -> bool:
        if op == ">=":
            return value >= threshold
        if op == "<=":
            return value <= threshold
        if op == ">":
            return value > threshold
        if op == "<":
            return value < threshold
        return False

    def check_telemetry(
        self, telemetry: Dict[str, Any], current_tick: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """Evaluates telemetry against redline rules.

        If any redline is breached, transitions to TRIPPED and returns the failsafe action.

        Returns:
            Tuple of (is_tripped, failsafe_action_or_none)
        """
        for rule in self.rules:
            if rule.metric_key in telemetry:
                val = float(telemetry[rule.metric_key])
                if self._eval_condition(val, rule.threshold, rule.comparison):
                    self.state = ReflexState.TRIPPED
                    self.active_failsafe_action = rule.failsafe_action
                    self.tripped_rule = rule
                    self.trip_history.append({
                        "tick": current_tick,
                        "metric": rule.metric_key,
                        "value": val,
                        "threshold": rule.threshold,
                        "action": rule.failsafe_action,
                    })
                    return True, rule.failsafe_action

        return False, None

    def attempt_reset(
        self, action: str, telemetry: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Attempts to reset the breaker from TRIPPED back to RECOVERED.

        Enforces hysteresis: telemetry MUST satisfy reset_threshold.

        Returns:
            Tuple of (success, message).
        """
        if self.state != ReflexState.TRIPPED:
            return True, "Breaker is not in TRIPPED state."

        clean_action = action.replace("ACTION:", "").strip()
        rule = self.tripped_rule

        if rule is None:
            self.state = ReflexState.RECOVERED
            return True, "Breaker reset to RECOVERED (no active rule bound)."

        # Validate action
        if clean_action != rule.reset_action.replace("ACTION:", "").strip():
            return False, f"RESET_FAILED: Expected '{rule.reset_action}', received '{clean_action}'"

        # Validate hysteresis threshold
        if rule.reset_threshold is not None and rule.metric_key in telemetry:
            val = float(telemetry[rule.metric_key])
            # Determine safe direction from trip operator:
            # If tripped on >= or >, safe recovery requires <= reset_threshold
            safe_op = "<=" if rule.comparison in (">=", ">") else ">="
            if not self._eval_condition(val, rule.reset_threshold, safe_op):
                return False, (
                    f"HYSTERESIS_INTERLOCK: Metric '{rule.metric_key}' ({val}) has not reached "
                    f"safe recovery threshold ({safe_op} {rule.reset_threshold})"
                )

        self.state = ReflexState.RECOVERED
        self.active_failsafe_action = None
        self.tripped_rule = None
        return True, "Breaker successfully reset to RECOVERED."
