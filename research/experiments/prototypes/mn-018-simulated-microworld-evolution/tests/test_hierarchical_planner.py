"""Unit tests for HierarchicalPlanner and MissionGraph."""
import pytest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from hierarchical_planner import HierarchicalPlanner, MissionGraph, SubGoal
from microworld_engine import MicroworldEngine, WorldEntity


def test_mission_graph_topological_progression():
    engine = MicroworldEngine(domain="orbital_station")
    engine.register_entity(WorldEntity("valv_1", "valve", properties={"state": "CLOSED"}))
    engine.register_entity(WorldEntity("tank_1", "tank", properties={"pressure": 50}))

    graph = MissionGraph("test_mission", "Topological Life Support Restore")
    
    # Sub-goal 1: Open valve
    sg1 = SubGoal(
        goal_id="G1",
        title="Open Valve 1",
        description="Open valve 1 to enable pressure flow",
        prerequisites=[],
        allowed_actions=["open_valve valv_1"],
        completion_predicate=lambda eng: eng.get_entity("valv_1").properties.get("state") == "OPEN",
    )
    
    # Sub-goal 2: Pressurize tank
    sg2 = SubGoal(
        goal_id="G2",
        title="Pressurize Tank 1",
        description="Increase tank pressure to >= 100",
        prerequisites=["G1"],
        allowed_actions=["pressurize tank_1"],
        completion_predicate=lambda eng: eng.get_entity("tank_1").properties.get("pressure", 0) >= 100,
    )
    
    graph.add_subgoal(sg1)
    graph.add_subgoal(sg2)

    planner = HierarchicalPlanner(graph)
    
    # Initially active is G1
    adv, active = planner.update_plan(engine)
    assert active.goal_id == "G1"
    assert not graph.is_mission_accomplished(engine)

    # Complete G1 in engine
    engine.entities["valv_1"].properties["state"] = "OPEN"
    adv, active = planner.update_plan(engine)
    assert adv
    assert active.goal_id == "G2"

    # Complete G2 in engine
    engine.entities["tank_1"].properties["pressure"] = 105
    adv, active = planner.update_plan(engine)
    assert active is None
    assert graph.is_mission_accomplished(engine)


def test_scoped_prompt_bounded():
    engine = MicroworldEngine(domain="orbital_station")
    graph = MissionGraph("mission_alpha", "Test Mission")
    sg = SubGoal(
        goal_id="G1",
        title="Stabilize Bus",
        description="Align power flow",
        allowed_actions=["divert_power bus 50"],
    )
    graph.add_subgoal(sg)
    planner = HierarchicalPlanner(graph)
    planner.update_plan(engine)

    prompt = planner.render_scoped_prompt(engine)
    assert "[ACTIVE SUBGOAL G1: Stabilize Bus]" in prompt
    assert len(prompt) < 500  # Well within <= 128 tokens
