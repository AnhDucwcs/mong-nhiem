"""Standardized Benchmark Corpus v1 for MN-022 (N = 80 Swarm Scenarios, M = 5)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from typing import List
from src.async_world_engine import SwarmScenario


def get_corpus() -> List[SwarmScenario]:
    """Generates N = 80 standardized multi-agent swarm scenarios across 3 domains."""
    corpus: List[SwarmScenario] = []

    # Domain 1: Smart Microgrid Swarm Load Balancing (N = 27)
    for i in range(1, 28):
        resources = [f"substation_{j}" for j in range(1, 6)]
        # Imbalances vary across scenarios
        init_state = {
            f"substation_{j}": (20 if (i + j) % 2 == 0 else -20)
            for j in range(1, 6)
        }
        target_state = {f"substation_{j}": 0 for j in range(1, 6)}
        goals = {
            f"agent_{j}": f"Stabilize substation_{j} to 0 net imbalance"
            for j in range(1, 6)
        }
        corpus.append(
            SwarmScenario(
                scenario_id=f"grid_{i:03d}",
                domain="smart_microgrid",
                title=f"Microgrid Stabilization Case {i:03d}",
                num_agents=5,
                max_ticks=22,
                initial_state=init_state,
                target_state=target_state,
                resources=resources,
                agent_goals=goals,
            )
        )

    # Domain 2: Multi-Depot Autonomous Fleet Logistics (N = 27)
    for i in range(1, 28):
        resources = [f"bay_{chr(65 + j)}" for j in range(5)]  # bay_A to bay_E
        init_state = {f"bay_{chr(65 + j)}": "PENDING" for j in range(5)}
        target_state = {f"bay_{chr(65 + j)}": "DELIVERED" for j in range(5)}
        goals = {
            f"agent_{j+1}": f"Deliver cargo through bay_{chr(65 + j)}"
            for j in range(5)
        }
        corpus.append(
            SwarmScenario(
                scenario_id=f"fleet_{i:03d}",
                domain="fleet_logistics",
                title=f"Fleet Logistics Consolidation Case {i:03d}",
                num_agents=5,
                max_ticks=25,
                initial_state=init_state,
                target_state=target_state,
                resources=resources,
                agent_goals=goals,
            )
        )

    # Domain 3: Distributed High-Performance Cluster Scheduling (N = 26)
    for i in range(1, 27):
        resources = [f"node_{j}" for j in range(1, 6)]
        init_state = {f"node_{j}": "QUEUED" for j in range(1, 6)}
        target_state = {f"node_{j}": "COMPLETED" for j in range(1, 6)}
        goals = {
            f"agent_{j}": f"Schedule and complete pipeline stage on node_{j}"
            for j in range(1, 6)
        }
        corpus.append(
            SwarmScenario(
                scenario_id=f"cluster_{i:03d}",
                domain="cluster_scheduling",
                title=f"Cluster Scheduling Pipeline Case {i:03d}",
                num_agents=5,
                max_ticks=25,
                initial_state=init_state,
                target_state=target_state,
                resources=resources,
                agent_goals=goals,
            )
        )

    assert len(corpus) == 80, f"Expected 80 scenarios, got {len(corpus)}"
    return corpus
