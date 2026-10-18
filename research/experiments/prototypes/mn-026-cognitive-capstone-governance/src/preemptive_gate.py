"""Preemptive Cognitive Interrupt Gate for Milestone MN-026.

Detects mid-trajectory environmental shocks at t+1, invalidates stale action proposals
planned for epoch t, revokes active concurrency leases, and injects emergency flash directives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


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
    """Authoritative Host Gate managing state epochs and cognitive preemption."""

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
        """Verifies if the action proposal was computed on the current world epoch.
        
        If action_epoch < world_epoch, the proposal is STALE and preempted.
        """
        clean_action = action.replace("ACTION:", "").strip()

        # If an emergency shock is active, only the required mitigation is valid
        if self.emergency_active and self.active_shock:
            if clean_action != self.active_shock.required_mitigation:
                # If agent tried executing an obsolete plan or wrong action during emergency
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

        # Nominal epoch check
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
