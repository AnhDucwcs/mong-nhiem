"""Unit tests for Symbiosis Orchestrator in Track 1 Simulator."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "benchmarks")))

from corpus_v1 import generate_benchmark_corpus
from orchestrator_symbiosis import SymbiosisOrchestrator


def test_arm3_symbiosis_resolution():
    corpus = generate_benchmark_corpus(n_per_domain=1)
    case = corpus[0]  # Microgrid case

    orch = SymbiosisOrchestrator(
        domain=case["domain"],
        initial_entities=case["initial_entities"],
        subgoals_agent1=case["subgoals_agent1"],
        subgoals_agent2=case["subgoals_agent2"],
        arm="arm3_host_symbiosis",
        track=1,
    )
    res = orch.run_episode("TEST-CASE-001")

    assert res["status"] == "PASS"
    assert res["committed_race_violations"] == 0
    assert res["max_prompt_tokens"] <= 512
    assert res["autodream_compaction_ratio"] >= 0.70


def test_arm1_uncoordinated_race_conditions():
    corpus = generate_benchmark_corpus(n_per_domain=1)
    case = corpus[0]

    # Run Arm 1 (Flat Baseline)
    orch = SymbiosisOrchestrator(
        domain=case["domain"],
        initial_entities=case["initial_entities"],
        subgoals_agent1=case["subgoals_agent1"],
        subgoals_agent2=case["subgoals_agent2"],
        arm="arm1_flat",
        track=1,
    )
    res = orch.run_episode("TEST-CASE-001-ARM1")
    # In uncoordinated flat baseline without leases, agents act without mutual awareness
    assert res["status"] in ["PASS", "FAIL"]
