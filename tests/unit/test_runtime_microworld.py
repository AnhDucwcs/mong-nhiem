"""Unit tests for AuthoritativeMicroworld discrete physics runtime and rollback."""

import pytest
from mong_nhiem.core.invariants import ConservationInvariantGuard, InvariantViolationError
from mong_nhiem.runtime.microworld import AuthoritativeMicroworld


def test_microworld_discrete_tick_advance():
    initial = {"battery": 100.0, "status": "ONLINE"}
    world = AuthoritativeMicroworld(initial_state=initial)

    assert world.current_tick == 0
    assert world.get_property("battery") == 100.0

    # Advance tick with passive battery decay of -5.0
    def passive_decay(state, tick):
        state["battery"] -= 5.0

    world.advance_tick(decay_fn=passive_decay)
    assert world.current_tick == 1
    assert world.get_property("battery") == 95.0


def test_microworld_mutation_and_rollback_on_invariant_breach():
    initial = {"battery": 10.0}
    world = AuthoritativeMicroworld(initial_state=initial)

    # Valid mutation
    def valid_mut(state):
        state["battery"] = 5.0

    world.apply_mutation(valid_mut, tag="valid_discharge")
    assert world.get_property("battery") == 5.0

    # Invalid mutation (depletes battery into negative)
    def invalid_mut(state):
        state["battery"] = -20.0

    with pytest.raises(InvariantViolationError):
        world.apply_mutation(invalid_mut, tag="excessive_drain")

    # Authoritative state should have safely rolled back to 5.0!
    assert world.get_property("battery") == 5.0


def test_microworld_manual_rollback():
    initial = {"stage": 1, "battery": 100.0}
    world = AuthoritativeMicroworld(initial_state=initial)

    world.advance_tick()
    world.apply_mutation(lambda s: s.update({"stage": 2}))
    assert world.get_property("stage") == 2

    # Rollback to pre-mutation
    ok = world.rollback()
    assert ok is True
    assert world.get_property("stage") == 1
