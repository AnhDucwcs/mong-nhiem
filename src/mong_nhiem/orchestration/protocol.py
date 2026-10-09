"""Protocol definitions, data structures, and serialization for Cognitive Orchestration.

100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ActionType(str, Enum):
    """Categorical action types supported by Cognitive Orchestrator."""
    READ = "READ"
    INSPECT = "INSPECT"
    DISPATCH = "DISPATCH"
    RESOLVE = "RESOLVE"
    INVALID = "INVALID"


@dataclass(frozen=True)
class ToolAction:
    """Parsed structured tool action."""
    action_type: ActionType
    target: str = ""
    payload: str = ""
    raw_text: str = ""

    @property
    def action_key(self) -> str:
        """Deterministic canonical representation for deduplication and rollbacks."""
        if self.action_type == ActionType.DISPATCH:
            return f"DISPATCH:{self.target}:{self.payload}"
        elif self.action_type in (ActionType.READ, ActionType.INSPECT):
            return f"{self.action_type.value}:{self.target}"
        elif self.action_type == ActionType.RESOLVE:
            return f"RESOLVE:{self.payload}"
        return f"INVALID:{self.raw_text}"


@dataclass
class AffordanceSpec:
    """Active executable affordance set at a given execution turn."""
    reads: List[str] = field(default_factory=list)
    inspects: List[str] = field(default_factory=list)
    dispatches: List[Tuple[str, str]] = field(default_factory=list)  # (tool_name, payload)
    resolves: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Return True if no affordances are active."""
        return not (self.reads or self.inspects or self.dispatches or self.resolves)


@dataclass
class TurnRecord:
    """Auditable log of a single execution turn."""
    turn_index: int
    prompt: str
    prompt_tokens: int
    raw_response: str
    action: ToolAction
    observation: str
    is_rollback: bool = False
    latency_ms: float = 0.0
    used_grammar: bool = False
    compiled_gbnf: Optional[str] = None


@dataclass
class OrchestratorResult:
    """Final outcome of an orchestration session."""
    status: str  # 'SUCCESS', 'DEADLOCK_CYCLE_DETECTED', 'MAX_TURNS_EXCEEDED', 'BUDGET_OVERFLOW'
    answer: str
    total_turns: int
    rollback_count: int
    turns: List[TurnRecord]
    all_under_budget: bool
    total_latency_ms: float
    final_environment: Dict[str, Any]


def parse_action(raw: str) -> ToolAction:
    """Parse raw model completion into structured ToolAction.
    
    Tolerates leading/trailing markdown fences, whitespace, and formatting variances.
    """
    clean = raw.strip()
    clean = re.sub(r"^```(?:[a-zA-Z0-9_-]+)?\s*", "", clean)
    clean = re.sub(r"\s*```$", "", clean)
    clean = clean.strip()

    action_match = re.search(r"ACTION:\s*([A-Z]+)(?:\s+(.*))?", clean, re.IGNORECASE)
    if not action_match:
        return ToolAction(action_type=ActionType.INVALID, raw_text=clean)

    verb = action_match.group(1).upper()
    rest = (action_match.group(2) or "").strip()

    if verb == "READ":
        return ToolAction(action_type=ActionType.READ, target=rest, raw_text=clean)

    elif verb == "INSPECT":
        return ToolAction(action_type=ActionType.INSPECT, target=rest, raw_text=clean)

    elif verb == "DISPATCH":
        parts = rest.split(None, 1)
        tool = parts[0] if parts else ""
        payload = parts[1] if len(parts) > 1 else ""
        return ToolAction(action_type=ActionType.DISPATCH, target=tool, payload=payload, raw_text=clean)

    elif verb == "RESOLVE":
        return ToolAction(action_type=ActionType.RESOLVE, payload=rest, raw_text=clean)

    return ToolAction(action_type=ActionType.INVALID, raw_text=clean)


def format_action(action: ToolAction) -> str:
    """Format ToolAction into canonical prompt string."""
    if action.action_type == ActionType.DISPATCH:
        return f"ACTION: DISPATCH {action.target} {action.payload}".strip()
    elif action.action_type == ActionType.RESOLVE:
        return f"ACTION: RESOLVE {action.payload}".strip()
    elif action.action_type in (ActionType.READ, ActionType.INSPECT):
        return f"ACTION: {action.action_type.value} {action.target}".strip()
    return f"ACTION: INVALID {action.raw_text}".strip()


def format_affordance_prior(spec: AffordanceSpec) -> str:
    """Format ultra-compact affordance prior string for L1 attention seeding (<= 20 tokens)."""
    items: List[str] = []
    for r in spec.reads:
        items.append(f"READ:{r}")
    for i in spec.inspects:
        items.append(f"INSPECT:{i}")
    for tool, payload in spec.dispatches:
        items.append(f"DISPATCH:{tool}({payload})")
    for res in spec.resolves:
        items.append(f"RESOLVE:{res}")

    if not items:
        return "Available Affordances: []"

    # Truncate representation to keep strictly bounded <= 25 tokens
    if len(items) > 3:
        summary_items = items[:3] + [f"...+{len(items)-3} more"]
    else:
        summary_items = items
    return f"Available Affordances: [{', '.join(summary_items)}]"
