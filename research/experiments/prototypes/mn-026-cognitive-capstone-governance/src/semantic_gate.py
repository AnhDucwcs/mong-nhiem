"""Semantic Invariant Gate for Milestone MN-026.

Validates semantic preconditions, causal dependencies, and physical consistency
beyond structural GBNF syntax.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class SemanticPrecondition:
    required_entity: str
    required_state: str
    incompatible_states: Set[str] = field(default_factory=set)


class SemanticInvariantGate:
    """Validates action proposals against physical causal state preconditions."""

    def __init__(self):
        # Action -> required preconditions
        self.preconditions: Dict[str, SemanticPrecondition] = {
            "ENGAGE secondary_feed": SemanticPrecondition(
                required_entity="isolation_seal",
                required_state="SEALED",
                incompatible_states={"COMPROMISED", "OPEN"},
            ),
            "ENGAGE auxiliary_coolant": SemanticPrecondition(
                required_entity="bypass_valve",
                required_state="OPEN",
                incompatible_states={"SEALED", "BLOCKED"},
            ),
            "STABILIZE reactor_core": SemanticPrecondition(
                required_entity="coolant_pump",
                required_state="ACTIVE",
                incompatible_states={"OFFLINE", "CAVITATING"},
            ),
            "DIVERT bus_tie": SemanticPrecondition(
                required_entity="load_breaker",
                required_state="OPEN",
                incompatible_states={"TRIPPED", "LOCKED"},
            ),
            "ACTIVATE backup_oxygen": SemanticPrecondition(
                required_entity="manifold_seal",
                required_state="SEALED",
                incompatible_states={"RUPTURED", "LEAKING"},
            ),
        }
        self.semantic_breach_count = 0
        self.intercepted_violations: List[str] = []

    def validate_action(
        self, action: str, world_state: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Checks if an action violates semantic causal preconditions."""
        clean_action = action.replace("ACTION:", "").strip()

        if clean_action in self.preconditions:
            cond = self.preconditions[clean_action]
            curr_state = str(world_state.get(cond.required_entity, "UNKNOWN"))

            if curr_state in cond.incompatible_states or curr_state != cond.required_state:
                reason = (
                    f"Semantic precondition violated: {clean_action} requires "
                    f"{cond.required_entity}=={cond.required_state}, found {curr_state}"
                )
                self.intercepted_violations.append(reason)
                return False, reason

        return True, None
