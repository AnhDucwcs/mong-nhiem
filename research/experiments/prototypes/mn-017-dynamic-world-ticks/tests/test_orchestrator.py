"""Unit tests for orchestrator.py."""
from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from hierarchical_planner import MissionGraph, SubGoal
from orchestrator import MN017Orchestrator
from world_engine import DynamicWorldEngine, WorldEntity


def test_orchestrator_turn_stepping() -> None:
    engine = DynamicWorldEngine()
    engine.register_entity(WorldEntity(
        entity_id="res_alpha",
        entity_type="Storage",
        version=1,
        properties={"locked": False},
        ttl=10,
    ))

    g1 = SubGoal(
        goal_id="G1",
        title="Lock Alpha",
        description="Lock resource alpha",
        allowed_actions=["lock_resource res_alpha"],
        completion_predicate=lambda eng: eng.get_entity("res_alpha").properties.get("locked") is True,
    )
    mission = MissionGraph("M_ORCH", "Orchestrator Test")
    mission.add_subgoal(g1)

    orch = MN017Orchestrator(engine, mission, arm="arm3", ticks_per_turn=1)

    # 1. Build prompt
    prompt = orch.build_prompt("Global mission specification")
    assert "ACTIVE SUBGOAL G1" in prompt

    # 2. Check grammar
    grammar = orch.get_gbnf_grammar(["lock_resource res_alpha", "future_act res_alpha"])
    assert "lock_resource res_alpha" in grammar
    assert "future_act" not in grammar

    # 3. Step with RECALL
    def dummy_executor(act_type, act_target, eng):
        return True, "OK"

    metric_recall = orch.step("ACTION: RECALL res_alpha", dummy_executor)
    assert metric_recall.action_type == "RECALL"
    assert "res_alpha" in orch.working_entities

    # 4. In the background, an external drift event mutates res_alpha from v1 -> v2
    engine.mutate_entity("res_alpha", {"metadata": "drifted"})

    # Turn 2: Attempt DISPATCH with stale v1 observation
    # ConcurrencyGuard intercepts stale dispatch and emits DELTA NOTICE.
    def lock_executor(act_type, act_target, eng):
        if act_target == "lock_resource res_alpha":
            eng.mutate_entity("res_alpha", {"locked": True})
            return True, "LOCKED"
        return False, "FAIL"

    metric_stale = orch.step("ACTION: DISPATCH lock_resource res_alpha", lock_executor)
    assert metric_stale.action_type == "DISPATCH"
    assert metric_stale.is_stale_mutation is True
    assert orch.guard.stale_violations_intercepted == 1
    assert len(orch.pending_delta_notices) > 0

    # 5. Build prompt for Turn 3: Context includes DELTA NOTICE
    prompt_t3 = orch.build_prompt("Global mission specification")
    assert "DELTA NOTICE" in prompt_t3

    # 6. Turn 3: Dispatched with refreshed version -> Succeeds!
    metric_fresh = orch.step("ACTION: DISPATCH lock_resource res_alpha", lock_executor)
    assert metric_fresh.action_type == "DISPATCH"
    assert metric_fresh.is_stale_mutation is False
    assert mission.is_mission_accomplished(engine) is True
