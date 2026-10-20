"""Legacy Milestone MN-026 Verification under Slot Cache Isolation.

Tests the full multi-domain capstone governance suite (Nuclear Fission, Orbital Life Support,
Smart Microgrid, and Sensor Blackout) under SlotCacheManager isolation mode.
Verifies 100% memory isolation, zero cross-case KV leakage, and complete deterministic resolution.
100% Python Standard Library. Zero external dependencies.
"""

from mong_nhiem.core.semantic_gate import SemanticInvariantGate, SemanticPrecondition
from mong_nhiem.knowledge.abductive_tracer import (
    AbductiveCausalTracer,
    CausalDependency,
)
from mong_nhiem.orchestration.reflex_breaker import RedlineRule, ReflexCircuitBreaker
from mong_nhiem.orchestration.telemetry_observer import (
    BlackoutMode,
    ProxyEstimator,
    TelemetryObserver,
)
from mong_nhiem.runtime.slot_cache import SlotCacheManager, SlotExecutionMode


def test_mn026_cross_scenario_memory_isolation_with_slot_flush():
    """Simulates sequential execution of 4 legacy domains through SlotCacheManager.
    
    Verifies that calling flush_slot between scenarios eliminates any residual state,
    preventing cross-scenario KV leakage.
    """
    slot_mgr = SlotCacheManager(mode=SlotExecutionMode.ISOLATION, total_slots=2)

    # --- Domain 1: Nuclear Fission Cooling ---
    session_1 = "mn026_nuclear_stage1"
    req_1 = slot_mgr.build_request_payload(
        session_id=session_1,
        static_prefix="[DOMAIN: NUCLEAR] Invariant: Temp < 450K. Redline rule active.",
        dynamic_suffix="State: temp=410K, primary_loop=ONLINE",
    )
    assert req_1["cache_prompt"] is False
    assert req_1["id_slot"] == 0

    # Execute Domain 1 logic
    breaker = ReflexCircuitBreaker()
    breaker.register_rule(RedlineRule("temp", 450.0, ">=", "ACTION: TRIP_SCRAM", 320.0))
    tripped_1, action_1 = breaker.check_telemetry({"temp": 455.0})
    assert tripped_1 is True
    assert action_1 == "ACTION: TRIP_SCRAM"

    # End of Domain 1: Flush slot to guarantee isolation
    slot_mgr.flush_slot(0)
    status_1 = slot_mgr.get_slot_status(0)
    assert status_1["assigned_session_id"] is None
    assert status_1["is_cached"] is False

    # --- Domain 2: Orbital Life Support ---
    session_2 = "mn026_orbital_stage2"
    req_2 = slot_mgr.build_request_payload(
        session_id=session_2,
        static_prefix="[DOMAIN: ORBITAL] Invariant: O2 >= 19.5%. Cabin pressure sealed.",
        dynamic_suffix="State: o2=18.2%, scrubber=OFFLINE",
    )
    assert req_2["cache_prompt"] is False
    # Verified: Memory from session_1 does NOT leak into session_2
    assert "NUCLEAR" not in req_2["prompt"]
    assert "ORBITAL" in req_2["prompt"]

    # Execute Domain 2 logic
    tracer = AbductiveCausalTracer()
    dep = CausalDependency(
        source_partition="life_support",
        source_action="VALVE_SEAL",
        target_partition="cabin",
        resulting_symptom="o2_low",
        mitigation_action="START_SCRUBBER",
    )
    tracer.register_dependency(dep)
    res = tracer.trace_symptom("o2_low", "cabin")
    assert res == ("life_support", "VALVE_SEAL", "START_SCRUBBER")

    slot_mgr.flush_slot(req_2["id_slot"])

    # --- Domain 3: Smart Microgrid Confluence ---
    session_3 = "mn026_microgrid_stage3"
    req_3 = slot_mgr.build_request_payload(
        session_id=session_3,
        static_prefix="[DOMAIN: MICROGRID] Invariant: Frequency 50Hz +/- 0.5Hz.",
        dynamic_suffix="State: freq=48.2Hz, solar_infeed=DROPPED",
    )
    assert req_3["cache_prompt"] is False
    assert "ORBITAL" not in req_3["prompt"]

    gate = SemanticInvariantGate()
    gate.register_precondition("ISOLATE_BUS", SemanticPrecondition("tie_breaker", "OPEN", {"CLOSED"}))
    valid_iso, _ = gate.validate_action("ACTION: ISOLATE_BUS", {"tie_breaker": "OPEN"})
    assert valid_iso is True

    slot_mgr.flush_slot(req_3["id_slot"])

    # --- Domain 4: Stage 7 Sensor Blackout Autonomy ---
    session_4 = "mn026_stage7_blackout"
    req_4 = slot_mgr.build_request_payload(
        session_id=session_4,
        static_prefix="[DOMAIN: BLACKOUT] Sensor confidence decay under blackout.",
        dynamic_suffix="State: blackout=TRUE, blind_ticks=4",
    )
    assert req_4["cache_prompt"] is False

    observer = TelemetryObserver(
        mode=BlackoutMode.AUTONOMOUS_IMPROVISE,
        decay_rate_per_tick=0.1,
        max_blind_ticks=3,
        estimators={
            "core_pressure": ProxyEstimator(
                target_metric="core_pressure",
                source_metric="aux_flow",
                estimator_fn=lambda f: 100.0 + (f * 0.1),
            )
        },
    )
    est_p = observer.estimate_metric("core_pressure", {"aux_flow": 13.0})
    assert est_p == 101.3

    observer.start_blackout()
    assert observer.in_blackout is True

    # Advance past TTL (3 ticks) -> forces transition to SUPERVISED_STANDBY
    for _ in range(4):
        _conf, ttl_exceeded = observer.step_blackout_tick()
    assert ttl_exceeded is True
    assert observer.mode == BlackoutMode.SUPERVISED_STANDBY

    slot_mgr.flush_slot(req_4["id_slot"])

    # Final Telemetry Check: Zero cache contamination across all 4 domains
    assert slot_mgr.telemetry["cache_hits"] == 0
    assert slot_mgr.telemetry["isolation_flushes"] == 4
