"""Unit tests for the promoted production mong_nhiem.context package."""
from __future__ import annotations

import pytest

from mong_nhiem.context import (
    ActionType,
    AgentAction,
    CircuitBreaker,
    CircuitBreakerStatus,
    CodebaseSlicer,
    ContextPacker,
    InvariantViolationError,
    IterativeCoordinator,
    TextChunk,
    assert_temporal_invariant,
    format_action,
    parse_action,
    sanitize_chat_tokens,
    slice_codebase,
    slice_graph_by_khop,
    slice_table_by_projection,
)


def test_sanitize_chat_tokens_all_architectures() -> None:
    # Llama 3
    assert "<|begin_of_text|>" not in sanitize_chat_tokens("Doc: <|begin_of_text|>")
    assert "<|eot_id|>" not in sanitize_chat_tokens("End: <|eot_id|>")
    # Qwen ChatML
    assert "<|im_start|>" not in sanitize_chat_tokens("Inject: <|im_start|>system")
    assert "<|im_end|>" not in sanitize_chat_tokens("Inject: <|im_end|>")
    assert "<|endoftext|>" not in sanitize_chat_tokens("Halt: <|endoftext|>")
    # Reasoning
    assert "<think>" not in sanitize_chat_tokens("CoT: <think>fake</think>")
    assert "</think>" not in sanitize_chat_tokens("CoT: <think>fake</think>")
    # Generic
    assert "<|extra_1|>" not in sanitize_chat_tokens("Token: <|extra_1|>")


def test_context_packer_budget_knapsack() -> None:
    packer = ContextPacker(max_budget=200)
    docs = [f"Paragraph {i}: This is detailed event logging for Unit_{i}. State is OK." for i in range(50)]
    packed = packer.pack(docs, query="What is the state of Unit_5?")
    
    assert packer.count_tokens(packed) <= 200
    assert "Unit_5" in packed
    assert "Query: What is the state of Unit_5?" in packed


def test_temporal_invariant_assertion() -> None:
    table = {"Alpha": "ACTIVE", "Beta": "STANDBY"}
    assert_temporal_invariant(["Alpha", "Beta"], table)

    with pytest.raises(InvariantViolationError) as exc_info:
        assert_temporal_invariant(["Alpha", "Gamma"], table)
    assert "Gamma" in str(exc_info.value)


def test_slice_graph_by_khop() -> None:
    graph = {
        "A": ["B"],
        "B": ["C", "D"],
        "C": ["E"],
        "D": [],
        "E": ["F"],
        "Z": ["Y"],
    }
    # 2-hop from A should reach A, B, C, D (not E, F, Z, Y)
    sub = slice_graph_by_khop(graph, target_entities={"A"}, max_hops=2)
    assert "A" in sub and "B" in sub and "C" in sub and "D" in sub
    assert "E" not in sub
    assert "Z" not in sub


def test_slice_table_by_projection() -> None:
    table = {
        "User_1": {"role": "ADMIN", "secret": "12345", "level": 10},
        "User_2": {"role": "GUEST", "secret": "99999", "level": 1},
        "User_3": {"role": "USER", "secret": "55555", "level": 2},
    }
    sub = slice_table_by_projection(table, active_entities={"User_1"}, target_columns={"role", "level"})
    assert sub == {"User_1": {"role": "ADMIN", "level": 10}}


def test_slice_codebase_ast() -> None:
    code = """
def short_helper(x):
    return x * 10

def unused_long_helper(y):
    a = y + 1
    b = a + 2
    c = b + 3
    d = c + 4
    e = d + 5
    return e

def target_fn(n):
    return short_helper(n) + 5
"""
    sliced = slice_codebase(code, target_function="target_fn", max_inline_lines=3, omit_uncalled=True)
    assert "def target_fn(n):" in sliced
    assert "def short_helper(x):" in sliced
    assert "def unused_long_helper" not in sliced


def test_action_protocol_parse_and_format() -> None:
    act_fetch = parse_action("ACTION: FETCH Entity_101")
    assert act_fetch.action_type == ActionType.FETCH
    assert act_fetch.argument == "Entity_101"
    assert format_action(act_fetch.action_type, act_fetch.argument) == "ACTION: FETCH Entity_101"

    act_res = parse_action("ACTION: RESOLVE 'Cluster Active'")
    assert act_res.action_type == ActionType.RESOLVE
    assert act_res.argument == "Cluster Active"

    act_inv = parse_action("No action here")
    assert act_inv.action_type == ActionType.INVALID


def test_circuit_breaker_cycle_prevention() -> None:
    cb = CircuitBreaker(max_turns=3)
    a1 = AgentAction(ActionType.FETCH, "Target_A", "raw")
    ok, status, _ = cb.validate_action(a1)
    assert ok and status == CircuitBreakerStatus.OK
    cb.record_step(a1)

    # Attempt to fetch same target again
    a1_repeat = AgentAction(ActionType.FETCH, "target_a", "raw")
    ok, status, reason = cb.validate_action(a1_repeat)
    assert not ok
    assert status == CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED
    assert "Cycle detected" in reason


def test_iterative_coordinator_multi_hop_run() -> None:
    db = {
        "Cluster_X": "Primary router is Gateway_99.",
        "Gateway_99": "Host IP is 192.168.1.99.",
    }
    responses = [
        "ACTION: FETCH Gateway_99",
        "ACTION: RESOLVE 192.168.1.99",
    ]
    resp_iter = iter(responses)

    coordinator = IterativeCoordinator(
        retriever_fn=lambda t: db.get(t),
        model_fn=lambda p: next(resp_iter),
        max_turns=3,
        max_budget=512,
    )

    result = coordinator.run(
        query="What is the host IP for Cluster_X?",
        initial_context=db["Cluster_X"],
    )
    assert result.status == "RESOLVED"
    assert result.answer == "192.168.1.99"
    assert result.total_turns == 2
    assert result.all_under_budget is True

