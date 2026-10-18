"""Preemptive Cognitive Interrupt Gate for Milestone MN-026.

Detects mid-trajectory environmental shocks at t+1, invalidates stale action proposals
planned for epoch t, revokes active concurrency leases, and injects emergency flash directives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ActionClass(Enum):
    READ_ONLY = "READ_ONLY"
    FAILSAFE = "FAILSAFE"
    MUTATION = "MUTATION"


def classify_action(action: str) -> ActionClass:
    """Classifies an action proposal into an orthogonal 3-tier behavioral class."""
    clean = action.replace("ACTION:", "").strip()
    # Read-only observation/inspection actions (epoch-immune)
    if any(clean.startswith(v) for v in ["PROBE", "INSPECT", "READ", "WAIT", "REPORT_ANOMALY"]):
        return ActionClass.READ_ONLY
    # Failsafe idempotent risk-mitigation actions (epoch-tolerant: leeway <= 1)
    if any(clean.startswith(v) for v in ["ENGAGE emergency_scram", "ISOLATE", "ABSTAIN", "REFUSE"]):
        return ActionClass.FAILSAFE
    # Physical state mutations (strictly requires epoch match)
    return ActionClass.MUTATION


@dataclass
class PreemptiveShockEvent:
    shock_id: str
    target_entity: str
    shock_type: str
    severity: str
    trigger_tick: int
    required_mitigation: str
    resolved: bool = False


class PreemptiveInterruptGate:
    """Authoritative Host Gate managing state epochs, cognitive preemption, and 3-class action validation."""

    def __init__(self):
        self.world_epoch: int = 1
        self.emergency_active: bool = False
        self.active_shock: Optional[PreemptiveShockEvent] = None
        
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
    ) -> PreemptiveShockEvent:
        """Injects sudden asynchronous physical shock at t+1, incrementing epoch."""
        self.world_epoch += 1
        self.emergency_active = True
        self.active_shock = PreemptiveShockEvent(
            shock_id=shock_id,
            target_entity=target_entity,
            shock_type=shock_type,
            severity="CRITICAL",
            trigger_tick=trigger_tick,
            required_mitigation=required_mitigation,
            resolved=False,
        )
        return self.active_shock

    def validate_action_epoch(
        self, action: str, action_epoch: int
    ) -> Tuple[bool, Optional[str]]:
        """Verifies action proposal validity according to the 3-class action taxonomy.
        
        - READ_ONLY: Epoch immune (always valid, never preempted).
        - FAILSAFE: Epoch tolerant (valid if world_epoch - action_epoch <= 1).
        - MUTATION: Strict epoch requirement (action_epoch == world_epoch).
        """
        clean_action = action.replace("ACTION:", "").strip()
        act_class = classify_action(clean_action)
        epoch_lag = self.world_epoch - action_epoch

        # If an emergency shock is active:
        if self.emergency_active and self.active_shock:
            req_mitigation = self.active_shock.required_mitigation
            # If the action matches required mitigation
            if clean_action == req_mitigation:
                # Failsafe actions tolerate 1-epoch delay (e.g. shock occurred while planning scram)
                if act_class == ActionClass.FAILSAFE and epoch_lag <= 1:
                    return True, None
                if action_epoch == self.world_epoch:
                    return True, None
                # Stale beyond tolerance
                self.preempted_stale_count += 1
                reason = f"Failsafe mitigation '{clean_action}' excessively stale (lag={epoch_lag} > 1)."
                return False, reason

            # Action does not match required mitigation during emergency:
            if act_class == ActionClass.READ_ONLY:
                # Read-only observation/probe during emergency is non-destructive
                return True, None

            if act_class == ActionClass.FAILSAFE:
                # Non-matching failsafe (e.g. generic abstention) does not cause breach, but doesn't resolve emergency
                return True, None

            # Attempting non-matching physical mutation during emergency
            if action_epoch < self.world_epoch:
                self.preempted_stale_count += 1
                reason = (
                    f"Action '{clean_action}' PREEMPTED: Computed on stale epoch {action_epoch} "
                    f"< current epoch {self.world_epoch}. Emergency '{self.active_shock.shock_type}' active."
                )
                self.intercepted_history.append({"tick": self.active_shock.trigger_tick, "reason": reason})
                return False, reason
            else:
                self.unhandled_shock_breaches += 1
                reason = (
                    f"Physical breach: Emergency '{self.active_shock.shock_type}' requires "
                    f"'{self.active_shock.required_mitigation}', attempted '{clean_action}'."
                )
                return False, reason

        # Nominal epoch check (no emergency active):
        if act_class == ActionClass.READ_ONLY:
            return True, None

        if act_class == ActionClass.FAILSAFE:
            if epoch_lag <= 1:
                return True, None
            self.preempted_stale_count += 1
            return False, f"Failsafe proposal stale (lag={epoch_lag} > 1)."

        # MUTATION: Strict epoch check
        if action_epoch < self.world_epoch:
            self.preempted_stale_count += 1
            reason = f"Stale proposal epoch {action_epoch} < current epoch {self.world_epoch}"
            return False, reason

        return True, None

    def resolve_emergency(self, action: str) -> bool:
        """Resolves active emergency shock if matching mitigation is executed."""
        clean_action = action.replace("ACTION:", "").strip()
        if self.emergency_active and self.active_shock:
            if clean_action == self.active_shock.required_mitigation:
                self.active_shock.resolved = True
                self.emergency_active = False
                self.emergency_mitigations_count += 1
                return True
        return False

    def render_interrupt_card_lines(self) -> List[str]:
        """Renders emergency directive banners for Fact Card Tier 1 & 2."""
        if not self.emergency_active or not self.active_shock:
            return []
        return [
            f"[EMERGENCY_INTERRUPT: {self.active_shock.shock_type} DETECTED AT TICK {self.active_shock.trigger_tick}]",
            f"[DIRECTIVE: ALL IN-FLIGHT PLANS PREEMPTED -> EXECUTE {self.active_shock.required_mitigation}]",
        ]
