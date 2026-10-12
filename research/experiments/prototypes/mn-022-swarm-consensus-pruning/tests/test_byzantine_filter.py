"""Unit tests for ByzantineFilter."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pytest
from src.byzantine_filter import ByzantineFilter


def test_valid_actions():
    bfilter = ByzantineFilter({"substation_1", "substation_2"})

    res_lease = bfilter.validate_action("ACTION: LEASE substation_1", "agent_1", set())
    assert res_lease.is_valid is True
    assert res_lease.action_type == "LEASE"
    assert res_lease.target == "substation_1"

    res_act = bfilter.validate_action(
        "ACTION: ACT substation_1 STABILIZE", "agent_1", {"substation_1"}
    )
    assert res_act.is_valid is True
    assert res_act.action_type == "ACT"
    assert res_act.param == "STABILIZE"

    res_wait = bfilter.validate_action("ACTION: WAIT", "agent_1", set())
    assert res_wait.is_valid is True
    assert res_wait.action_type == "WAIT"


def test_syntax_malformed():
    bfilter = ByzantineFilter({"substation_1"})

    res_bad = bfilter.validate_action("I want to lease substation_1 please", "agent_1", set())
    assert res_bad.is_valid is False
    assert "SYNTAX_VIOLATION" in res_bad.reason
    assert bfilter.malformed_intercepts == 1


def test_unauthorized_act():
    bfilter = ByzantineFilter({"substation_1"})

    # Agent does not hold lease
    res_unauth = bfilter.validate_action(
        "ACTION: ACT substation_1 STABILIZE", "agent_1", set()
    )
    assert res_unauth.is_valid is False
    assert "UNAUTHORIZED" in res_unauth.reason
    assert bfilter.unauthorized_intercepts == 1


def test_unknown_resource():
    bfilter = ByzantineFilter({"substation_1"})

    res_unknown = bfilter.validate_action("ACTION: LEASE alien_reactor", "agent_1", set())
    assert res_unknown.is_valid is False
    assert "UNKNOWN_RESOURCE" in res_unknown.reason
    assert bfilter.constraint_intercepts == 1
