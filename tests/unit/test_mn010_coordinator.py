"""Unit tests for MN-010 Iterative Context Coordinator prototype."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROTOTYPE_SRC = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-010-iterative-context-loop" / "src"
if str(PROTOTYPE_SRC) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_SRC))

from circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from coordinator import IterativeCoordinator
from protocol import ActionType, AgentAction, format_action, parse_action


def test_protocol_parse_action() -> None:
    # Standard format
    a1 = parse_action("ACTION: FETCH func_a")
    assert a1.action_type == ActionType.FETCH
    assert a1.argument == "func_a"

    a2 = parse_action("ACTION: RESOLVE 42")
    assert a2.action_type == ActionType.RESOLVE
    assert a2.argument == "42"

    # Multiline with reasoning tags
    a3 = parse_action("<think>I need more facts</think>\nI will now inspect.\nACTION: FETCH target_entity")
    assert a3.action_type == ActionType.FETCH
    assert a3.argument == "target_entity"

    # Quoted argument
    a4 = parse_action('ACTION: RESOLVE "Hello World"')
    assert a4.action_type == ActionType.RESOLVE
    assert a4.argument == "Hello World"

    # Colon format
    a5 = parse_action("ACTION: FETCH: helper_node")
    assert a5.action_type == ActionType.FETCH
    assert a5.argument == "helper_node"

    # Invalid
    a6 = parse_action("I am not sure what to do.")
    assert a6.action_type == ActionType.INVALID
    assert a6.argument == ""


def test_circuit_breaker_max_turns() -> None:
    cb = CircuitBreaker(max_turns=3)
    fetch_action = AgentAction(ActionType.FETCH, "node_1", "raw")
    
    # Turn 1
    valid, status, _ = cb.validate_action(fetch_action)
    assert valid
    cb.record_step(fetch_action)

    # Turn 2
    fetch_action2 = AgentAction(ActionType.FETCH, "node_2", "raw")
    valid, status, _ = cb.validate_action(fetch_action2)
    assert valid
    cb.record_step(fetch_action2)

    # Turn 3
    fetch_action3 = AgentAction(ActionType.FETCH, "node_3", "raw")
    valid, status, _ = cb.validate_action(fetch_action3)
    assert valid
    cb.record_step(fetch_action3)

    # Turn 4 (Exceeds max 3 turns)
    fetch_action4 = AgentAction(ActionType.FETCH, "node_4", "raw")
    valid, status, reason = cb.validate_action(fetch_action4)
    assert not valid
    assert status == CircuitBreakerStatus.TRIPPED_MAX_TURNS


def test_circuit_breaker_cycle_detection() -> None:
    cb = CircuitBreaker(max_turns=3)
    fetch_a = AgentAction(ActionType.FETCH, "Node_Alpha", "raw")
    valid, status, _ = cb.validate_action(fetch_a)
    assert valid
    cb.record_step(fetch_a)

    # Repeated fetch with different casing
    fetch_a_repeat = AgentAction(ActionType.FETCH, "node_alpha", "raw")
    valid, status, reason = cb.validate_action(fetch_a_repeat)
    assert not valid
    assert status == CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED
    assert "Cycle detected" in reason


def test_circuit_breaker_empty_target() -> None:
    cb = CircuitBreaker(max_turns=3)
    empty_fetch = AgentAction(ActionType.FETCH, "   ", "raw")
    valid, status, reason = cb.validate_action(empty_fetch)
    assert not valid
    assert status == CircuitBreakerStatus.TRIPPED_EMPTY_TARGET


def test_iterative_coordinator_resolution() -> None:
    knowledge_base = {
        "User_101": "User_101 assigned role 'TeamLead'. Direct supervisor: User_001.",
        "User_001": "User_001 department: Infrastructure Security.",
    }

    def mock_retriever(target: str):
        return knowledge_base.get(target)

    # Simulated model: turn 1 fetches supervisor, turn 2 resolves department
    responses = [
        "ACTION: FETCH User_001",
        "ACTION: RESOLVE Infrastructure Security",
    ]
    resp_iter = iter(responses)

    def mock_model(prompt: str) -> str:
        return next(resp_iter)

    coordinator = IterativeCoordinator(
        retriever_fn=mock_retriever,
        model_fn=mock_model,
        max_turns=3,
        max_budget=512,
    )

    res = coordinator.run(
        query="What department does User_101's direct supervisor belong to?",
        initial_context=knowledge_base["User_101"],
    )

    assert res.status == "RESOLVED"
    assert res.answer == "Infrastructure Security"
    assert res.total_turns == 2
    assert "user_001" in res.visited_targets
    assert res.all_under_budget is True


def test_iterative_coordinator_cycle_trip() -> None:
    knowledge_base = {"A": "A calls B", "B": "B calls A"}

    def mock_retriever(target: str):
        return knowledge_base.get(target)

    responses = [
        "ACTION: FETCH B",
        "ACTION: FETCH B",  # Cycle
    ]
    resp_iter = iter(responses)

    coordinator = IterativeCoordinator(
        retriever_fn=mock_retriever,
        model_fn=lambda prompt: next(resp_iter),
        max_turns=3,
    )

    res = coordinator.run(query="Solve loop", initial_context="A calls B")
    assert res.status == CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED.value
    assert res.total_turns == 2
