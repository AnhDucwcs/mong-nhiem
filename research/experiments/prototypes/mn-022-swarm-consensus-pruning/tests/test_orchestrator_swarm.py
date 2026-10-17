"""Integration tests for SwarmOrchestrator across experimental arms."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pytest
from src.async_world_engine import SwarmScenario
from src.orchestrator_swarm import SwarmOrchestrator


def make_test_scenario() -> SwarmScenario:
    resources = [f"substation_{i}" for i in range(1, 6)]
    return SwarmScenario(
        scenario_id="test_grid_01",
        domain="smart_microgrid",
        title="Test Microgrid",
        num_agents=5,
        max_ticks=15,
        initial_state={res: 20 for res in resources},
        target_state={res: 0 for res in resources},
        resources=resources,
        agent_goals={f"agent_{i}": f"Stabilize substation_{i}" for i in range(1, 6)},
    )


def test_orchestrator_arm3_resolves():
    scen = make_test_scenario()
    orch = SwarmOrchestrator(scen, arm="arm3", min_latency=0, max_latency=2, seed=42)
    res = orch.run_episode()

    assert res["success"] is True
    assert res["physical_breaches"] == 0
    assert res["race_collisions"] == 0
    assert res["max_tokens"] <= 512
    assert res["compaction_ratio"] >= 0.5


def test_orchestrator_arm1_race_collision():
    scen = make_test_scenario()
    # Force all agents to target the SAME resource without lease arbiter in Arm 1
    scen.resources = ["substation_1"]
    orch = SwarmOrchestrator(scen, arm="arm1", min_latency=0, max_latency=0, seed=42)
    res = orch.run_episode()

    # In Arm 1 without arbitration, multiple agents mutate simultaneously, producing race collisions
    assert res["race_collisions"] > 0
