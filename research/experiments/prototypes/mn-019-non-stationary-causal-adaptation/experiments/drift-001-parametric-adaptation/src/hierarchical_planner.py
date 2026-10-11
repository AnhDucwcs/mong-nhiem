"""Hierarchical Sub-Goal Planner and Topological Phase Monitor."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class SubGoal:
    """A bounded topological sub-goal within a multi-phase task."""
    subgoal_id: str
    description: str
    target_entity: str
    target_property: str
    operator: str  # '>=', '<=', '==', '!='
    target_value: float
    candidate_actions: List[str]
    is_completed: bool = False

    def evaluate(self, current_value: float) -> bool:
        """Check whether current entity property satisfies the sub-goal condition."""
        if self.operator == ">=":
            return current_value >= self.target_value
        elif self.operator == "<=":
            return current_value <= self.target_value
        elif self.operator == "==":
            return abs(current_value - self.target_value) < 1e-3
        elif self.operator == "!=":
            return abs(current_value - self.target_value) >= 1e-3
        return False


class HierarchicalPlanner:
    """Manages ordered sub-goals and evaluates task progression."""

    def __init__(self, subgoals: List[SubGoal]):
        self.subgoals = list(subgoals)
        self.active_index = 0

    @property
    def current_subgoal(self) -> Optional[SubGoal]:
        """Return the current active sub-goal."""
        if 0 <= self.active_index < len(self.subgoals):
            return self.subgoals[self.active_index]
        return None

    def is_all_completed(self) -> bool:
        """Check whether all sub-goals have been satisfied."""
        return all(g.is_completed for g in self.subgoals)

    def update_progress(self, entities: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Evaluate the active sub-goal against current entity states.
        
        Returns:
            Tuple[advanced_to_next, newly_completed_subgoal_id_or_None]
        """
        active = self.current_subgoal
        if not active:
            return False, None

        entity = entities.get(active.target_entity)
        if not entity:
            return False, None

        props = entity.properties if hasattr(entity, "properties") else entity
        curr_val = props.get(active.target_property)

        if curr_val is not None and active.evaluate(float(curr_val)):
            active.is_completed = True
            completed_id = active.subgoal_id
            self.active_index += 1
            return True, completed_id

        return False, None
