"""Host-Authoritative Semantic Invariant Gate.

Validates semantic causal preconditions and entity state compatibility prior to
committing proposed actions to the authoritative physical state vector.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class SemanticPrecondition:
    """Defines physical causal state requirements for a discrete action verb."""

    required_entity: str
    required_state: str
    incompatible_states: Set[str] = field(default_factory=set)


class SemanticInvariantGate:
    """Validates candidate action proposals against world state preconditions."""

    def __init__(
        self,
        preconditions: Optional[Dict[str, SemanticPrecondition]] = None,
    ) -> None:
        self._preconditions: Dict[str, SemanticPrecondition] = (
            dict(preconditions) if preconditions is not None else {}
        )
        self.semantic_breach_count: int = 0
        self.intercepted_violations: List[str] = []

    def register_precondition(
        self, action_verb: str, precondition: SemanticPrecondition
    ) -> None:
        """Registers a required precondition for an action verb."""
        clean_verb = action_verb.replace("ACTION:", "").strip()
        self._preconditions[clean_verb] = precondition

    def get_precondition(self, action: str) -> Optional[SemanticPrecondition]:
        """Retrieves registered precondition for an action."""
        clean_action = action.replace("ACTION:", "").strip()
        return self._preconditions.get(clean_action)

    def validate_action(
        self, action: str, world_state: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Verifies if an action proposal satisfies registered semantic preconditions.

        Args:
            action: Action string (e.g. 'ACTION: ENGAGE secondary_feed' or 'ENGAGE secondary_feed')
            world_state: Current world state dictionary mapping entity names to states.

        Returns:
            Tuple of (is_valid, optional_rejection_reason).
        """
        clean_action = action.replace("ACTION:", "").strip()

        if clean_action in self._preconditions:
            cond = self._preconditions[clean_action]
            curr_state = str(world_state.get(cond.required_entity, "UNKNOWN"))

            # Reject if current state is in explicitly forbidden incompatible states
            if curr_state in cond.incompatible_states:
                reason = (
                    f"INCOMPATIBLE_STATE_BREACH: Action '{clean_action}' requires entity "
                    f"'{cond.required_entity}' not to be in forbidden state '{curr_state}'"
                )
                self.semantic_breach_count += 1
                self.intercepted_violations.append(reason)
                return False, reason

            # Reject if required state is not strictly matched
            if curr_state != cond.required_state:
                reason = (
                    f"PRECONDITION_UNMET: Action '{clean_action}' requires "
                    f"'{cond.required_entity}'=='{cond.required_state}', found '{curr_state}'"
                )
                self.semantic_breach_count += 1
                self.intercepted_violations.append(reason)
                return False, reason

        return True, None
