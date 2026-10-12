"""Hierarchical multi-phase mission planning and dependency phase gating."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class SubGoal:
    """Discrete milestone in a hierarchical multi-stage mission."""

    goal_id: str
    title: str
    description: str = ""
    prerequisites: List[str] = field(default_factory=list)
    allowed_actions: List[str] = field(default_factory=list)
    completion_predicate: Optional[Callable[[Any], bool]] = None
    is_completed: bool = False

    def check_completion(self, context: Any) -> bool:
        """Evaluates completion via predicate if provided."""
        if self.completion_predicate is None:
            return self.is_completed
        try:
            return bool(self.completion_predicate(context))
        except Exception:
            return False


class MissionGraph:
    """Directed Acyclic Graph of sub-goals enforcing topological progression."""

    def __init__(self, mission_id: str, title: str = ""):
        self.mission_id = mission_id
        self.title = title
        self.subgoals: Dict[str, SubGoal] = {}
        self.topological_order: List[str] = []

    def add_subgoal(self, subgoal: SubGoal) -> None:
        """Appends a sub-goal to the mission graph."""
        self.subgoals[subgoal.goal_id] = subgoal
        if subgoal.goal_id not in self.topological_order:
            self.topological_order.append(subgoal.goal_id)

    def get_active_subgoal(self, context: Any = None) -> Optional[SubGoal]:
        """Determines the current active sub-goal whose prerequisites are satisfied."""
        for gid in self.topological_order:
            sg = self.subgoals[gid]
            if sg.is_completed:
                continue

            prereqs_met = all(
                pid in self.subgoals and self.subgoals[pid].is_completed
                for pid in sg.prerequisites
            )
            if not prereqs_met:
                continue

            if context is not None and sg.check_completion(context):
                sg.is_completed = True
            else:
                return sg

        return None

    def is_mission_accomplished(self, context: Any = None) -> bool:
        """Returns True if every sub-goal in the mission has been completed."""
        for gid in self.topological_order:
            sg = self.subgoals[gid]
            if not sg.is_completed and context is not None and sg.check_completion(context):
                sg.is_completed = True
        return all(sg.is_completed for sg in self.subgoals.values())


class HierarchicalPlanner:
    """Host planner coordinating sub-goal scoping, phase gating, and bounded prompt generation."""

    def __init__(self, mission: MissionGraph):
        self.mission = mission
        self.active_subgoal: Optional[SubGoal] = None

    def update_plan(self, context: Any = None) -> Tuple[bool, Optional[SubGoal]]:
        """Advances phase gates based on evaluation context.
        
        Returns:
            (advanced_to_new_phase: bool, active_subgoal: Optional[SubGoal])
        """
        old_goal_id = self.active_subgoal.goal_id if self.active_subgoal else None
        self.active_subgoal = self.mission.get_active_subgoal(context)
        new_goal_id = self.active_subgoal.goal_id if self.active_subgoal else None

        advanced = old_goal_id != new_goal_id and new_goal_id is not None
        return advanced, self.active_subgoal

    def render_scoped_prompt(self, current_tick: int = 0) -> str:
        """Renders compact active sub-goal prompt strictly <= 128 tokens."""
        if self.mission.is_mission_accomplished():
            return f"[MISSION: {self.mission.mission_id} | TICK: {current_tick} | STATUS: ALL SUBGOALS COMPLETED. Emit RESOLVE to finalize.]"

        if self.active_subgoal is None:
            return f"[MISSION: {self.mission.mission_id} | TICK: {current_tick} | STATUS: BLOCKED OR COMPLETE]"

        completed_ids = [gid for gid, sg in self.mission.subgoals.items() if sg.is_completed]
        comp_str = ",".join(completed_ids) if completed_ids else "NONE"
        allowed_str = ", ".join(self.active_subgoal.allowed_actions) if self.active_subgoal.allowed_actions else "ALL"

        return (
            f"[MISSION: {self.mission.mission_id} | TICK: {current_tick}]\n"
            f"[COMPLETED: {comp_str}]\n"
            f"[ACTIVE SUBGOAL {self.active_subgoal.goal_id}: {self.active_subgoal.title}]\n"
            f"[CRITERIA: {self.active_subgoal.description}]\n"
            f"[ALLOWED ACTIONS: {allowed_str}]"
        )
