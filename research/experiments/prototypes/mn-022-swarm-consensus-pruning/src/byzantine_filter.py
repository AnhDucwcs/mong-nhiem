"""Byzantine Action Filter providing host admission control against malformed or invalid proposals."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class FilterResult:
    is_valid: bool
    action_type: str
    target: str
    param: Optional[str]
    reason: str


class ByzantineFilter:
    """Host admission gate that sanitizes action proposals from noisy or faulty nodes."""

    # Action pattern: ACTION: <TYPE> [TARGET] [PARAM]
    ACTION_REGEX = re.compile(
        r"^ACTION:\s*(LEASE|ACT|RELEASE|WAIT)(?:\s+([A-Za-z0-9_\-\.]+))?(?:\s+([A-Za-z0-9_\-\.]+))?$",
        re.IGNORECASE,
    )

    def __init__(self, valid_resources: Optional[Set[str]] = None) -> None:
        self.valid_resources: Set[str] = valid_resources or set()
        self.malformed_intercepts: int = 0
        self.unauthorized_intercepts: int = 0
        self.constraint_intercepts: int = 0

    def register_resources(self, resources: Set[str]) -> None:
        """Updates valid resource universe."""
        self.valid_resources.update(resources)

    def validate_action(
        self,
        raw_text: str,
        agent_id: str,
        held_leases: Set[str],
        require_lease: bool = True,
    ) -> FilterResult:
        """Validates action syntax and authorization constraints."""
        text = raw_text.strip()
        match = self.ACTION_REGEX.match(text)
        if not match:
            self.malformed_intercepts += 1
            return FilterResult(
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
            return FilterResult(
                is_valid=True,
                action_type="WAIT",
                target="",
                param=None,
                reason="VALID_WAIT",
            )

        if not target:
            self.malformed_intercepts += 1
            return FilterResult(
                is_valid=False,
                action_type=act_type,
                target="",
                param=param,
                reason=f"MISSING_TARGET: {act_type} requires target resource",
            )

        if self.valid_resources and target not in self.valid_resources:
            self.constraint_intercepts += 1
            return FilterResult(
                is_valid=False,
                action_type=act_type,
                target=target,
                param=param,
                reason=f"UNKNOWN_RESOURCE: '{target}' not in valid resources",
            )

        # Check authorization for ACT and RELEASE
        if require_lease and act_type in ("ACT", "RELEASE") and target not in held_leases:
            self.unauthorized_intercepts += 1
            return FilterResult(
                is_valid=False,
                action_type=act_type,
                target=target,
                param=param,
                reason=f"UNAUTHORIZED: Agent '{agent_id}' does not hold active lease on '{target}'",
            )

        return FilterResult(
            is_valid=True,
            action_type=act_type,
            target=target,
            param=param,
            reason="VALID_PROPOSAL",
        )
