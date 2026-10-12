"""Unit tests for SwarmConcurrencyArbiter."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pytest
from src.swarm_concurrency_arbiter import SwarmConcurrencyArbiter


def test_acquire_and_release():
    arbiter = SwarmConcurrencyArbiter(default_ttl=4)
    arbiter.register_resource("res_1")

    ok, status = arbiter.acquire("res_1", "agent_1", current_tick=0)
    assert ok is True
    assert status == "ACQUIRED"
    assert arbiter.leases["res_1"].holder_id == "agent_1"

    # Agent 1 releases
    ok_rel, rel_status = arbiter.release("res_1", "agent_1")
    assert ok_rel is True
    assert rel_status == "RELEASED"
    assert arbiter.leases["res_1"].state == "FREE"


def test_contention_and_lock_stealing():
    arbiter = SwarmConcurrencyArbiter(default_ttl=3)
    arbiter.register_resource("res_alpha")

    # Agent 1 acquires at tick 0, expires at tick 3
    ok1, _ = arbiter.acquire("res_alpha", "agent_1", current_tick=0, ttl_ticks=3)
    assert ok1 is True

    # Agent 2 attempts acquisition at tick 1 -> locked
    ok2, status2 = arbiter.acquire("res_alpha", "agent_2", current_tick=1)
    assert ok2 is False
    assert "LOCKED" in status2
    assert arbiter.conflict_intercepts == 1

    # At tick 3 (expired), Agent 2 attempts acquisition -> lock stealing succeeds
    ok3, status3 = arbiter.acquire("res_alpha", "agent_2", current_tick=3)
    assert ok3 is True
    assert "STOLEN_EXPIRED" in status3
    assert arbiter.lock_steals == 1
    assert arbiter.leases["res_alpha"].holder_id == "agent_2"


def test_lease_renewal():
    arbiter = SwarmConcurrencyArbiter(default_ttl=3)
    arbiter.register_resource("res_beta")

    arbiter.acquire("res_beta", "agent_1", current_tick=0, ttl_ticks=3)
    assert arbiter.leases["res_beta"].expires_tick == 3

    # Renew at tick 2
    ok_ren, status_ren = arbiter.acquire("res_beta", "agent_1", current_tick=2, ttl_ticks=4)
    assert ok_ren is True
    assert status_ren == "RENEWED"
    assert arbiter.leases["res_beta"].expires_tick == 6
