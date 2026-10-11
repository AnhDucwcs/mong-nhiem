"""Unit tests for Concurrency Arbiter & Lease Manager."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from concurrency_arbiter import ConcurrencyArbiter


def test_lease_grant_and_mutual_exclusion():
    arb = ConcurrencyArbiter(default_ttl=3)

    # Agent 1 acquires battery_bank
    assert arb.request_lease("agent_1", "battery_bank", current_tick=1) is True
    assert arb.get_lease_holder("battery_bank", current_tick=1) == "agent_1"

    # Agent 2 attempts to acquire battery_bank -> REJECTED
    assert arb.request_lease("agent_2", "battery_bank", current_tick=1) is False
    assert arb.can_mutate("agent_2", "battery_bank", current_tick=1) is False
    assert arb.can_mutate("agent_1", "battery_bank", current_tick=1) is True


def test_lease_expiration_and_release():
    arb = ConcurrencyArbiter(default_ttl=2)

    # Agent 1 acquires entity at tick 1, expires at tick 1 + 2 = 3
    arb.request_lease("agent_1", "solar_array", current_tick=1)

    # At tick 2: still valid
    assert arb.can_mutate("agent_1", "solar_array", current_tick=2) is True
    assert arb.can_mutate("agent_2", "solar_array", current_tick=2) is False

    # At tick 3: expired! Agent 2 can acquire
    assert arb.can_mutate("agent_2", "solar_array", current_tick=3) is True
    assert arb.request_lease("agent_2", "solar_array", current_tick=3) is True
    assert arb.get_lease_holder("solar_array", current_tick=3) == "agent_2"


def test_deadlock_cycle_detection():
    arb = ConcurrencyArbiter()

    # Agent 1 waits for Agent 2, Agent 2 waits for Agent 1
    waits = {"agent_1": "agent_2", "agent_2": "agent_1"}
    cycles = arb.detect_wait_for_deadlocks(waits)
    assert len(cycles) > 0
    assert "agent_1" in cycles[0]
    assert "agent_2" in cycles[0]


def test_discrete_signalling():
    arb = ConcurrencyArbiter()
    arb.send_signal("agent_1", "agent_2", "YIELD_REQUEST", target_entity="battery_bank", tick=2)

    signals = arb.retrieve_signals_for("agent_2")
    assert len(signals) == 1
    assert signals[0].sender_id == "agent_1"
    assert signals[0].signal_type == "YIELD_REQUEST"
    assert signals[0].target_entity == "battery_bank"

    # Inbox cleared
    assert len(arb.retrieve_signals_for("agent_2")) == 0
