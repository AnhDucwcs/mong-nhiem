"""Unit tests for concurrency_guard.py."""
from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from concurrency_guard import ConcurrencyGuard
from world_engine import DynamicWorldEngine, WorldEntity


def test_concurrency_guard_intercepts_stale_mutation() -> None:
    engine = DynamicWorldEngine()
    engine.register_entity(WorldEntity(
        entity_id="lease_a",
        entity_type="Lease",
        version=1,
        ttl=10,
        properties={"holder": "none"},
    ))

    guard = ConcurrencyGuard()
    # Agent observed entity at v1
    guard.record_observation("lease_a", version=1, tick=0)

    # In the background, an external worker mutates entity to v2
    engine.mutate_entity("lease_a", {"holder": "external_worker"})
    ent = engine.get_entity("lease_a")
    assert ent.version == 2

    # Under Arm 3 (enforce_guard=True): stale mutation must be intercepted
    is_allowed, err_code, notice = guard.validate_action("lease_a", engine, enforce_guard=True)
    assert is_allowed is False
    assert err_code == "STALE_VERSION_INTERCEPTED"
    assert notice is not None
    assert "DELTA NOTICE" in notice
    assert "was v1, now v2" in notice
    assert guard.stale_violations_intercepted == 1

    # After delta notice is received, guard updated observation to v2
    # Next attempt succeeds
    is_allowed2, err_code2, _ = guard.validate_action("lease_a", engine, enforce_guard=True)
    assert is_allowed2 is True
    assert err_code2 is None


def test_concurrency_guard_bypass_mode() -> None:
    engine = DynamicWorldEngine()
    engine.register_entity(WorldEntity(
        entity_id="lease_b",
        entity_type="Lease",
        version=1,
        ttl=5,
    ))

    guard = ConcurrencyGuard()
    guard.record_observation("lease_b", version=1, tick=0)

    # In the background, an external worker mutates entity to v2
    engine.mutate_entity("lease_b", {"holder": "external_worker"})

    # Under Arm 1/2 (enforce_guard=False): stale overwrite is allowed through
    is_allowed, err_code, _ = guard.validate_action("lease_b", engine, enforce_guard=False)
    assert is_allowed is True
    assert err_code == "STALE_OVERWRITE_PERMITTED"
    assert guard.stale_overwrites_committed == 1
