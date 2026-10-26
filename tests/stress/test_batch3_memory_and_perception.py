"""Batch 3 Adversarial Stress Tests: Memory, Perception & Natural Language Distillation.

Adversarial Stress Test Battery for Milestone MN-029:
- Test 3: Byzantine Sensor & Equifinality Trap (Mandatory diagnostic PROBE forcing)
- Test 5: Sub-Threshold Slow-Burn Poisoning (Cumulative telemetry drift retention across 100 ticks)
- Test 4: Chaotic Human Operator Stress Test (Reasoning-First Dynamic Enum GBNF distillation)
"""

from __future__ import annotations

import pytest

from mong_nhiem.extensions.autodream.fact_cards import FactCard


# ============================================================================
# TEST 3: Byzantine Sensor & Equifinality Trap
# ============================================================================

def test_byzantine_sensor_equifinality_trap_baseline() -> None:
    """Test 3: Conflicting root causes with stuck-at sensor must mandate ACTION: PROBE."""
    try:
        from mong_nhiem.knowledge.diagnostic_probe import DiagnosticProbeEnforcer
    except ImportError:
        # BASELINE EMPIRICAL EVIDENCE: Abductive tracer returns multiple hypotheses without forcing PROBE
        pytest.xfail("BASELINE VULNERABILITY: DiagnosticProbeEnforcer not yet implemented in v0.2.0")

    enforcer = DiagnosticProbeEnforcer()

    # Define equifinality: Pressure drop caused by either Leak or Pump_Stall
    candidate_hypotheses = ["Pipe_Leak", "Pump_Stall"]

    # Telemetry history: Sensor 1 shows drop (40.0), Sensor 2 is stuck-at 50.0 (variance = 0 across 10 ticks)
    sensor_history = {
        "sensor_primary": [50.0, 48.0, 45.0, 42.0, 40.0],
        "sensor_secondary_stuck": [50.0, 50.0, 50.0, 50.0, 50.0],
    }

    # Under equifinality and unvalidated stuck sensor: mutating actions must be blocked
    decision = enforcer.evaluate_diagnostic_affordance(
        symptom="pressure_drop",
        candidates=candidate_hypotheses,
        telemetry_history=sensor_history,
    )

    assert decision.must_probe is True, "Must enforce diagnostic probing before taking corrective action"
    assert decision.recommended_action == "ACTION: PROBE sensor_secondary_stuck"
    assert "ACTION: INCREASE_PUMP" in decision.blocked_actions
    assert "ACTION: DECREASE_PUMP" in decision.blocked_actions


# ============================================================================
# TEST 5: Sub-Threshold Slow-Burn Poisoning
# ============================================================================

def test_sub_threshold_slow_burn_poisoning_baseline() -> None:
    """Test 5: Subtle 0.2% micro-tremors over 100 ticks must be accumulated and retained."""
    try:
        from mong_nhiem.extensions.autodream.cumulative_tracker import CumulativeTelemetryTracker
    except ImportError:
        # BASELINE EMPIRICAL EVIDENCE: Standard AutoDream heuristic compaction prunes sub-threshold drifts
        pytest.xfail("BASELINE VULNERABILITY: CumulativeTelemetryTracker not implemented in v0.2.0")

    tracker = CumulativeTelemetryTracker(window_size=100, anomaly_threshold=0.50)

    # Simulate 100 ticks:
    # At tick 5, 25, 45, 65, inject +0.2% vibration
    # Between those ticks, inject 96 nominal/noisy events
    for tick in range(1, 101):
        if tick in (5, 25, 45, 65):
            tracker.record_sample(metric="vibration_amplitude", value=0.20, tick=tick)
        else:
            tracker.record_sample(metric="vibration_amplitude", value=0.00, tick=tick)

    # Total accumulated vibration = 0.80% (crosses 0.50% threshold)
    card: FactCard | None = tracker.synthesize_cumulative_fact_card("vibration_amplitude")
    assert card is not None, "Cumulative fact card must be synthesized when rolling sum crosses threshold"
    assert card.entity == "vibration_amplitude"
    assert card.value >= 0.80
    assert card.priority == "CRITICAL_PERSISTENT", "Must be marked non-evictable by compaction"


# ============================================================================
# TEST 4: Chaotic Human Operator Stress Test
# ============================================================================

def test_chaotic_human_operator_distillation_baseline() -> None:
    """Test 4: GBNF Reasoning-First Dynamic Enum distillation of messy self-negating operator speech."""
    try:
        from mong_nhiem.schema.grammars.dynamic_operator_intent import (
            OperatorIntentDistiller,
            build_operator_intent_gbnf,
        )
    except ImportError:
        # BASELINE EMPIRICAL EVIDENCE: Dynamic Enum GBNF intent distiller not implemented in v0.2.0
        pytest.xfail("BASELINE VULNERABILITY: OperatorIntentDistiller not yet implemented in v0.2.0")

    valid_entities = ["valve_1", "valve_2", "aux_valve"]
    gbnf_grammar = build_operator_intent_gbnf(valid_entities)

    # 1. Grammar validation
    assert 'entity ::= "valve_1" | "valve_2" | "aux_valve"' in gbnf_grammar
    assert "[^\\n]{1,120}" in gbnf_grammar

    distiller = OperatorIntentDistiller(valid_entities=valid_entities)

    # Sample 1: Self-negation mid-sentence
    speech_1 = "Mở ngay cái van xả số 2 cho tôi... à khoan đừng mở số 2, đóng nó lại rồi mở cái van phụ bên cạnh ấy!"
    # Must correctly resolve to OPEN aux_valve, NOT OPEN valve_2
    action_1 = distiller.distill_intent(speech_1)
    assert action_1.verb == "OPEN"
    assert action_1.entity == "aux_valve"

    # Sample 2: Double negation & colloquial slang
    speech_2 = "Đừng có mà không ngắt nguồn lò số 1 nhé, để nó chạy tiếp là toang đấy!"
    # "Đừng không ngắt" -> "Ngắt" -> STOP valve_1 / reactor_1
    action_2 = distiller.distill_intent(speech_2)
    assert action_2.verb in ("STOP", "CLOSE")

    # Sample 3: Abbreviated / ASR phonetic glitch
    speech_3 = "ngat dien khu b ngay k thi no bay gio"
    action_3 = distiller.distill_intent(speech_3)
    assert action_3.verb in ("STOP", "CLOSE")
