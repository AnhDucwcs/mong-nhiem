"""Unit tests for CausalEventDAG and DynamicSchemaRegistry."""

import pytest
from mong_nhiem.knowledge.causal_dag import CausalEventDAG
from mong_nhiem.knowledge.schema_registry import DynamicSchemaRegistry


def test_causal_dag_multi_parent_chaining():
    dag = CausalEventDAG()
    e1 = dag.add_event(actor="agent_1", action_name="INIT", target_entity="sub_a", tick=1)
    e2 = dag.add_event(actor="agent_2", action_name="INIT", target_entity="sub_b", tick=1)
    # e3 depends on both e1 and e2
    e3 = dag.add_event(
        actor="agent_1",
        action_name="LINK",
        target_entity="sub_a",
        parent_ids=[e1.event_id, e2.event_id],
        tick=2,
    )

    assert e3.parent_hash != "0" * 64
    assert len(e3.parent_ids) == 2
    ancestors = dag.get_k_hop_ancestors(e3.event_id, k_hops=1)
    assert len(ancestors) == 2
    ancestor_ids = {a.event_id for a in ancestors}
    assert e1.event_id in ancestor_ids
    assert e2.event_id in ancestor_ids


def test_causal_dag_topological_order():
    dag = CausalEventDAG()
    e1 = dag.add_event(actor="a", action_name="A", target_entity="t1", tick=1)
    e2 = dag.add_event(actor="b", action_name="B", target_entity="t2", parent_ids=[e1.event_id], tick=2)
    e3 = dag.add_event(actor="c", action_name="C", target_entity="t3", parent_ids=[e2.event_id], tick=3)

    topo = dag.get_topological_order()
    assert [n.event_id for n in topo] == [e1.event_id, e2.event_id, e3.event_id]


def test_dynamic_schema_registry_lifecycle():
    registry = DynamicSchemaRegistry()
    registry.register_entity_type("battery", required_properties=["capacity", "soc"])

    # Emerge entity missing required prop should raise
    with pytest.raises(ValueError):
        registry.emerge_entity("bat_1", "battery", {"capacity": 100})

    # Emerge valid entity
    bat = registry.emerge_entity("bat_1", "battery", {"capacity": 100, "soc": 80})
    assert bat["version"] == 1
    assert registry.is_active("bat_1") is True

    # Mutate schema
    mutated = registry.mutate_schema("bat_1", add_properties={"temperature": 25.0})
    assert mutated["version"] == 2
    assert mutated["properties"]["temperature"] == 25.0

    # Add relation
    registry.emerge_entity("inv_1", "inverter", {})
    registry.add_relation("bat_1", "CONNECTED_TO", "inv_1")
    rels = registry.get_relations("bat_1")
    assert rels["CONNECTED_TO"] == ["inv_1"]

    # Retire entity
    registry.retire_entity("bat_1", reason="decommissioned")
    assert registry.is_active("bat_1") is False
    assert registry.get_entity("bat_1") is None


def test_causal_dag_frontier_preservation_and_join():
    dag = CausalEventDAG()
    # Two independent concurrent events by different agents
    e1 = dag.add_event(actor="agent_1", action_name="MINE", target_entity="ore_1", tick=1)
    e2 = dag.add_event(actor="agent_2", action_name="CHOP", target_entity="tree_1", tick=1)

    # Both must be present on the frontier (|F| == 2)
    frontier = dag.get_frontier()
    assert len(frontier) == 2
    frontier_ids = {n.event_id for n in frontier}
    assert e1.event_id in frontier_ids
    assert e2.event_id in frontier_ids
    assert len(dag.get_frontier_hashes()) == 2

    # Agent 1 continues independently
    e3 = dag.add_event(actor="agent_1", action_name="REFINE", target_entity="ore_1", parent_ids=[e1.event_id], tick=2)
    frontier_ids2 = {n.event_id for n in dag.get_frontier()}
    # Frontier now contains e3 and e2 (e1 was consumed by e3, e2 is untouched)
    assert len(frontier_ids2) == 2
    assert e3.event_id in frontier_ids2
    assert e2.event_id in frontier_ids2

    # A join/consensus event merges e3 and e2
    e4 = dag.add_event(
        actor="arbiter",
        action_name="SYNCHRONIZE",
        target_entity="system",
        parent_ids=[e3.event_id, e2.event_id],
        tick=3,
    )
    frontier_ids3 = {n.event_id for n in dag.get_frontier()}
    # Frontier collapses to exactly {e4}
    assert len(frontier_ids3) == 1
    assert e4.event_id in frontier_ids3
