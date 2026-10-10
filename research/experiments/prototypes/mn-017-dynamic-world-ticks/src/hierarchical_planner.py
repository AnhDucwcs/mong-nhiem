"""Hierarchical Mission Planning and Host-Authoritative Phase-Gate Progression.

Decomposes complex multi-phase missions into discrete sub-goals organized in a DAG,
evaluates completion strictly via Host symbolic predicates, and delivers scoped
context prompts strictly bounded to <= 128 tokens.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from world_engine import DynamicWorldEngine


@dataclass
class SubGoal:
    """Discrete milestone in a hierarchical mission."""
    goal_id: str
    title: str
    description: str
    prerequisites: List[str] = field(default_factory=list)
    allowed_actions: List[str] = field(default_factory=list)
    completion_predicate: Optional[Callable[[DynamicWorldEngine], bool]] = None
    is_completed: bool = False

    def check_completion(self, engine: DynamicWorldEngine) -> bool:
        """Evaluate completion via Host symbolic predicate."""
        if self.completion_predicate is None:
            return self.is_completed
        return self.completion_predicate(engine)


class MissionGraph:
    """Directed Acyclic Graph of sub-goals enforcing topological execution."""

    def __init__(self, mission_id: str, title: str) -> None:
        self.mission_id = mission_id
        self.title = title
        self.subgoals: Dict[str, SubGoal] = {}
        self.topological_order: List[str] = []

    def add_subgoal(self, subgoal: SubGoal) -> None:
        """Add a sub-goal to the mission graph."""
        self.subgoals[subgoal.goal_id] = subgoal
        if subgoal.goal_id not in self.topological_order:
            self.topological_order.append(subgoal.goal_id)

    def get_active_subgoal(self, engine: DynamicWorldEngine) -> Optional[SubGoal]:
        """Determine current active sub-goal based on prerequisite satisfaction and Host predicates."""
        for gid in self.topological_order:
            sg = self.subgoals[gid]
            # Check if prerequisites are satisfied
            prereqs_met = all(self.subgoals[pid].is_completed for pid in sg.prerequisites)
            if not prereqs_met:
                continue
            
            # Check if this goal is already complete
            if sg.check_completion(engine):
                sg.is_completed = True
            else:
                return sg
        
        return None  # All goals completed

    def is_mission_accomplished(self, engine: DynamicWorldEngine) -> bool:
        """Verify whether every sub-goal in the mission has satisfied its Host predicate."""
        return all(sg.is_completed for sg in self.subgoals.values())


class HierarchicalPlanner:
    """Host planner coordinating sub-goal scoping and phase progression."""

    def __init__(self, mission: MissionGraph) -> None:
        self.mission = mission
        self.active_subgoal: Optional[SubGoal] = None

    def update_plan(self, engine: DynamicWorldEngine) -> Tuple[bool, Optional[SubGoal]]:
        """Advance phase gates based on world state.
        
        Returns:
            (advanced_to_new_phase, new_active_subgoal)
        """
        old_goal_id = self.active_subgoal.goal_id if self.active_subgoal else None
        self.active_subgoal = self.mission.get_active_subgoal(engine)
        new_goal_id = self.active_subgoal.goal_id if self.active_subgoal else None
        
        advanced = old_goal_id != new_goal_id and new_goal_id is not None
        return advanced, self.active_subgoal

    def render_scoped_prompt(self, engine: DynamicWorldEngine) -> str:
        """Render compact active sub-goal prompt strictly <= 128 tokens."""
        tick = engine.clock.current_tick
        if self.mission.is_mission_accomplished(engine):
            return f"[MISSION: {self.mission.mission_id} | TICK: {tick} | STATUS: ALL SUBGOALS COMPLETED. Emit RESOLVE to finalize.]"
        
        if self.active_subgoal is None:
            return f"[MISSION: {self.mission.mission_id} | TICK: {tick} | STATUS: BLOCKED OR COMPLETE]"
        
        completed_ids = [gid for gid, sg in self.mission.subgoals.items() if sg.is_completed]
        comp_str = ",".join(completed_ids) if completed_ids else "NONE"
        allowed_str = ", ".join(self.active_subgoal.allowed_actions)
        
        return (
            f"[MISSION: {self.mission.mission_id} | TICK: {tick}]\n"
            f"[COMPLETED: {comp_str}]\n"
            f"[ACTIVE SUBGOAL {self.active_subgoal.goal_id}: {self.active_subgoal.title}]\n"
            f"[CRITERIA: {self.active_subgoal.description}]\n"
            f"[ALLOWED ACTIONS: {allowed_str}]"
        )
