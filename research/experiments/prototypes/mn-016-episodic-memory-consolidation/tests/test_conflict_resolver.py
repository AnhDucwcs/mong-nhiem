"""Unit tests for Deterministic Conflict Resolver."""

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from conflict_resolver import DeterministicConflictResolver, EntityState
from provenance import EpisodicEvent


def test_conflict_resolver_monotonic_state_update() -> None:
    events = [
        EpisodicEvent(
            event_id="e1",
            tick=1,
            entity_id="vault_alpha",
            action_name="init",
            success=True,
            state_delta={"balance": 500, "status": "ACTIVE"},
        ),
        EpisodicEvent(
            event_id="e2",
            tick=5,
            entity_id="vault_alpha",
            action_name="withdraw",
            success=True,
            state_delta={"balance": 200},
        ),
        EpisodicEvent(
            event_id="e3",
            tick=12,
            entity_id="vault_alpha",
            action_name="close",
            success=True,
            state_delta={"balance": 0, "status": "CLOSED"},
        ),
    ]

    states = DeterministicConflictResolver.resolve(events)
    assert len(states) == 1
    alpha = states["vault_alpha"]
    assert alpha.status == "CLOSED"
    assert alpha.attributes["balance"] == 0
    assert alpha.last_updated_tick == 12
    assert alpha.causal_event_id == "e3"


def test_conflict_resolver_purges_contradictions() -> None:
    # Event order shuffled in input, but resolved monotonically
    events = [
        EpisodicEvent(
            event_id="e2",
            tick=10,
            entity_id="svc_auth",
            action_name="terminate",
            success=True,
            state_delta={"status": "TERMINATED", "host": "none"},
        ),
        EpisodicEvent(
            event_id="e1",
            tick=2,
            entity_id="svc_auth",
            action_name="start",
            success=True,
            state_delta={"status": "RUNNING", "host": "srv_1"},
        ),
    ]

    states = DeterministicConflictResolver.resolve(events)
    svc = states["svc_auth"]
    # Final state reflects tick 10, completely purging "RUNNING" and "srv_1"
    assert svc.status == "TERMINATED"
    assert svc.attributes["host"] == "none"
    assert svc.last_updated_tick == 10

    # Test Card Formatting
    card = svc.format_card()
    assert "ENTITY: svc_auth" in card
    assert "STATUS: TERMINATED" in card
    assert "ATTRS: host=none" in card
    assert "AT_TICK: 10" in card
    assert len(card.split()) < 48  # Within token budget
