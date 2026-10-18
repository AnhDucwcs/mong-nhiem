"""Unit tests for production cognitive capstone modules promoted in MN-026.

Verifies domain-agnostic behavior, 6 safety checkpoints, and 7 failure family guards:
- SemanticInvariantGate (core.semantic_gate)
- ReflexCircuitBreaker with Hysteresis (orchestration.reflex_breaker)
- AbductiveCausalTracer with Cycle Termination & Confluence (knowledge.abductive_tracer)
- GoalConditionedAffordanceRanker with Dependency Pulling (orchestration.affordance_ranker)
- PreemptiveInterruptGate with 3-Class Taxonomy (orchestration.preemption_gate)
- VirtualJitterArbiter (orchestration.jitter_arbiter)
- TelemetryObserver with Confidence Decay TTL (orchestration.telemetry_observer)
100% Python Standard Library. Zero external dependencies.
"""

import pytest

from mong_nhiem.core.semantic_gate import SemanticInvariantGate, SemanticPrecondition
from mong_nhiem.knowledge.abductive_tracer import AbductiveCausalTracer, CausalDependency
from mong_nhiem.orchestration.affordance_ranker import GoalConditionedAffordanceRanker
from mong_nhiem.orchestration.jitter_arbiter import VirtualJitterArbiter, VirtualRoleProfile
from mong_nhiem.orchestration.preemption_gate import (
    ActionClass,
    PreemptiveInterruptGate,
    default_action_classifier,
)
from mong_nhiem.orchestration.reflex_breaker import RedlineRule, ReflexCircuitBreaker, ReflexState
from mong_nhiem.orchestration.telemetry_observer import BlackoutMode, ProxyEstimator, TelemetryObserver


# ==============================================================================
# 1. Semantic Invariant Gate Tests
# ==============================================================================

def test_semantic_gate_precondition_validation():
    gate = SemanticInvariantGate()
    gate.register_precondition(
        "ENGAGE feeder",
        SemanticPrecondition(
            required_entity="isolation_barrier",
            required_state="CLOSED",
            incompatible_states={"BREACHED", "OPEN"},
        ),
    )

    # World state where precondition is met
    valid, reason = gate.validate_action("ACTION: ENGAGE feeder", {"isolation_barrier": "CLOSED"})
    assert valid is True
    assert reason is None

    # World state where precondition is unmet
    valid, reason = gate.validate_action("ENGAGE feeder", {"isolation_barrier": "PENDING"})
    assert valid is False
    assert "PRECONDITION_UNMET" in reason

    # World state with incompatible state
    valid, reason = gate.validate_action("ENGAGE feeder", {"isolation_barrier": "BREACHED"})
    assert valid is False
    assert "INCOMPATIBLE_STATE_BREACH" in reason
    assert gate.semantic_breach_count == 2


# ==============================================================================
# 2. Reflex Circuit Breaker with Hysteresis Tests
# ==============================================================================

def test_reflex_breaker_hysteresis_and_scram():
    breaker = ReflexCircuitBreaker([
        RedlineRule(
            metric_key="temp",
            threshold=450.0,
            comparison=">=",
            failsafe_action="ENGAGE emergency_scram",
            reset_threshold=320.0,
            reset_action="RESET_SCRAM_BREAKER",
        )
    ])

    # Normal telemetry
    tripped, action = breaker.check_telemetry({"temp": 380.0}, current_tick=1)
    assert not tripped
    assert breaker.state == ReflexState.NORMAL

    # Redline excursion
    tripped, action = breaker.check_telemetry({"temp": 465.0}, current_tick=2)
    assert tripped
    assert action == "ENGAGE emergency_scram"
    assert breaker.state == ReflexState.TRIPPED

    # Attempt reset while temperature is still above reset_threshold (320.0) -> MUST FAIL (Hysteresis)
    reset_ok, msg = breaker.attempt_reset("ACTION: RESET_SCRAM_BREAKER", {"temp": 390.0})
    assert not reset_ok
    assert "HYSTERESIS_INTERLOCK" in msg
    assert breaker.state == ReflexState.TRIPPED

    # Attempt reset with wrong action -> MUST FAIL
    reset_ok, msg = breaker.attempt_reset("ACTION: NORMAL_OPERATION", {"temp": 300.0})
    assert not reset_ok
    assert "RESET_FAILED" in msg

    # Reset with correct action and safe temperature (<= 320.0) -> SUCCEEDS
    reset_ok, msg = breaker.attempt_reset("ACTION: RESET_SCRAM_BREAKER", {"temp": 310.0})
    assert reset_ok
    assert breaker.state == ReflexState.RECOVERED


