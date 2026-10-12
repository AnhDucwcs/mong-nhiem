"""Unit tests for Topological AutoDream Memory Engine (MN-021)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.autodream_topo import TopologicalAutoDream
from src.causal_dag import CausalEventDAG
from src.world_rules import WorldRuleEngine


def test_scoped_prompt_generation_and_compaction():
    rules = WorldRuleEngine("martian_biosphere")
    autodream = TopologicalAutoDream(rules)
    dag = CausalEventDAG()

    dag.add_event("agent_alpha", "ACTIVATE_POWER", "power_grid", {"grid_power_available": 75}, tick=1)
    dag.add_event("agent_beta", "DEPLOY_VALVE", "water_loop", {"valve_state": "OPEN"}, tick=2)

    prompt = autodream.compile_scoped_prompt(
        agent_role="agent_alpha",
        mission_phase="STABILIZE",
        current_tick=3,
        private_observations={"power_grid": {"grid_power_available": 75}},
        event_dag=dag,
        delta_notices=["[UPDATE: water_loop evolved]"],
    )

    assert "AGENT: agent_alpha" in prompt
    assert "EPISTEMIC_UPDATE:" in prompt
    assert "LOCAL_OBSERVATIONS:" in prompt
    assert "CAUSAL_HISTORY:" in prompt
    assert "WORLD_RULES:" in prompt

    # Prompt length token check (well below 512 tokens)
    estimated_tokens = len(prompt) / 3.5
    assert estimated_tokens < 512

    # Compaction ratio
    compaction = autodream.compute_compaction_ratio()
    assert compaction >= 0.0
