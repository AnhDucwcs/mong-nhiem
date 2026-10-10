"""Unit tests for ConcurrencyGuard and optimistic version drift."""
import pytest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from concurrency_guard import ConcurrencyGuard
from microworld_engine import MicroworldEngine, WorldEntity


def test_concurrency_guard_intercepts_stale_mutation():
    engine = MicroworldEngine(domain="industrial_microgrid")
    valve = WorldEntity("valve_1", "valve", version=1, properties={"flow": 10.0})
    engine.register_entity(valve)

    guard = ConcurrencyGuard()
    # Agent observes v1 at tick 0
    guard.record_observation("valve_1", version=1, tick=0)

    # In the meantime, world tick or background shock mutates valve_1 to v2
    engine.entities["valve_1"].version = 2
    engine.entities["valve_1"].properties["flow"] = 15.0

    # Arm 3 (enforce_guard=True): Action planned against v1 must be intercepted
    is_allowed, err_code, notice = guard.validate_action("valve_1", engine, enforce_guard=True)
    assert not is_allowed
    assert err_code == "STALE_VERSION_INTERCEPTED"
    assert guard.stale_violations_intercepted == 1
    assert "was v1, now v2" in notice

    # Guard updates observation to v2 upon interception
    # Subsequent action succeeds
    is_allowed2, err_code2, notice2 = guard.validate_action("valve_1", engine, enforce_guard=True)
    assert is_allowed2
    assert err_code2 is None


def test_concurrency_guard_arm1_arm2_unprotected():
    engine = MicroworldEngine(domain="industrial_microgrid")
    valve = WorldEntity("valve_1", "valve", version=1, properties={"flow": 10.0})
    engine.register_entity(valve)

    guard = ConcurrencyGuard()
    guard.record_observation("valve_1", version=1, tick=0)
    engine.entities["valve_1"].version = 2

    # Arm 1/2 (enforce_guard=False): Allows stale overwrite
    is_allowed, err_code, notice = guard.validate_action("valve_1", engine, enforce_guard=False)
    assert is_allowed
    assert err_code == "STALE_OVERWRITE_PERMITTED"
    assert guard.stale_overwrites_committed == 1
