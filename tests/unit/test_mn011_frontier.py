"""Unit tests for MN-011 evaluation harness and frontier metric algorithms."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROTOTYPE_SRC = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-011-scaffolding-context-frontier"
    / "src"
)
if str(PROTOTYPE_SRC) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_SRC))

from frontier_evaluator import (
    build_scaffolded_causal_prompt,
    check_graph_reachability,
    compute_conversion_efficiency,
    parse_causal_graph,
)
from mong_nhiem.context import ContextPacker


def test_compute_conversion_efficiency() -> None:
    assert compute_conversion_efficiency(100, 200) == 0.5
    assert compute_conversion_efficiency(50, 50) == 1.0
    assert compute_conversion_efficiency(100, 50) == 1.0  # Capped at 1.0
    assert compute_conversion_efficiency(0, 500) == 0.0
    assert compute_conversion_efficiency(100, 0) == 0.0


def test_parse_and_reachability_causal_graph() -> None:
    edges = [
        "Alpha directly causes Beta.",
        "Beta directly causes Gamma.",
        "Delta directly causes Epsilon.",
    ]
    graph = parse_causal_graph(edges)
    assert "Alpha" in graph and "Beta" in graph
    assert graph["Alpha"] == ["Beta"]
    assert graph["Beta"] == ["Gamma"]

    # Positive reachability
    assert check_graph_reachability(graph, "Alpha", "Gamma") is True
    # Negative reachability
    assert check_graph_reachability(graph, "Alpha", "Epsilon") is False
    assert check_graph_reachability(graph, "Delta", "Gamma") is False


def test_build_scaffolded_causal_prompt() -> None:
    raw_edges = [
        "Node_A directly causes Node_B.",
        "Node_B directly causes Node_C.",
    ] + [
        f"Distractor_{i} directly causes Distractor_{i+1}."
        for i in range(50)
    ]
    packer = ContextPacker(max_budget=512)
    prompt, prompt_tokens, pruned_count = build_scaffolded_causal_prompt(
        raw_edges=raw_edges,
        source="Node_A",
        target="Node_C",
        query="Does Node_A eventually cause Node_C?",
        packer=packer,
    )

    assert prompt_tokens <= 512
    assert "Node_A directly causes Node_B" in prompt
    assert "Node_B directly causes Node_C" in prompt
    assert "Distractor_10" not in prompt  # Pruned out
    assert pruned_count == 2


def test_budget_frontier_knapsack_limits() -> None:
    facts = [f"Salient event #{i}: Status updated to OK." for i in range(20)]
    
    for budget in [256, 512, 1024]:
        packer = ContextPacker(max_budget=budget)
        packed = packer.pack(facts, query="Summarize system health.")
        assert packer.count_tokens(packed) <= budget
