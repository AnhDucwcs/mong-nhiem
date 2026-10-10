"""Unit tests for DynamicAffordanceCompiler and RECALL pruning."""
import pytest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dynamic_affordance import DynamicAffordanceCompiler
from hierarchical_planner import SubGoal


def test_compile_subgoal_grammar():
    sg = SubGoal(
        goal_id="G1",
        title="Vent Gas",
        description="Vent pressure",
        allowed_actions=["vent_valve v1", "close_valve v1"],
    )
    grammar = DynamicAffordanceCompiler.compile_for_subgoal(
        subgoal=sg,
        known_entity_ids=["v1", "tank1"],
        all_completed=False,
    )
    assert 'root ::= action [\\n]?' in grammar
    assert '"ACTION: DISPATCH vent_valve v1"' in grammar
    assert '"ACTION: DISPATCH close_valve v1"' in grammar
    assert '"ACTION: RECALL v1"' in grammar
    assert '"ACTION: RECALL tank1"' in grammar
    assert '"ACTION: RESOLVE COMPLETE"' not in grammar


def test_recall_pruning_for_fresh_entities():
    sg = SubGoal(
        goal_id="G1",
        title="Vent Gas",
        description="Vent pressure",
        allowed_actions=["vent_valve v1"],
    )
    # v1 is already up-to-date in working memory (version 3 in both)
    # tank1 is stale (working version 1, world version 2)
    # pump1 is unobserved (None in working)
    working_versions = {"v1": 3, "tank1": 1}
    current_versions = {"v1": 3, "tank1": 2, "pump1": 1}

    grammar = DynamicAffordanceCompiler.compile_for_subgoal(
        subgoal=sg,
        known_entity_ids=["v1", "tank1", "pump1"],
        all_completed=False,
        working_entity_versions=working_versions,
        current_entity_versions=current_versions,
    )
    # v1 should be pruned from RECALL to avoid degenerate loops!
    assert '"ACTION: RECALL v1"' not in grammar
    assert '"ACTION: RECALL tank1"' in grammar
    assert '"ACTION: RECALL pump1"' in grammar


def test_negative_actions_exclusion():
    sg = SubGoal(
        goal_id="G1",
        title="Vent Gas",
        description="Vent pressure",
        allowed_actions=["vent_valve v1", "close_valve v1"],
    )
    grammar = DynamicAffordanceCompiler.compile_for_subgoal(
        subgoal=sg,
        known_entity_ids=["v1"],
        negative_actions=["vent_valve v1"],
    )
    assert '"ACTION: DISPATCH vent_valve v1"' not in grammar
    assert '"ACTION: DISPATCH close_valve v1"' in grammar


def test_all_completed_allows_only_resolve():
    grammar = DynamicAffordanceCompiler.compile_for_subgoal(
        subgoal=None,
        known_entity_ids=["v1", "tank1"],
        all_completed=True,
    )
    assert '"ACTION: RESOLVE COMPLETE"' in grammar
    assert 'ACTION: DISPATCH' not in grammar
    assert 'ACTION: RECALL' not in grammar