# ==============================================================================
# 3. Abductive Causal Tracer with Confluence & Cycle Termination Tests
# ==============================================================================

def test_abductive_tracer_cycle_termination_and_confluence():
    tracer = AbductiveCausalTracer([
        CausalDependency(
            source_partition="alpha",
            source_action="DIVERT flow",
            target_partition="beta",
            resulting_symptom="OVERHEAT",
            mitigation_action="RESTORE valve",
        ),
        # Circular coupling: beta back to alpha
        CausalDependency(
            source_partition="beta",
            source_action="RESTORE valve",
            target_partition="alpha",
            resulting_symptom="PRESSURE_SPIKE",
            mitigation_action="VENT damper",
        ),
    ])

    tracer.record_action("alpha", "DIVERT flow", tick=1)
    res = tracer.trace_symptom("OVERHEAT", "beta")
    assert res == ("alpha", "DIVERT flow", "RESTORE valve")

    # Verify cycle termination: visited set prevents recursion loop
    visited = set()
    res1 = tracer.trace_symptom("OVERHEAT", "beta", visited=visited)
    assert res1 is not None
    # Repeating same state key in visited returns None cleanly
    res2 = tracer.trace_symptom("OVERHEAT", "beta", visited=visited)
    assert res2 is None

    # Confluence attribution: dY/dXi * delta_Xi
    factors = {
        "coolant_loss": (2.0, 40.0),    # |2.0 * 40| = 80.0
        "ambient_load": (0.5, 40.0),    # |0.5 * 40| = 20.0
    }
    weights = tracer.compute_confluence_attribution(factors)
    assert weights["coolant_loss"] == 0.8
    assert weights["ambient_load"] == 0.2

    hints = tracer.render_confluence_hint("coolant_loss", "ambient_load", "ISOLATE ambient", "RESTORE coolant")
    assert len(hints) == 3
    assert "PHASE 1 - CONTAINMENT" in hints[1]
    assert "PHASE 2 - ROOT_FIX" in hints[2]


# ==============================================================================
# 4. Goal-Conditioned Affordance Ranker Tests
# ==============================================================================

def test_affordance_ranker_bounding_and_dependency_pulling():
    ranker = GoalConditionedAffordanceRanker(top_k=4, dependency_boost=25.0)

    candidates = [
        "ACTION: WAIT",
        "ACTION: ENGAGE primary_feed",
        "ACTION: REPAIR isolation_barrier",
        "ACTION: FLUSH line",
        "ACTION: ACTIVATE decoy_valve",
        "ACTION: PURGE tank",
    ]

    # Precondition for ENGAGE primary_feed is unmet: requires isolation_barrier repair
    unmet = {"isolation_barrier_ready"}
    enabling_map = {
        "REPAIR isolation_barrier": "isolation_barrier_ready",
    }
    confirmed_decoys = {"decoy_valve"}

    ranked = ranker.rank_affordances(
        candidates=candidates,
        unfulfilled_preconditions=unmet,
        enabling_map=enabling_map,
        confirmed_decoys=confirmed_decoys,
    )

    # 1. Output length strictly bounded by top_k
    assert len(ranked) <= 4

    # 2. Dependency pulling: REPAIR isolation_barrier gets +25 boost and ranks 1st
    assert ranked[0] == "ACTION: REPAIR isolation_barrier"

    # 3. Decoy masking: ACTIVATE decoy_valve is demoted and excluded from Top-4
    assert "ACTION: ACTIVATE decoy_valve" not in ranked


# ==============================================================================
# 5. Preemptive Interrupt Gate Tests
# ==============================================================================

