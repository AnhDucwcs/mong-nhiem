"""Unit tests for VectorClock and causal precedence."""

from mong_nhiem.core.events import CausalEvent
from mong_nhiem.core.vector_clock import VectorClock


def test_vector_clock_increment_and_merge():
    vc1 = VectorClock()
    vc1.increment("agent_1")
    vc1.increment("agent_1")
    vc1.increment("agent_2")

    assert vc1.get("agent_1") == 2
    assert vc1.get("agent_2") == 1
    assert vc1.get("agent_3") == 0

    vc2 = VectorClock({"agent_1": 1, "agent_3": 4})
    merged = vc1.merge(vc2)

    assert merged.get("agent_1") == 2
    assert merged.get("agent_2") == 1
    assert merged.get("agent_3") == 4


def test_vector_clock_causality_and_concurrency():
    vc_a = VectorClock({"a": 1, "b": 1})
    vc_b = VectorClock({"a": 2, "b": 1})
    vc_c = VectorClock({"a": 1, "b": 2})

    # vc_a happened before vc_b
    assert vc_a.is_causally_dependent(vc_b) is True
    assert vc_a.is_strictly_less(vc_b) is True
    assert vc_b.is_causally_dependent(vc_a) is False

    # vc_b and vc_c are concurrent
    assert vc_b.is_concurrent(vc_c) is True
    assert vc_c.is_concurrent(vc_b) is True


def test_causal_event_hashing_and_integrity():
    evt = CausalEvent(
        event_id="evt_001",
        tick=5,
        agent_id="agent_1",
        action_type="ACT",
        target="substation_1",
        payload={"power": 25},
        parent_hashes=["hash_root"],
    )

    assert evt.verify_integrity() is True
    # Mutating payload breaks integrity check
    evt.payload["power"] = 99
    assert evt.verify_integrity() is False
