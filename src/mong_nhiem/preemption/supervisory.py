"""Human-in-the-Loop Supervisory Preemption Bridge.

Resolves SUPERVISED_STANDBY states and handles human operator preemption commands.
Advances world epochs to safely drop stale in-flight SLM actions without physical breach.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from mong_nhiem.orchestration.preemption_gate import PreemptiveInterruptGate


@dataclass
class HumanCommandRecord:
    """Historical record of an injected human operator command."""

    timestamp: float
    epoch: int
    raw_command: str
    action_override: str | None
    resolved_standby: bool


class HumanSupervisoryBridge:
    """Bridges human operator supervisory actions with the Host Preemptive Gate."""

    def __init__(self, preemption_gate: PreemptiveInterruptGate | None = None) -> None:
        self.preemption_gate: PreemptiveInterruptGate = (
            preemption_gate if preemption_gate is not None else PreemptiveInterruptGate()
        )
        self.in_standby: bool = False
        self.standby_reason: str | None = None
        self.awaiting_human: bool = False
        self.last_human_directive: str | None = None
        self.command_history: list[HumanCommandRecord] = []

    def enter_standby(self, reason: str) -> None:
        """Transitions Host into SUPERVISED_STANDBY, awaiting operator intervention."""
        self.in_standby = True
        self.standby_reason = reason
        self.awaiting_human = True

    def inject_human_command(
        self,
        raw_command: str,
        action_override: str | None = None,
    ) -> int:
        """Injects a human operator supervisory command, advancing epoch and clearing standby.

        Returns:
            The newly established world epoch.
        """
        self.preemption_gate.trigger_shock(
            shock_id="human_supervisory_interrupt",
            target_entity="*",
            shock_type="HUMAN_SUPERVISORY_INTERRUPT",
            trigger_tick=self.preemption_gate.world_epoch,
            required_mitigation=action_override or raw_command,
        )
        new_epoch = self.preemption_gate.world_epoch

        resolved = self.in_standby
        self.in_standby = False
        self.standby_reason = None
        self.awaiting_human = False
        self.last_human_directive = raw_command

        record = HumanCommandRecord(
            timestamp=time.time(),
            epoch=new_epoch,
            raw_command=raw_command,
            action_override=action_override,
            resolved_standby=resolved,
        )
        self.command_history.append(record)

        return new_epoch

    def validate_action_against_human_epoch(self, action: str, action_epoch: int) -> tuple[bool, str | None]:
        """Evaluates whether an action proposal complies with current epoch and preemption rules."""
        return self.preemption_gate.validate_action_epoch(
            action=action,
            action_epoch=action_epoch,
        )

    def get_standby_status(self) -> dict[str, Any]:
        """Returns current supervisory standby state."""
        return {
            "in_standby": self.in_standby,
            "standby_reason": self.standby_reason,
            "awaiting_human": self.awaiting_human,
            "world_epoch": self.preemption_gate.world_epoch,
            "last_human_directive": self.last_human_directive,
            "interventions_count": len(self.command_history),
        }
