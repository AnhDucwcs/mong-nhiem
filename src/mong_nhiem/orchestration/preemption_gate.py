"""Preemptive Cognitive Interrupt Gate and Action Taxonomy Arbiter.

Coordinates mid-trajectory physical shocks, manages logical state epochs, and enforces
an orthogonal 3-class action taxonomy (READ_ONLY, FAILSAFE, MUTATION) to eliminate
stale mutation overwrites and livelock starvation.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class ActionClass(str, Enum):
    """Orthogonal taxonomy classifying action sensitivity to temporal state evolution."""

    READ_ONLY = "READ_ONLY"
    FAILSAFE = "FAILSAFE"
    MUTATION = "MUTATION"


def default_action_classifier(action: str) -> ActionClass:
    """Default heuristic classifier partitioning actions into the 3-tier taxonomy."""
    clean = action.replace("ACTION:", "").strip()

    # Read-only observation/inspection actions (epoch-immune)
    if any(clean.startswith(v) for v in ["PROBE", "INSPECT", "READ", "WAIT", "REPORT_ANOMALY", "OBSERVE"]):
        return ActionClass.READ_ONLY

    # Failsafe risk-mitigation actions (epoch-tolerant within bounded lag)
    if any(clean.startswith(v) for v in ["ENGAGE emergency_scram", "SCRAM", "ISOLATE", "ABSTAIN", "REFUSE", "HALT", "EMERGENCY_"]):
        return ActionClass.FAILSAFE

    # State-mutating operational actions (strictly epoch-bound)
    return ActionClass.MUTATION


@dataclass
class PreemptiveShock:
    """Represents a mid-trajectory environmental perturbation at t+1."""

    shock_id: str
    target_entity: str
    shock_type: str
    severity: str
    trigger_tick: int
    required_mitigation: str
    resolved: bool = False


class PreemptiveInterruptGate:
    """Authoritative Host Gate managing state epochs and cognitive preemption."""

    def __init__(
        self,
        classifier: Optional[Callable[[str], ActionClass]] = None,
        max_failsafe_lag: int = 1,
    ) -> None:
        self.world_epoch: int = 1
        self.emergency_active: bool = False
        self.active_shock: Optional[PreemptiveShock] = None
        self.classifier: Callable[[str], ActionClass] = classifier or default_action_classifier
        self.max_failsafe_lag: int = max_failsafe_lag

        # Telemetry & Accounting
        self.preempted_stale_count: int = 0
        self.emergency_mitigations_count: int = 0
        self.unhandled_shock_breaches: int = 0
        self.intercepted_history: List[Dict[str, Any]] = []

    def trigger_shock(
        self,
        shock_id: str,
        target_entity: str,
        shock_type: str,
        trigger_tick: int,
        required_mitigation: str,
        severity: str = "CRITICAL",
    ) -> PreemptiveShock:
        """Injects a sudden asynchronous physical shock, advancing world epoch."""
        self.world_epoch += 1
        self.emergency_active = True
        self.active_shock = PreemptiveShock(
            shock_id=shock_id,
            target_entity=target_entity,
            shock_type=shock_type,
            severity=severity,
            trigger_tick=trigger_tick,
            required_mitigation=required_mitigation,
            resolved=False,
        )
        return self.active_shock

    def validate_action_epoch(
        self, action: str, action_epoch: int
    ) -> Tuple[bool, Optional[str]]:
        """Verifies action proposal validity against the current world epoch.

        Rules:
        1. READ_ONLY: Always permitted regardless of epoch lag (epoch-immune).
        2. FAILSAFE: Permitted if lag <= max_failsafe_lag (epoch-tolerant).
        3. MUTATION: Strictly requires action_epoch == world_epoch.

        Returns:
            Tuple of (is_valid, optional_rejection_reason).
        """
        clean_action = action.replace("ACTION:", "").strip()
        act_class = self.classifier(clean_action)
        epoch_lag = self.world_epoch - action_epoch

        # Active emergency shock logic
        if self.emergency_active and self.active_shock:
            req_mitigation = self.active_shock.required_mitigation.replace("ACTION:", "").strip()

            if clean_action == req_mitigation:
                # Mitigation action allowed if within failsafe lag bound
                if act_class == ActionClass.FAILSAFE and epoch_lag <= self.max_failsafe_lag:
                    return True, None
                if act_class == ActionClass.MUTATION and epoch_lag == 0:
                    return True, None

            # READ_ONLY inspections allowed during emergency
            if act_class == ActionClass.READ_ONLY:
                return True, None

            # Non-mitigating action proposed during active emergency shock
            if epoch_lag > 0:
                self.preempted_stale_count += 1
                reason = (
                    f"PREEMPTED_STALE_ACTION: Action '{clean_action}' conceived at epoch "
                    f"{action_epoch} dropped due to active shock '{self.active_shock.shock_id}' (epoch {self.world_epoch})"
                )
                self.intercepted_history.append({"tick": -1, "reason": reason, "action": clean_action})
                return False, reason

        # Nominal operation (no active emergency shock)
        if act_class == ActionClass.READ_ONLY:
            return True, None

        if act_class == ActionClass.FAILSAFE:
            if epoch_lag <= self.max_failsafe_lag:
                return True, None
            reason = f"EXPIRED_FAILSAFE: Lag {epoch_lag} exceeds max allowed lag {self.max_failsafe_lag}"
            self.preempted_stale_count += 1
            return False, reason

        # MUTATION requires exact epoch
        if epoch_lag == 0:
            return True, None

        self.preempted_stale_count += 1
        reason = (
            f"STALE_MUTATION_DROPPED: Mutation '{clean_action}' was planned for epoch "
            f"{action_epoch}, but world is at epoch {self.world_epoch}"
        )
        self.intercepted_history.append({"tick": -1, "reason": reason, "action": clean_action})
        return False, reason

    def resolve_shock(self, action: str) -> bool:
        """Resolves active shock if action matches required mitigation."""
        clean_action = action.replace("ACTION:", "").strip()
        if self.emergency_active and self.active_shock:
            req = self.active_shock.required_mitigation.replace("ACTION:", "").strip()
            if clean_action == req:
                self.active_shock.resolved = True
                self.emergency_active = False
                self.emergency_mitigations_count += 1
                return True
        return False
