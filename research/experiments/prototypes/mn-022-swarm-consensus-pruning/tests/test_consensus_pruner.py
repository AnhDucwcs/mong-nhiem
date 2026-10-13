"""Unit tests for ConsensusPruner."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pytest
from src.consensus_pruner import ConsensusPruner


def test_record_and_hash():
    agents = ["agent_1", "agent_2", "agent_3", "agent_4", "agent_5"]
    pruner = ConsensusPruner(agents, frontier_window=3)

    node1 = pruner.record_event(
        event_id="evt-1",
        tick=0,
        agent_id="agent_1",
        action_type="LEASE",
        target="res_1",
        payload={},
    )
    assert node1.node_hash != ""
    assert node1.vector_clock["agent_1"] == 1
    assert node1.vector_clock["agent_2"] == 0
    assert pruner.frontier_hashes == {node1.node_hash}

    # Concurrent event by agent_2 without observing node1
    node2 = pruner.record_event(
        event_id="evt-2",
        tick=1,
        agent_id="agent_2",
        action_type="ACT",
        target="res_2",
        payload={},
    )
    assert node2.node_hash != ""
    assert node2.parent_hashes == []
    # Both concurrent branches remain in the frontier
    assert pruner.frontier_hashes == {node1.node_hash, node2.node_hash}

    # Causal join event observing both node1 and node2
    node3 = pruner.record_event(
        event_id="evt-3",
        tick=2,
        agent_id="agent_1",
        action_type="SYNC",
        target="res_1",
        payload={},
        external_parent_hashes=[node2.node_hash],
    )
    assert set(node3.parent_hashes) == {node1.node_hash, node2.node_hash}
    # Both parents collapsed into join node
    assert pruner.frontier_hashes == {node3.node_hash}


def test_vector_clock_merge():
    agents = ["agent_1", "agent_2"]
    pruner = ConsensusPruner(agents)
    pruner.tick_agent_clock("agent_1")  # agent_1: 1
    pruner.tick_agent_clock("agent_2")
    pruner.tick_agent_clock("agent_2")  # agent_2: 2

    # Merge agent_2 clock into agent_1
    pruner.merge_clock("agent_1", pruner.vector_clocks["agent_2"])
    assert pruner.vector_clocks["agent_1"] == {"agent_1": 1, "agent_2": 2}


def test_pruning_and_compaction():
    agents = ["agent_1", "agent_2", "agent_3", "agent_4", "agent_5"]
    pruner = ConsensusPruner(agents, frontier_window=2)

    for t in range(10):
        aid = agents[t % 5]
        pruner.record_event(
            event_id=f"evt-{t}",
            tick=t,
            agent_id=aid,
            action_type="ACT",
            target=f"res_{t % 5}",
            payload={},
        )

    # At tick 9 with frontier_window=2, active frontier includes ticks >= 7
    active = pruner.prune_frontier(current_tick=9)
    assert len(active) <= 5
    metrics = pruner.get_compaction_metrics()
    assert metrics["compaction_ratio"] >= 0.5
