"""Host-authoritative discrete simulated microworld runtime."""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, Optional

from mong_nhiem.core.invariants import ConservationInvariantGuard, InvariantViolationError
from mong_nhiem.orchestration.memento import MementoStack


class AuthoritativeMicroworld:
    """Authoritative discrete-tick simulated microworld with Memento rollback and invariant guards."""

    def __init__(
        self,
        initial_state: Optional[Dict[str, Any]] = None,
        invariant_guard: Optional[ConservationInvariantGuard] = None,
        max_mementos: int = 50,
    ):
        self.state: Dict[str, Any] = copy.deepcopy(initial_state or {})
        self.current_tick: int = 0
        self.invariant_guard = invariant_guard or ConservationInvariantGuard()
        self.memento_stack = MementoStack(max_depth=max_mementos)

        # Validate initial state invariants
        self.invariant_guard.enforce(self.state)

    def advance_tick(
        self,
        decay_fn: Optional[Callable[[Dict[str, Any], int], None]] = None,
    ) -> int:
        """Advances discrete world clock by 1 tick, optionally applying environmental decay.
        
        If decay causes invariant breach, world state rolls back automatically.
        """
        self.memento_stack.push(
            turn_index=self.current_tick,
            state=copy.deepcopy(self.state),
            action_key=f"tick_{self.current_tick}_pre_advance",
        )

        try:
            if decay_fn is not None:
                decay_fn(self.state, self.current_tick)
            self.invariant_guard.enforce(self.state)
            self.current_tick += 1
            return self.current_tick
        except InvariantViolationError:
            self.rollback()
            raise

    def apply_mutation(
        self,
        mutator_fn: Callable[[Dict[str, Any]], None],
        tag: str = "mutation",
    ) -> None:
        """Applies an in-place state mutation guarded by invariants and automatic Memento rollback."""
        self.memento_stack.push(
            turn_index=self.current_tick,
            state=copy.deepcopy(self.state),
            action_key=tag,
        )

        try:
            mutator_fn(self.state)
            self.invariant_guard.enforce(self.state)
        except InvariantViolationError:
            self.rollback()
            raise

    def rollback(self) -> bool:
        """Rolls back the world state to the most recent checkpoint on the Memento stack."""
        if not self.memento_stack.can_pop():
            return False

        memento = self.memento_stack.pop()
        if memento is not None:
            self.state = copy.deepcopy(memento.state)
            self.current_tick = memento.turn_index
            return True
        return False

    def get_state(self) -> Dict[str, Any]:
        """Returns an isolated deep copy of current authoritative world state."""
        return copy.deepcopy(self.state)

    def get_property(self, key: str, default: Any = None) -> Any:
        """Retrieves a top-level property value from the world state."""
        return self.state.get(key, default)
