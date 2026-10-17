"""Unit tests for AutoDreamSwarm context builder."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pytest
from src.autodream_swarm import AutoDreamSwarm
from src.consensus_pruner import SwarmEventNode


def test_autodream_prompt_assembly():
    builder = AutoDreamSwarm(token_ceiling=512)
    resource_states = {
        f"substation_{i}": {"val": 40, "holder": "FREE", "version": 1}
        for i in range(1, 6)
    }
    frontier_nodes = [
        SwarmEventNode(
            event_id=f"evt-{i}",
            tick=1,
            agent_id=f"agent_{i}",
            action_type="ACT",
            target=f"substation_{i}",
            vector_clock={f"agent_{i}": 1},
            parent_hashes=[],
            payload={},
            status="COMMITTED",
        )
        for i in range(1, 4)
    ]
    affordances = ["ACTION: LEASE substation_1", "ACTION: WAIT"]

    prompt, est_tok = builder.build_prompt(
        domain_name="smart_microgrid",
        current_tick=2,
        agent_id="agent_1",
        assigned_goal="Stabilize substation_1 to 0",
        resource_states=resource_states,
        frontier_nodes=frontier_nodes,
        held_leases=set(),
        valid_affordances=affordances,
    )

    assert "DOMAIN: smart_microgrid" in prompt
    assert "AGENT: agent_1" in prompt
    assert "[substation_1 v1 holder:FREE val:40]" in prompt
    assert est_tok <= 512
    assert est_tok > 20
