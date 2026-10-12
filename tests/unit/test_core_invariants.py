"""Unit tests for core physical conservation invariants and guards."""

import pytest
from mong_nhiem.core.invariants import ConservationInvariantGuard, InvariantViolationError


def test_guard_non_negativity_pass():
    guard = ConservationInvariantGuard()
    state = {
        "generator": {"energy": 100.0, "power": 45.5, "status": "ONLINE"},
        "tank": {"coolant": 12.0, "pressure": 101.3},
    }
    is_valid, reason = guard.validate(state)
    assert is_valid is True
    assert reason is None
    # Enforce should not raise
    guard.enforce(state)


def test_guard_non_negativity_violation():
    guard = ConservationInvariantGuard()
    state = {
        "substation": {"battery": -5.0},
    }
    is_valid, reason = guard.validate(state)
    assert is_valid is False
    assert "battery" in reason
    assert "INVARIANT_BREACH" in reason

    with pytest.raises(InvariantViolationError) as exc_info:
        guard.enforce(state)
    assert "battery" in str(exc_info.value)


def test_guard_custom_rule_registration():
    guard = ConservationInvariantGuard()

    # Rule: Total energy in system must not exceed 500
    def total_energy_bound(state, context):
        total = state.get("grid_a", {}).get("energy", 0) + state.get("grid_b", {}).get("energy", 0)
        if total > 500:
            return False, f"Total energy {total} exceeds capacity 500"
        return True, None

    guard.register_rule("energy_cap", total_energy_bound)

    valid_state = {"grid_a": {"energy": 200}, "grid_b": {"energy": 250}}
    guard.enforce(valid_state)

    invalid_state = {"grid_a": {"energy": 300}, "grid_b": {"energy": 250}}
    with pytest.raises(InvariantViolationError) as exc_info:
        guard.enforce(invalid_state)
    assert "Total energy 550 exceeds capacity 500" in str(exc_info.value)
