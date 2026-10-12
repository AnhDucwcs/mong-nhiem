"""Unit tests for Causal Event DAG engine (MN-021)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pytest
from src.causal_dag import CausalEventDAG, CausalNode


def test_causal_node_hashing():
    dag = CausalEventDAG()
    node1 = dag.add_event(
        actor="agent_alpha",
        action_name="DISPATCH_VALVE",
        target_entity="water_loop",
        state_delta={"valve_state": "OPEN"},
        tick=1,
    )
    assert node1.node_hash != ""
    assert node1.parent_hash == "0" * 64

    # Child node chaining parent hash
    node2 = dag.add_event(
        actor="agent_beta",
        action_name="PRESSURIZE",
        target_entity="water_loop",
        state_delta={"water_line_pressure": 110},
        parent_ids=[node1.event_id],
        tick=2,
    )
    assert node2.parent_hash != "0" * 64
    assert node2.parent_ids == [node1.event_id]


def test_missing_parent_rejection():
    dag = CausalEventDAG()
    with pytest.raises(KeyError):
        dag.add_event(
            actor="agent_alpha",
            action_name="INVALID",
            target_entity="e1",
            state_delta={},
            parent_ids=["non_existent_evt"],
        )


def test_window_events_query():
    dag = CausalEventDAG()
    e1 = dag.add_event("a1", "ACT1", "power_grid", {"v": 1}, tick=2)
    e2 = dag.add_event("a2", "ACT2", "scrubber", {"s": 2}, tick=3)
    e3 = dag.add_event("a1", "ACT3", "power_grid", {"v": 5}, parent_ids=[e1.event_id], tick=5)

    res = dag.get_events_for_entity_in_window("power_grid", 1, 6)
    assert len(res) == 2
    assert res[0].event_id == e1.event_id
    assert res[1].event_id == e3.event_id

    # Outside window
    res_out = dag.get_events_for_entity_in_window("power_grid", 3, 4)
    assert len(res_out) == 0
