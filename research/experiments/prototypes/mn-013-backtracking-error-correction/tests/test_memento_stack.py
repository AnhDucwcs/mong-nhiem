"""Unit tests for MN-013 MementoStack."""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest
from memento_stack import MementoStack


def test_memento_stack_push_pop_fidelity():
    stack = MementoStack(max_depth=3)
    initial_state = {"accounts": {"acc_a": 100, "acc_b": 50}, "log": ["init"]}
    stack.push(turn_index=1, state=initial_state, action_key="INIT")

    # Mutate external state to ensure deep copy isolation
    initial_state["accounts"]["acc_a"] = 999
    initial_state["log"].append("mutation")

    restored = stack.pop()
    assert restored.turn_index == 1
    assert restored.action_key == "INIT"
    assert restored.state["accounts"]["acc_a"] == 100
    assert restored.state["log"] == ["init"]


def test_memento_stack_max_depth():
    stack = MementoStack(max_depth=3)
    stack.push(1, {"val": 1})
    stack.push(2, {"val": 2})
    stack.push(3, {"val": 3})
    assert stack.depth == 3

    # Push 4th element - maintains bounded depth
    stack.push(4, {"val": 4})
    assert stack.depth == 3

    top = stack.pop()
    assert top.turn_index == 4


def test_memento_stack_empty_pop_raises():
    stack = MementoStack(max_depth=3)
    with pytest.raises(IndexError):
        stack.pop()
