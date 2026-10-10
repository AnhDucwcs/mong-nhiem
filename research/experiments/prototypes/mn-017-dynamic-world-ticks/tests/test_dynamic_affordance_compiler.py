"""Unit tests for dynamic_affordance_compiler.py."""
from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dynamic_affordance_compiler import DynamicAffordanceCompiler
from hierarchical_planner import SubGoal


def test_subgoal_affordance_isolation() -> None:
    sg1 = SubGoal(
        goal_id="G1",
        title="Lock Resource",
        description="Acquire lock",
        allowed_actions=["lock_resource node_1", "inspect_status node_1"],
    )

    grammar = DynamicAffordanceCompiler.compile_for_subgoal(
        subgoal=sg1,
        known_entity_ids=["node_1"],
        all_completed=False,
    )

    # Verifies root action grammar contains only G1 actions
    assert '"ACTION: DISPATCH inspect_status node_1"' in grammar
    assert '"ACTION: DISPATCH lock_resource node_1"' in grammar
    assert '"ACTION: RECALL node_1"' in grammar
    # Ensures future action 'migrate_payload' and 'RESOLVE' are NOT present
    assert "migrate_payload" not in grammar
    assert "ACTION: RESOLVE" not in grammar


def test_completed_mission_affords_only_resolve() -> None:
    grammar = DynamicAffordanceCompiler.compile_for_subgoal(
        subgoal=None,
        known_entity_ids=["node_1"],
        all_completed=True,
    )

    assert '"ACTION: RESOLVE COMPLETE"' in grammar
    assert "ACTION: DISPATCH" not in grammar


def test_global_grammar_contains_all_actions() -> None:
    all_actions = ["lock_res r1", "migrate_data r1", "verify_crc r1"]
    grammar = DynamicAffordanceCompiler.compile_global_grammar(
        all_actions=all_actions,
        known_entity_ids=["r1"],
        allow_resolve=True,
    )

    for act in all_actions:
        assert f'"ACTION: DISPATCH {act}"' in grammar
    assert '"ACTION: RESOLVE COMPLETE"' in grammar
