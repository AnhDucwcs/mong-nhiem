"""Star consensus coordinator and Byzantine admission gate for swarm governance."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .arbiter import MultiResourceArbiter


@dataclass
class ProposalFilterResult:
    """Outcome of Byzantine proposal validation."""

    is_valid: bool
    action_type: str
    target: str
    param: Optional[str] = None
    reason: str = ""


class ByzantineAdmissionGate:
    """Host admission gate that sanitizes action proposals from noisy or faulty agents."""

    ACTION_REGEX = re.compile(
        r"^ACTION:\s*(LEASE|ACT|RELEASE|WAIT)(?:\s+([A-Za-z0-9_\-\.]+))?(?:\s+([A-Za-z0-9_\-\.]+))?$",
        re.IGNORECASE,
    )

    def __init__(self, valid_resources: Optional[Set[str]] = None):
        self.valid_resources: Set[str] = set(valid_resources or [])
        self.malformed_intercepts: int = 0
        self.unauthorized_intercepts: int = 0
        self.constraint_intercepts: int = 0

    def register_resources(self, resources: Set[str]) -> None:
        """Expands the universe of authorized resources."""
        self.valid_resources.update(resources)

    def validate_action(
        self,
        raw_text: str,
        agent_id: str,
        held_leases: Set[str],
        require_lease: bool = True,
    ) -> ProposalFilterResult:
        """Validates action syntax and authorization constraints."""
        text = raw_text.strip()
        match = self.ACTION_REGEX.match(text)
        if not match:
            self.malformed_intercepts += 1
            return ProposalFilterResult(
                is_valid=False,
                action_type="MALFORMED",
                target="",
                param=None,
                reason=f"SYNTAX_VIOLATION: '{raw_text}' does not match ACTION grammar",
            )

        act_type = match.group(1).upper()
        target = match.group(2) or ""
        param = match.group(3)

        if act_type == "WAIT":
            return ProposalFilterResult(
                is_valid=True,
                action_type="WAIT",
                target="",
                param=None,
                reason="VALID_WAIT",
            )

        if not target:
            self.malformed_intercepts += 1
            return ProposalFilterResult(
                is_valid=False,
                action_type=act_type,
                target="",
                param=param,
                reason=f"MISSING_TARGET: {act_type} requires target resource",
            )

        if self.valid_resources and target not in self.valid_resources:
            self.constraint_intercepts += 1
            return ProposalFilterResult(
                is_valid=False,
                action_type=act_type,
                target=target,
                param=param,
                reason=f"UNKNOWN_RESOURCE: '{target}' not in valid resources",
            )

        if require_lease and act_type in ("ACT", "RELEASE") and target not in held_leases:
            self.unauthorized_intercepts += 1
            return ProposalFilterResult(
                is_valid=False,
                action_type=act_type,
                target=target,
                param=param,
                reason=f"UNAUTHORIZED: Agent '{agent_id}' does not hold active lease on '{target}'",
            )

        return ProposalFilterResult(
            is_valid=True,
            action_type=act_type,
            target=target,
            param=param,
            reason="VALID_PROPOSAL",
        )


class StarConsensusHub:
    """Centralized star topology consensus hub coordinating multi-agent actions in O(M) time."""

    def __init__(
        self,
        arbiter: MultiResourceArbiter,
        gate: Optional[ByzantineAdmissionGate] = None,
    ):
        self.arbiter = arbiter
        self.gate = gate or ByzantineAdmissionGate()
        self.committed_proposals: List[Dict[str, Any]] = []
        self.rejected_proposals: List[Dict[str, Any]] = []

    def process_proposal(
        self,
        agent_id: str,
        raw_action_text: str,
        current_tick: int,
        action_executor: Optional[Callable[[str, str, Optional[str]], Tuple[bool, str]]] = None,
    ) -> Tuple[bool, str]:
        """Processes and evaluates a single agent proposal through the admission gate and arbiter.
        
        Returns:
            (committed: bool, feedback_message: str)
        """
        held = self.arbiter.get_held_resources(agent_id)
        filtered = self.gate.validate_action(raw_action_text, agent_id, held)

        if not filtered.is_valid:
            self.rejected_proposals.append({
                "tick": current_tick,
                "agent_id": agent_id,
                "raw": raw_action_text,
                "reason": filtered.reason,
            })
            return False, filtered.reason

        act_type = filtered.action_type
        target = filtered.target
        param = filtered.param

        if act_type == "WAIT":
            return True, "WAITED"

        if act_type == "LEASE":
            success, msg = self.arbiter.acquire(target, agent_id, current_tick)
            if success:
                self.committed_proposals.append({
                    "tick": current_tick,
                    "agent_id": agent_id,
                    "action_type": act_type,
                    "target": target,
                    "status": "COMMITTED",
                })
                return True, f"LEASE_ACQUIRED: {target} ({msg})"
            else:
                self.rejected_proposals.append({
                    "tick": current_tick,
                    "agent_id": agent_id,
                    "action_type": act_type,
                    "target": target,
                    "reason": msg,
                })
                return False, f"LEASE_DENIED: {target} ({msg})"

        if act_type == "RELEASE":
            success, msg = self.arbiter.release(target, agent_id)
            if success:
                self.committed_proposals.append({
                    "tick": current_tick,
                    "agent_id": agent_id,
                    "action_type": act_type,
                    "target": target,
                    "status": "COMMITTED",
                })
                return True, f"LEASE_RELEASED: {target}"
            else:
                return False, f"RELEASE_FAILED: {msg}"

        if act_type == "ACT":
            if action_executor is not None:
                exec_success, exec_msg = action_executor(act_type, target, param)
                if not exec_success:
                    self.rejected_proposals.append({
                        "tick": current_tick,
                        "agent_id": agent_id,
                        "action_type": act_type,
                        "target": target,
                        "reason": exec_msg,
                    })
                    return False, f"ACT_FAILED: {exec_msg}"

            self.committed_proposals.append({
                "tick": current_tick,
                "agent_id": agent_id,
                "action_type": act_type,
                "target": target,
                "status": "COMMITTED",
            })
            return True, f"ACT_SUCCESS: {target}"

        return False, "UNKNOWN_PROPOSAL_TYPE"