def test_preemptive_interrupt_gate_3class_taxonomy():
    gate = PreemptiveInterruptGate(max_failsafe_lag=1)

    # Verify classification
    assert default_action_classifier("PROBE component") == ActionClass.READ_ONLY
    assert default_action_classifier("ENGAGE emergency_scram") == ActionClass.FAILSAFE
    assert default_action_classifier("ACTIVATE main_feed") == ActionClass.MUTATION

    # Nominal epoch 1: mutation at epoch 1 valid
    valid, _ = gate.validate_action_epoch("ACTIVATE main_feed", action_epoch=1)
    assert valid is True

    # Mid-trajectory shock occurs at t+1: epoch advances to 2
    shock = gate.trigger_shock(
        shock_id="SHOCK_PIPE_BURST",
        target_entity="pipe_alpha",
        shock_type="RUPTURE",
        trigger_tick=5,
        required_mitigation="ISOLATE pipe_alpha",
    )
    assert gate.world_epoch == 2
    assert gate.emergency_active is True

    # Stale mutation planned for epoch 1 -> MUST BE DROPPED
    valid, reason = gate.validate_action_epoch("ACTIVATE main_feed", action_epoch=1)
    assert valid is False
    assert "PREEMPTED_STALE_ACTION" in reason
    assert gate.preempted_stale_count == 1

    # Read-only action planned at epoch 1 -> EPOCH IMMUNE (PERMITTED)
    valid, _ = gate.validate_action_epoch("PROBE pipe_alpha", action_epoch=1)
    assert valid is True

    # Failsafe mitigation action with lag <= 1 -> EPOCH TOLERANT (PERMITTED)
    valid, _ = gate.validate_action_epoch("ISOLATE pipe_alpha", action_epoch=1)
    assert valid is True

    # Resolving shock returns gate to nominal
    resolved = gate.resolve_shock("ISOLATE pipe_alpha")
    assert resolved is True
    assert gate.emergency_active is False


# ==============================================================================
# 6. Virtual Jitter Arbiter Tests
# ==============================================================================

def test_virtual_jitter_arbiter_leases_and_latency():
    arbiter = VirtualJitterArbiter(
        roles={
            "scout": VirtualRoleProfile(
                role_name="scout",
                base_latency_ms=100.0,
                jitter_range_ms=(80.0, 150.0),
            )
        },
        default_ttl=3,
    )

    # Virtual latency computation is deterministic for same seed
    lat1 = arbiter.compute_turn_latency("scout", seed=10)
    lat2 = arbiter.compute_turn_latency("scout", seed=10)
    assert lat1 == lat2
    assert 80.0 <= lat1 <= 150.0

    # Agent A acquires lease at tick 0
    ok = arbiter.acquire_lease("valve_1", agent_id="agent_a", current_tick=0, ttl=3)
    assert ok is True
    assert arbiter.is_locked("valve_1", current_tick=1)

    # Agent B attempts acquire before TTL expiration (tick 1 < 3) -> MUST FAIL (collision)
    ok_b = arbiter.acquire_lease("valve_1", agent_id="agent_b", current_tick=1)
    assert ok_b is False
    assert arbiter.collision_count == 1

    # At tick 4, lease has expired -> Agent B can steal/acquire
    ok_b_expired = arbiter.acquire_lease("valve_1", agent_id="agent_b", current_tick=4)
    assert ok_b_expired is True
    assert arbiter.active_leases["valve_1"].holder == "agent_b"


# ==============================================================================
# 7. Telemetry Observer Tests
# ==============================================================================

def test_telemetry_observer_blackout_and_confidence_ttl():
    observer = TelemetryObserver(
        mode=BlackoutMode.AUTONOMOUS_IMPROVISE,
        decay_rate_per_tick=0.1,
        max_blind_ticks=5,
        estimators={
            "temp": ProxyEstimator(
                target_metric="temp",
                source_metric="current_amps",
                estimator_fn=lambda amps: 300.0 + (amps * 2.5),
            )
        },
    )

    # Proxy estimation
    est_temp = observer.estimate_metric("temp", {"current_amps": 40.0})
    assert est_temp == 400.0

    # Start blackout
    observer.start_blackout()
    assert observer.in_blackout is True

    # Advance 3 ticks: confidence decays from 1.0 -> 0.7
    for _ in range(3):
        conf, ttl_exceeded = observer.step_blackout_tick()
    assert conf == 0.7
    assert not ttl_exceeded
    assert observer.mode == BlackoutMode.AUTONOMOUS_IMPROVISE

    # Advance past max_blind_ticks (5 ticks) -> TTL trips to SUPERVISED_STANDBY
    for _ in range(3):
        conf, ttl_exceeded = observer.step_blackout_tick()
    assert ttl_exceeded is True
    assert observer.mode == BlackoutMode.SUPERVISED_STANDBY
