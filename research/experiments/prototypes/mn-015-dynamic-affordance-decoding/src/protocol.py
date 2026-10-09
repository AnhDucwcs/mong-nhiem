"""Protocol definitions, deterministic action parsing, and affordance formatting for MN-015.

Under Dual-Layer Affordance Steering, model emissions adhere strictly to the
dynamically compiled Context-Free Grammar. This module provides deterministic
structural parsing, backward-compatible fallback parsing, and compact affordance
prior serialization for L1 prompt attention seeding.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple


class ActionType(str, Enum):
    READ = "READ"
    INSPECT = "INSPECT"
    DISPATCH = "DISPATCH"
    RESOLVE = "RESOLVE"
    INVALID = "INVALID"


@dataclass(frozen=True)
class ToolAction:
    action_type: ActionType
    target: str
    payload: str
    raw: str

    @property
    def action_key(self) -> str:
        """Deterministic string key used for cycle detection and negative masking."""
        if self.action_type == ActionType.DISPATCH:
            return f"DISPATCH:{self.target}:{self.payload.strip()}"
        elif self.action_type == ActionType.INSPECT:
            return f"INSPECT:{self.target}"
        elif self.action_type == ActionType.READ:
            return f"READ:{self.target}"
        elif self.action_type == ActionType.RESOLVE:
            return f"RESOLVE:{self.payload.strip()}"
        return f"INVALID:{self.raw.strip()}"


@dataclass
class Affordances:
    reads: List[str] = field(default_factory=list)
    inspects: List[str] = field(default_factory=list)
    dispatches: List[Tuple[str, str]] = field(default_factory=list)  # (tool_name, payload)
    resolves: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.reads or self.inspects or self.dispatches or self.resolves)


_ACTION_REGEX = re.compile(
    r"ACTION:\s*(READ|INSPECT|DISPATCH|RESOLVE)(?:[:\s]\s*)([^\r\n]+)",
    re.IGNORECASE,
)
_THINK_TAG_REGEX = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def parse_action(text: str) -> ToolAction:
    """Parse model generation into typed ToolAction."""
    if not text or not text.strip():
        return ToolAction(action_type=ActionType.INVALID, target="", payload="", raw=text)

    cleaned = _THINK_TAG_REGEX.sub("", text).strip()

    # Fast-path: canonical GBNF formatted line
    if cleaned.startswith("ACTION: "):
        line = cleaned.split("\n", 1)[0].strip()
        body = line[len("ACTION: "):].strip()
        parts = body.split(maxsplit=1)
        if parts:
            verb = parts[0].upper()
            remainder = parts[1] if len(parts) > 1 else ""
            if verb in ("READ", "INSPECT", "DISPATCH", "RESOLVE"):
                action_type = ActionType(verb)
                target = ""
                payload = ""
                if action_type in (ActionType.READ, ActionType.INSPECT):
                    target = remainder.strip()
                elif action_type == ActionType.DISPATCH:
                    sub_parts = remainder.split(maxsplit=1)
                    target = sub_parts[0].strip()
                    payload = sub_parts[1].strip() if len(sub_parts) > 1 else ""
                elif action_type == ActionType.RESOLVE:
                    payload = remainder.strip()
                return ToolAction(
                    action_type=action_type,
                    target=target,
                    payload=payload,
                    raw=line,
                )

    # Fallback path for unconstrained generation
    matches = list(_ACTION_REGEX.finditer(cleaned))
    if not matches:
        for verb_candidate in ("READ", "INSPECT", "DISPATCH", "RESOLVE"):
            if cleaned.upper().startswith(verb_candidate):
                cleaned = f"ACTION: {cleaned}"
                matches = list(_ACTION_REGEX.finditer(cleaned))
                break
    if not matches:
        return ToolAction(action_type=ActionType.INVALID, target="", payload="", raw=text)

    last_match = matches[-1]
    verb = last_match.group(1).upper()
    remainder = last_match.group(2).strip()

    action_type = ActionType(verb)
    target = ""
    payload = ""

    if action_type in (ActionType.READ, ActionType.INSPECT):
        target = remainder
    elif action_type == ActionType.DISPATCH:
        parts = remainder.split(maxsplit=1)
        target = parts[0]
        payload = parts[1] if len(parts) > 1 else ""
    elif action_type == ActionType.RESOLVE:
        payload = remainder

    return ToolAction(
        action_type=action_type,
        target=target,
        payload=payload,
        raw=last_match.group(0),
    )


def format_action(action: ToolAction) -> str:
    """Format ToolAction to canonical protocol string."""
    if action.action_type in (ActionType.READ, ActionType.INSPECT):
        return f"ACTION: {action.action_type.value} {action.target}"
    elif action.action_type == ActionType.DISPATCH:
        return f"ACTION: DISPATCH {action.target} {action.payload}".strip()
    elif action.action_type == ActionType.RESOLVE:
        return f"ACTION: RESOLVE {action.payload}"
    return "ACTION: INVALID"


def format_negative_directive(rejected_action_key: str, reason: str) -> str:
    """Construct a compact negative directive (<= 25 tokens) for prompt injection."""
    return f"REJECTED: {rejected_action_key} ({reason}). Do NOT repeat this action. Choose an alternative step."


def format_affordance_prior(affordances: Affordances) -> str:
    """Construct a compact 1-line affordance prior (<= 20 tokens) for prompt injection.
    
    Example output:
    Available Affordances: [INSPECT svc_worker_b_51.status, DISPATCH activate_service svc_worker_b_51,CONSERVATIVE_PIPELINE]
    """
    items: List[str] = []
    for r in affordances.reads:
        items.append(f"READ {r}")
    for i in affordances.inspects:
        items.append(f"INSPECT {i}")
    for tool, payload in affordances.dispatches:
        items.append(f"DISPATCH {tool} {payload}".strip())
    for res in affordances.resolves:
        items.append(f"RESOLVE {res}")

    if not items:
        return "Available Affordances: None"
    return f"Available Affordances: [{', '.join(items)}]"
