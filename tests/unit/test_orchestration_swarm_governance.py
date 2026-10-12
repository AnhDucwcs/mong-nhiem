"""Unit tests for swarm governance: MultiResourceArbiter, StarConsensusHub, and AsynchronousTransport."""

from mong_nhiem.orchestration.arbiter import MultiResourceArbiter
from mong_nhiem.orchestration.consensus import ByzantineAdmissionGate, StarConsensusHub
from mong_nhiem.orchestration.planner import HierarchicalPlanner, MissionGraph, SubGoal
from mong_nhiem.orchestration.transport import AsynchronousTransport


def test_arbiter_lease_lifecycle_and_stealing():
    arbiter = MultiResourceArbiter(default_ttl=4)
    arbiter.register_resource("res_alpha")

    # Agent 1 acquires at tick 0
    ok, msg = arbiter.acquire("res_alpha", "agent_1", current_tick=0)
    assert ok is True
    assert msg == "ACQUIRED"
    assert arbiter.get_held_resources("agent_1") == {"res_alpha"}

    # Agent 2 attempts acquisition while locked at tick 1 (should fail)
    ok2, msg2 = arbiter.acquire("res_alpha", "agent_2", current_tick=1)
    assert ok2 is False
    assert "LOCKED_BY_agent_1" in msg2

    # At tick 4, Agent 1's TTL expires. Agent 2 steals the lock
    ok3, msg3 = arbiter.acquire("res_alpha", "agent_2", current_tick=4)
    assert ok3 is True
    assert "STOLEN_EXPIRED_FROM_agent_1" in msg3
    assert arbiter.get_held_resources("agent_2") == {"res_alpha"}
    assert arbiter.get_held_resources("agent_1") == set()


def test_goal_conditioned_affordance_sorting():
    arbiter = MultiResourceArbiter(default_ttl=4)
    arbiter.register_resource("substation_north")
    arbiter.register_resource("substation_south")
    arbiter.register_resource("substation_east")

    # Agent assigned to stabilize substation_south
    affordances = arbiter.get_valid_affordances(
        agent_id="agent_1",
        assigned_goal="stabilize substation_south",
        all_resources=["substation_north", "substation_south", "substation_east"],
    )

    # South should be the first LEASE affordance offered!
    lease_affordances = [a for a in affordances if a.startswith("ACTION: LEASE")]
    assert lease_affordances[0] == "ACTION: LEASE substation_south"


def test_byzantine_admission_gate_and_consensus_hub():
    arbiter = MultiResourceArbiter(default_ttl=4)
    arbiter.register_resource("cargo_bay")
    gate = ByzantineAdmissionGate(valid_resources={"cargo_bay"})
    hub = StarConsensusHub(arbiter=arbiter, gate=gate)

    # Syntax violation
    ok, msg = hub.process_proposal("agent_1", "I would like to lease cargo_bay", current_tick=0)
    assert ok is False
    assert "SYNTAX_VIOLATION" in msg

    # Unauthorized ACT without lease
    ok, msg = hub.process_proposal("agent_1", "ACTION: ACT cargo_bay", current_tick=0)
    assert ok is False
    assert "UNAUTHORIZED" in msg

    # Valid LEASE proposal
    ok, msg = hub.process_proposal("agent_1", "ACTION: LEASE cargo_bay", current_tick=0)
    assert ok is True
    assert "LEASE_ACQUIRED" in msg

    # Authorized ACT with lease held
    ok, msg = hub.process_proposal("agent_1", "ACTION: ACT cargo_bay", current_tick=1)
    assert ok is True
    assert "ACT_SUCCESS" in msg


def test_asynchronous_transport():
    transport = AsynchronousTransport(min_latency=1, max_latency=3, seed=42)
    pkt = transport.send("agent_1", "hub", {"cmd": "ping"}, current_tick=0)
    assert pkt is not None
    assert pkt.arrival_tick >= 1

    # At tick 0, poll should find nothing
    assert transport.poll(0, "hub") == []

    # At max_latency tick 3, packet must be delivered
    delivered = transport.poll(3, "hub")
    assert len(delivered) == 1
    assert delivered[0].payload == {"cmd": "ping"}


def test_hierarchical_planner():
    mission = MissionGraph("test_mission")
    sg1 = SubGoal("sg1", "Phase 1", completion_predicate=lambda s: s.get("phase1_done", False))
    sg2 = SubGoal("sg2", "Phase 2", prerequisites=["sg1"], completion_predicate=lambda s: s.get("phase2_done", False))
    mission.add_subgoal(sg1)
    mission.add_subgoal(sg2)

    planner = HierarchicalPlanner(mission)
    state = {"phase1_done": False, "phase2_done": False}

    adv, active = planner.update_plan(state)
    assert active.goal_id == "sg1"

    # Mark phase 1 done
    state["phase1_done"] = True
    adv, active = planner.update_plan(state)
    assert adv is True
    assert active.goal_id == "sg2"
    assert mission.subgoals["sg1"].is_completed is True
