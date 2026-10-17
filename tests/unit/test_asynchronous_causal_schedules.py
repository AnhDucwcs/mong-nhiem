"""Targeted unit tests for tricky asynchronous execution schedules in Mộng Nhiễm.

Verifies:
1. Concurrent branches held simultaneously on the frontier.
2. Out-of-order packet arrival with causal dependency resolution.
3. Duplicate packet idempotency across asynchronous transport.
4. Rejected event causal isolation (causal sequence intact, world mutation zero).
5. Multi-parent causal join converging frontier without ancestor data loss.
"""

import pytest
from mong_nhiem.core.vector_clock import VectorClock
from mong_nhiem.knowledge.causal_dag import CausalEventDAG
from mong_nhiem.extensions.autodream.consolidator import FrontierBranchPruner
from mong_nhiem.orchestration.transport import AsynchronousTransport, NetworkPacket
from mong_nhiem.orchestration.arbiter import MultiResourceArbiter


def test_concurrent_branches_frontier_coexistence():
    """Verifies two concurrent branches are maintained on the frontier until explicit join."""
    pruner = FrontierBranchPruner(frontier_window=4)
    # Agent 1 produces A1 -> A2
    pruner.record_agent_event("agent_1", "hash_a1")
    pruner.record_agent_event("agent_1", "hash_a2")

    # Agent 2 produces B1 concurrently (never observed A1 or A2)
    pruner.record_agent_event("agent_2", "hash_b1")

    # Both active heads must be present on the frontier
    assert pruner.frontier_hashes == {"hash_a2", "hash_b1"}
    assert len(pruner.frontier_hashes) == 2


def test_duplicate_packet_idempotency():
    """Verifies transport and receiver do not double-merge clock on duplicate deliveries."""
    transport = AsynchronousTransport(min_latency=0, max_latency=0)
    # Send packet
    transport.send(
        sender_id="agent_1",
        recipient_id="host",
        payload={"action": "PING"},
        current_tick=0,
        vector_clock={"agent_1": 3},
    )

    host_clock = {"agent_1": 1, "host": 1}
    # First delivery
    pkts1 = transport.poll_and_merge(0, "host", host_clock)
    assert len(pkts1) == 1
    assert host_clock["agent_1"] == 3

    # Subsequent poll at tick 0 should yield 0 packets (already marked delivered)
    pkts2 = transport.poll_and_merge(0, "host", host_clock)
    assert len(pkts2) == 0
    assert host_clock["agent_1"] == 3


def test_rejected_event_causal_isolation():
    """Verifies rejected events record causal attempts without mutating state or breaking DAG."""
    dag = CausalEventDAG()
    arbiter = MultiResourceArbiter(default_ttl=5)
    arbiter.register_resource("res_core")

    # Agent 1 holds the lease
    ok1, _ = arbiter.acquire("res_core", "agent_1", current_tick=0)
    assert ok1 is True
    e1 = dag.add_event(
        actor="agent_1",
        action_name="LEASE",
        target_entity="res_core",
        state_delta={"holder": "agent_1"},
        tick=0,
    )

    # Agent 2 attempts to acquire and is REJECTED
    ok2, msg2 = arbiter.acquire("res_core", "agent_2", current_tick=1)
    assert ok2 is False
    assert "LOCKED_BY_agent_1" in msg2

    # The rejected attempt is recorded into DAG with state_delta={} to preserve provenance
    e2_rejected = dag.add_event(
        actor="agent_2",
        action_name="LEASE_ATTEMPT_REJECTED",
        target_entity="res_core",
        state_delta={},
        parent_ids=[e1.event_id],
        tick=1,
    )

    # Topological order remains valid and state delta of rejected event is empty
    topo = dag.get_topological_order()
    assert [n.event_id for n in topo] == [e1.event_id, e2_rejected.event_id]
    assert e2_rejected.state_delta == {}
    assert arbiter.get_held_resources("agent_2") == set()
    assert arbiter.get_held_resources("agent_1") == {"res_core"}


def test_out_of_order_causal_dependency_buffering():
    """Verifies that an event received before its causal parent can be detected via Vector Clock."""
    vc_parent = VectorClock({"agent_1": 1, "agent_2": 0})
    vc_child = VectorClock({"agent_1": 2, "agent_2": 0})

    # Host only knows up to agent_1: 0
    host_vc = VectorClock({"agent_1": 0, "agent_2": 0})

    # Child arrives before parent: host detects dependency gap (child's agent_1 clock is 2, host is 0)
    gap = vc_child.get("agent_1") - host_vc.get("agent_1")
    assert gap == 2  # Missing 2 events, must buffer child

    # Parent arrives: gap closes to 1
    host_vc.merge(vc_parent)
    assert vc_child.get("agent_1") - host_vc.get("agent_1") == 1


def test_causal_join_converges_without_history_loss():
    """Verifies that a multi-parent join collapses the active frontier while retaining full history."""
    dag = CausalEventDAG()
    e_root = dag.add_event(actor="host", action_name="INIT", target_entity="world", tick=0)

    # Two concurrent independent branches
    e_branch_a = dag.add_event(actor="agent_a", action_name="MOVE_WEST", target_entity="world", parent_ids=[e_root.event_id], tick=1)
    e_branch_b = dag.add_event(actor="agent_b", action_name="MOVE_EAST", target_entity="world", parent_ids=[e_root.event_id], tick=1)

    # Active frontier has 2 independent leaves
    assert len(dag.get_frontier()) == 2
    assert {n.event_id for n in dag.get_frontier()} == {e_branch_a.event_id, e_branch_b.event_id}

    # Consensus join merges both branches
    e_join = dag.add_event(
        actor="host",
        action_name="SYNCHRONIZE",
        target_entity="world",
        parent_ids=[e_branch_a.event_id, e_branch_b.event_id],
        tick=2,
    )

    # Frontier collapses to exactly 1 head
    frontier = dag.get_frontier()
    assert len(frontier) == 1
    assert frontier[0].event_id == e_join.event_id

    # Crucial: Complete ancestral provenance is 100% retained
    ancestors = dag.get_k_hop_ancestors(e_join.event_id, k_hops=2)
    ancestor_ids = {n.event_id for n in ancestors}
    assert e_branch_a.event_id in ancestor_ids
    assert e_branch_b.event_id in ancestor_ids
    assert e_root.event_id in ancestor_ids
    assert len(dag) == 4
