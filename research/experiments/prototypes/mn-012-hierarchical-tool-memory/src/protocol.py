"""Action Protocol Grammar parser and formatter for MN-012 Stateful Tool Calling.

Grammar specification:
    ACTION: READ <target_id>
    ACTION: INSPECT <entity_id>.<property>
    ACTION: DISPATCH <action_name> <payload>
    ACTION: RESOLVE <final_answer>
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


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


_ACTION_REGEX = re.compile(
    r"ACTION:\s*(READ|INSPECT|DISPATCH|RESOLVE)(?:[:\s]\s*)([^\r\n]+)",
    re.IGNORECASE,
)
_THINK_TAG_REGEX = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def parse_action(text: str) -> ToolAction:
    """Parse raw model generation text into a typed ToolAction.
    
    Strips internal thinking tokens (<think>...</think>) and extracts
    the last conforming ACTION directive to prevent preamble corruption.
    """
    if not text or not text.strip():
        return ToolAction(action_type=ActionType.INVALID, target="", payload="", raw=text)

    cleaned = _THINK_TAG_REGEX.sub("", text).strip()
    matches = list(_ACTION_REGEX.finditer(cleaned))
    if not matches:
        return ToolAction(action_type=ActionType.INVALID, target="", payload="", raw=text)

    last_match = matches[-1]
    verb = last_match.group(1).upper()
    body = last_match.group(2).strip()

    # Strip surrounding quotes if wrapped
    if (body.startswith('"') and body.endswith('"')) or (body.startswith("'") and body.endswith("'")):
        body = body[1:-1].strip()

    action_type = ActionType[verb]

    if action_type == ActionType.DISPATCH:
        # Split into action_name and payload
        # e.g., "transfer acc_a,acc_b,100" or "refactor func:mult=2"
        parts = re.split(r"\s+", body, maxsplit=1)
        target = parts[0].strip()
        payload = parts[1].strip() if len(parts) > 1 else ""
        if (payload.startswith('"') and payload.endswith('"')) or (payload.startswith("'") and payload.endswith("'")):
            payload = payload[1:-1].strip()
        return ToolAction(action_type=action_type, target=target, payload=payload, raw=last_match.group(0))

    elif action_type == ActionType.RESOLVE:
        return ToolAction(action_type=action_type, target="", payload=body, raw=last_match.group(0))

    else:
        # READ or INSPECT
        return ToolAction(action_type=action_type, target=body, payload="", raw=last_match.group(0))


def format_action(action_type: ActionType, target: str, payload: str = "") -> str:
    """Format action enum, target, and payload into canonical protocol string."""
    if action_type == ActionType.INVALID:
        raise ValueError("Cannot format INVALID action type")
    if action_type == ActionType.RESOLVE:
        return f"ACTION: RESOLVE {payload.strip()}"
    if action_type == ActionType.DISPATCH:
        payload_str = f" {payload.strip()}" if payload.strip() else ""
        return f"ACTION: DISPATCH {target.strip()}{payload_str}"
    return f"ACTION: {action_type.value} {target.strip()}"
