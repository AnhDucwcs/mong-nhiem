"""Unit tests for hierarchical_planner.py."""
from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from hierarchical_planner import HierarchicalPlanner, MissionGraph, SubGoal
from world_engine import DynamicWorldEngine, WorldEntity


def test_topological_goal_advancement() -> None:
    engine = DynamicWorldEngine()
    engine.register_entity(WorldEntity(
        entity_id="res_a",
        entity_type="Lock",
        version=1,
        properties={"locked": False, "migrated": False, "verified": False},
    ))

    # Define 3 sub-goals
    g1 = SubGoal(
        goal_id="G1",
        title="Lock Resource",
        description="Acquire exclusive lock on res_a",
        allowed_actions=["lock_resource res_a"],
        completion_predicate=lambda eng: eng.get_entity("res_a").properties.get("locked") is True,
    )
    g2 = SubGoal(
        goal_id="G2",
        title="Migrate Data",
        description="Migrate payload to res_a",
        prerequisites=["G1"],
        allowed_actions=["migrate_payload res_a"],
        completion_predicate=lambda eng: eng.get_entity("res_a").properties.get("migrated") is True,
    )
    g3 = SubGoal(
        goal_id="G3",
        title="Verify Checksum",
        description="Verify SHA256 checksum",
        prerequisites=["G2"],
        allowed_actions=["verify_checksum res_a"],
        completion_predicate=lambda eng: eng.get_entity("res_a").properties.get("verified") is True,
    )

    mission = MissionGraph(mission_id="M_TEST", title="Test Migration Mission")
    mission.add_subgoal(g1)
    mission.add_subgoal(g2)
    mission.add_subgoal(g3)

    planner = HierarchicalPlanner(mission)

    # Initially G1 is active
    planner.update_plan(engine)
    assert planner.active_subgoal is not None
    assert planner.active_subgoal.goal_id == "G1"
    assert not mission.is_mission_accomplished(engine)

    # Satisfy G1
    engine.mutate_entity("res_a", {"locked": True})
    advanced, active_sg = planner.update_plan(engine)
    assert advanced is True
    assert active_sg is not None
    assert active_sg.goal_id == "G2"

    # Satisfy G2
    engine.mutate_entity("res_a", {"migrated": True})
    advanced, active_sg = planner.update_plan(engine)
    assert advanced is True
    assert active_sg is not None
    assert active_sg.goal_id == "G3"

    # Satisfy G3 -> Mission accomplished
    engine.mutate_entity("res_a", {"verified": True})
    advanced, active_sg = planner.update_plan(engine)
    assert active_sg is None
    assert mission.is_mission_accomplished(engine) is True


def test_scoped_prompt_budget() -> None:
    engine = DynamicWorldEngine()
    g1 = SubGoal(
        goal_id="G1",
        title="Lock Resource",
        description="Acquire lock",
        allowed_actions=["lock_resource res_1"],
    )
    mission = MissionGraph(mission_id="M_SCOPED", title="Scoped Test")
    mission.add_subgoal(g1)

    planner = HierarchicalPlanner(mission)
    planner.update_plan(engine)
    prompt = planner.render_scoped_prompt(engine)
    
    assert "ACTIVE SUBGOAL G1" in prompt
    assert "lock_resource res_1" in prompt
    # Strict brevity requirement <= 128 tokens
    approx_tokens = len(prompt) / 3.8
    assert approx_tokens <= 128
