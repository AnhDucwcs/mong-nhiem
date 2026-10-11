"""Hierarchical Planner with Topological Sub-Goal Management and Emergent Prerequisite Gating."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SubGoal:
    """Discrete sub-goal in topological mission graph."""
    subgoal_id: str
    description: str
    target_entity: str
    target_property: str
    operator: str  # '>=', '<=', '=='
    target_value: float
    candidate_actions: List[str] = field(default_factory=list)
    required_emergent_entity: Optional[str] = None  # If set, requires this entity to be active
    is_completed: bool = False

    def evaluate(self, current_value: float) -> bool:
        if self.operator == ">=":
            return current_value >= self.target_value
        elif self.operator == "<=":
            return current_value <= self.target_value
        elif self.operator == "==":
            return current_value == self.target_value
        return False


class HierarchicalPlanner:
    """Manages sequential execution of topological sub-goals."""

    def __init__(self, subgoals: List[SubGoal]) -> None:
        self.subgoals = copy.deepcopy(subgoals)
        self.active_index: int = 0

    @property
    def current_subgoal(self) -> Optional[SubGoal]:
        if self.active_index < len(self.subgoals):
            return self.subgoals[self.active_index]
        return None

    def is_all_completed(self) -> bool:
        return self.active_index >= len(self.subgoals)

    def update_progress(self, entities: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Evaluate active sub-goal against current entities.
        
        Returns:
            Tuple[advanced_to_next, newly_completed_subgoal_id_or_None]
        """
        active = self.current_subgoal
        if not active:
            return False, None

        # Check emergent entity prerequisite
        if active.required_emergent_entity:
            req_ent = entities.get(active.required_emergent_entity)
            if not req_ent or not req_ent.is_active:
                return False, None

        entity = entities.get(active.target_entity)
        if not entity or not entity.is_active:
            return False, None

        props = entity.properties if hasattr(entity, "properties") else entity
        curr_val = props.get(active.target_property)

        if curr_val is not None and active.evaluate(float(curr_val)):
            active.is_completed = True
            completed_id = active.subgoal_id
            self.active_index += 1
            return True, completed_id

        return False, None
