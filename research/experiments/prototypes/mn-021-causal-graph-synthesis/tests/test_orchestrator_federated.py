"""Unit tests for Federated Orchestrator (MN-021)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from benchmarks.corpus_v1 import generate_benchmark_corpus
from src.orchestrator_federated import FederatedOrchestrator


def test_arm3_nominal_episode():
    corpus = generate_benchmark_corpus()
    nominal_case = corpus[0]  # MB-001 (nominal)

    orchestrator = FederatedOrchestrator(
        domain=nominal_case["domain"],
        initial_entities=nominal_case["initial_entities"],
        subgoals_agent1=nominal_case["agent1_goals"],
        subgoals_agent2=nominal_case["agent2_goals"],
        arm="arm3_federated_synthesis",
        track=1,
        max_turns=20,
        shock_config=nominal_case["shock_config"],
    )

    result = orchestrator.run_episode(nominal_case["case_id"])
    assert result["status"] == "PASS"
    assert result["committed_rule_breaches"] == 0
    assert result["committed_race_violations"] == 0
    assert result["max_prompt_tokens"] <= 512


def test_arm3_shock_episode():
    corpus = generate_benchmark_corpus()
    shock_case = next(c for c in corpus if c["shock_config"].get("has_shock"))

    orchestrator = FederatedOrchestrator(
        domain=shock_case["domain"],
        initial_entities=shock_case["initial_entities"],
        subgoals_agent1=shock_case["agent1_goals"],
        subgoals_agent2=shock_case["agent2_goals"],
        arm="arm3_federated_synthesis",
        track=1,
        max_turns=20,
        shock_config=shock_case["shock_config"],
    )

    result = orchestrator.run_episode(shock_case["case_id"])
    assert result["status"] == "PASS"
    assert result["committed_rule_breaches"] == 0
    assert result["max_prompt_tokens"] <= 512
