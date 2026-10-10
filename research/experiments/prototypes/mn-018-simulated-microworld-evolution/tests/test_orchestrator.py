"""Unit tests for MN018Orchestrator, MementoStack, and end-to-end execution."""
import pytest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from hierarchical_planner import MissionGraph, SubGoal
from memento_stack import MementoStack
from microworld_engine import MicroworldEngine, WorldEntity
from orchestrator import MN018Orchestrator


def test_memento_stack_rollback_and_negative_directive():
    engine = MicroworldEngine(domain="fleet_supply_chain")
    drone = WorldEntity("drone_1", "drone", properties={"payload_units": 2, "battery_percent": 80.0})
    engine.register_entity(drone)

    memento = MementoStack()
    memento.push(engine, action_attempted="dispatch_drone drone_1")

    # Corrupt or mutate state illegally
    engine.entities["drone_1"].properties["battery_percent"] = -10.0

    # Roll back
    cp = memento.rollback_latest(engine, reason="Battery depleted below zero")
    assert cp is not None
    assert engine.get_entity("drone_1").properties["battery_percent"] == 80.0
    assert "dispatch_drone drone_1" in memento.get_negative_actions()
    neg_dir = memento.render_negative_directives()
    assert "[NEGATIVE DIRECTIVE:" in neg_dir
    assert "dispatch_drone drone_1" in neg_dir


def test_orchestrator_end_to_end_arm3():
    nominal = {"nominal_coolant_liters": 100.0}
    engine = MicroworldEngine(domain="orbital_station", nominal_constants=nominal)

    p_bus = WorldEntity("power_bus", "bus", properties={"stored_kwh": 100.0})
    ls = WorldEntity("life_support", "env", properties={"o2_percent": 21.0, "pressure_kpa": 101.3})
    c_a = WorldEntity("coolant_loop_a", "loop", properties={"volume_liters": 40.0})
    c_b = WorldEntity("coolant_loop_b", "loop", properties={"volume_liters": 40.0})
    c_res = WorldEntity("coolant_reserve", "reserve", properties={"volume_liters": 20.0})

    for ent in [p_bus, ls, c_a, c_b, c_res]:
        engine.register_entity(ent)

    # Mission DAG: Subgoal 1 = balance coolant, Subgoal 2 = confirm stabilization
    mission = MissionGraph("M1", "Stabilize Station Thermal Loop")
    sg1 = SubGoal(
        goal_id="G1",
        title="Balance Coolant Loop",
        description="Transfer coolant to loop A",
        allowed_actions=["transfer_coolant reserve loop_a 5"],
        completion_predicate=lambda eng: eng.get_entity("coolant_loop_a").properties.get("volume_liters") == 45.0,
    )
    sg2 = SubGoal(
        goal_id="G2",
        title="Finalize Thermal Stability",
        description="Confirm station thermal equilibrium",
        prerequisites=["G1"],
        allowed_actions=["confirm_stabilization bus"],
        completion_predicate=lambda eng: eng.get_entity("power_bus").properties.get("stabilized") is True,
    )
    mission.add_subgoal(sg1)
    mission.add_subgoal(sg2)

    orch = MN018Orchestrator(
        engine=engine,
        mission=mission,
        arm="arm3",
        ticks_per_turn=1,
    )

    def action_executor(act_type, act_target, eng):
        if act_target == "transfer_coolant reserve loop_a 5":
            eng.entities["coolant_reserve"].properties["volume_liters"] = 15.0
            eng.entities["coolant_loop_a"].properties["volume_liters"] = 45.0
            eng.entities["coolant_reserve"].version += 1
            eng.entities["coolant_loop_a"].version += 1
            return True, "Coolant transferred successfully."
        elif act_target == "confirm_stabilization bus":
            eng.entities["power_bus"].properties["stabilized"] = True
            eng.entities["power_bus"].version += 1
            return True, "Thermal stability confirmed."
        return False, "Unknown action"

    # Turn 1: Build prompt, check token bounds
    prompt1 = orch.build_prompt("Balance station thermal loops.")
    assert orch.token_counter(prompt1) <= 512
    grammar1 = orch.get_gbnf_grammar(["transfer_coolant reserve loop_a 5", "confirm_stabilization bus"])
    assert '"ACTION: DISPATCH transfer_coolant reserve loop_a 5"' in grammar1

    # Execute Turn 1
    t1_metric = orch.step("ACTION: DISPATCH transfer_coolant reserve loop_a 5", action_executor)
    assert t1_metric.is_valid_format
    assert not t1_metric.is_stale_mutation
    assert not t1_metric.is_conservation_breach

    # Turn 2: G1 complete, now active is G2
    prompt2 = orch.build_prompt("Balance station thermal loops.")
    assert orch.token_counter(prompt2) <= 512
    grammar2 = orch.get_gbnf_grammar(["transfer_coolant reserve loop_a 5", "confirm_stabilization bus"])
    assert '"ACTION: DISPATCH confirm_stabilization bus"' in grammar2

    # Execute Turn 2
    t2_metric = orch.step("ACTION: DISPATCH confirm_stabilization bus", action_executor)
    assert t2_metric.is_valid_format

    # Turn 3: All subgoals complete -> Grammar permits only RESOLVE
    grammar3 = orch.get_gbnf_grammar(["transfer_coolant reserve loop_a 5", "confirm_stabilization bus"])
    assert '"ACTION: RESOLVE COMPLETE"' in grammar3

    t3_metric = orch.step("ACTION: RESOLVE COMPLETE", action_executor)
    assert not t3_metric.is_premature_resolution
    assert mission.is_mission_accomplished(engine)
