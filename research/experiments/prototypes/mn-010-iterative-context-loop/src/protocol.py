"""Action Protocol Grammar parser and formatter for MN-010 Iterative Context Loop.

Grammar specification:
    ACTION: FETCH <target_entity_or_symbol>
    ACTION: RESOLVE <final_answer>
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class ActionType(str, Enum):
    FETCH = "FETCH"
    RESOLVE = "RESOLVE"
    INVALID = "INVALID"


@dataclass(frozen=True)
class AgentAction:
    action_type: ActionType
    argument: str
    raw: str


_ACTION_REGEX = re.compile(
    r"ACTION:\s*(FETCH|RESOLVE)(?:[:\s]\s*)([^\r\n]+)",
    re.IGNORECASE,
)
_THINK_TAG_REGEX = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def parse_action(text: str) -> AgentAction:
    """Parse a model generation text into a typed AgentAction.
    
    Strips reasoning tags (<think>...</think>) and searches for the latest
    ACTION directive conforming to the grammar.
    """
    if not text or not text.strip():
        return AgentAction(action_type=ActionType.INVALID, argument="", raw=text)

    cleaned = _THINK_TAG_REGEX.sub("", text).strip()
    
    # Search backwards or match lines
    matches = list(_ACTION_REGEX.finditer(cleaned))
    if not matches:
        return AgentAction(action_type=ActionType.INVALID, argument="", raw=text)

    # Use the last valid action emitted in the turn
    last_match = matches[-1]
    verb = last_match.group(1).upper()
    arg = last_match.group(2).strip()

    # Strip surrounding quotes if model added them
    if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
        arg = arg[1:-1].strip()

    action_type = ActionType.FETCH if verb == "FETCH" else ActionType.RESOLVE
    return AgentAction(
        action_type=action_type,
        argument=arg,
        raw=last_match.group(0),
    )


def format_action(action_type: ActionType, argument: str) -> str:
    """Format action enum and argument into canonical protocol string."""
    if action_type == ActionType.INVALID:
        raise ValueError("Cannot format INVALID action type")
    return f"ACTION: {action_type.value} {argument.strip()}"
