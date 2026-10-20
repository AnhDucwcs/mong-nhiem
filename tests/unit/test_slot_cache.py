"""Unit Tests for KV-Slot Cache Manager & Memory Isolation."""

from mong_nhiem.runtime.slot_cache import (
    SlotCacheManager,
    SlotExecutionMode,
)


def test_slot_cache_isolation_mode():
    mgr = SlotCacheManager(mode=SlotExecutionMode.ISOLATION, total_slots=2)

    # 1. First turn: Session A
    req1 = mgr.build_request_payload(
        session_id="test_case_001",
        static_prefix="[SYSTEM INSTRUCTION: DO NOT LEAK] ",
        dynamic_suffix="State: tick=1",
    )
    assert req1["cache_prompt"] is False
    assert req1["id_slot"] == 0

    # 2. Second turn: Session A in isolation mode still forces cache_prompt = False
    req2 = mgr.build_request_payload(
        session_id="test_case_001",
        static_prefix="[SYSTEM INSTRUCTION: DO NOT LEAK] ",
        dynamic_suffix="State: tick=2",
    )
    assert req2["cache_prompt"] is False
    assert mgr.telemetry["cache_misses"] == 2
    assert mgr.telemetry["cache_hits"] == 0


def test_slot_cache_affinity_mode_and_token_savings():
    mgr = SlotCacheManager(mode=SlotExecutionMode.AFFINITY, total_slots=2)

    prefix = "[SYSTEM: INVARIANT COGNITIVE KERNEL] " * 5  # ~175 chars ~ 43 tokens

    # Turn 1: Cold prefill
    req1 = mgr.build_request_payload(
        session_id="prod_session_1",
        static_prefix=prefix,
        dynamic_suffix="Reading: 42.0",
    )
    assert req1["cache_prompt"] is True
    assert mgr.telemetry["cache_misses"] == 1
    assert mgr.telemetry["cache_hits"] == 0
    assert mgr.telemetry["tokens_saved"] == 0

    # Turn 2: Cached prefix reuse
    req2 = mgr.build_request_payload(
        session_id="prod_session_1",
        static_prefix=prefix,
        dynamic_suffix="Reading: 43.5",
    )
    assert req2["cache_prompt"] is True
    assert mgr.telemetry["cache_hits"] == 1
    assert mgr.telemetry["tokens_saved"] > 0


def test_slot_cache_lru_eviction_and_flush_isolation():
    mgr = SlotCacheManager(mode=SlotExecutionMode.AFFINITY, total_slots=2)

    # Fill slot 0 and slot 1
    mgr.build_request_payload("session_a", "prefix_a", "suffix_a")
    mgr.build_request_payload("session_b", "prefix_b", "suffix_b")

    status_0 = mgr.get_slot_status(0)
    assert status_0["assigned_session_id"] == "session_a"
    assert status_0["is_cached"] is True

    # Third session forces LRU eviction on slot 0
    slot_id_c = mgr.assign_slot_for_session("session_c")
    assert slot_id_c == 0

    # Slot 0 must have been flushed upon eviction
    status_0_after = mgr.get_slot_status(0)
    assert status_0_after["assigned_session_id"] == "session_c"
    assert mgr.telemetry["isolation_flushes"] >= 1


def test_flush_all_slots_memory_clear():
    mgr = SlotCacheManager(total_slots=3)
    mgr.build_request_payload("s1", "p1", "d1")
    mgr.build_request_payload("s2", "p2", "d2")

    assert len(mgr.session_to_slot) == 2

    # Flush all for test suite boundary
    mgr.flush_all_slots()
    assert len(mgr.session_to_slot) == 0
    for s_id in range(3):
        assert mgr.get_slot_status(s_id)["assigned_session_id"] is None
        assert mgr.get_slot_status(s_id)["is_cached"] is False
