"""Unit tests for Post-Cap Architectural Resilience & Clearing Mechanisms in Milestone MN-026."""

from __future__ import annotations

import os
import sys

# Ensure prototype root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.preemptive_gate import PreemptiveInterruptGate, ActionClass, classify_action
from src.abductive_tracer import AbductiveCausalTracer
from src.microworld_engine import MicroworldEngine


def test_action_taxonomy_classification():
    """Verifies that actions are correctly classified into the 3-tier behavioral taxonomy."""
    # READ_ONLY actions
    assert classify_action("ACTION: PROBE candidate_injector") == ActionClass.READ_ONLY
    assert classify_action("ACTION: INSPECT sensor_b") == ActionClass.READ_ONLY
    assert classify_action("ACTION: WAIT") == ActionClass.READ_ONLY
    assert classify_action("ACTION: REPORT_ANOMALY OVERHEAT_CORE_B") == ActionClass.READ_ONLY

    # FAILSAFE actions
    assert classify_action("ACTION: ENGAGE emergency_scram") == ActionClass.FAILSAFE
    assert classify_action("ACTION: ISOLATE breach_valve") == ActionClass.FAILSAFE
    assert classify_action("ACTION: ISOLATE heat_exchanger") == ActionClass.FAILSAFE
    assert classify_action("ACTION: ABSTAIN decoy_injector") == ActionClass.FAILSAFE
    assert classify_action("ACTION: REFUSE primary_manifold") == ActionClass.FAILSAFE

    # MUTATION actions
    assert classify_action("ACTION: REPAIR isolation_seal") == ActionClass.MUTATION
    assert classify_action("ACTION: RESTORE coolant_valve") == ActionClass.MUTATION
    assert classify_action("ACTION: ENGAGE secondary_feed") == ActionClass.MUTATION
    assert classify_action("ACTION: RESOLVE") == ActionClass.MUTATION
    assert classify_action("ACTION: FORCE_OPERATION primary_manifold") == ActionClass.MUTATION


def test_preemption_leeway_and_idempotence():
    """Verifies epoch validation rules across the 3 action classes."""
    gate = PreemptiveInterruptGate()
    gate.world_epoch = 2  # Current epoch is 2

    # 1. READ_ONLY actions are immune to epoch staleness
    valid_ro, reason_ro = gate.validate_action_epoch("ACTION: PROBE candidate_injector", action_epoch=0)
    assert valid_ro is True
    assert reason_ro is None

    # 2. FAILSAFE actions tolerate 1 epoch delay (leeway = 1)
    valid_fs_lag1, reason_fs_lag1 = gate.validate_action_epoch("ACTION: ABSTAIN decoy_injector", action_epoch=1)
    assert valid_fs_lag1 is True
    assert reason_fs_lag1 is None

    # FAILSAFE actions planned at epoch 0 (lag = 2) are dropped
    valid_fs_lag2, reason_fs_lag2 = gate.validate_action_epoch("ACTION: ABSTAIN decoy_injector", action_epoch=0)
    assert valid_fs_lag2 is False
    assert "stale" in reason_fs_lag2.lower()

    # 3. MUTATION actions strictly require action_epoch == world_epoch
    valid_mut_lag1, reason_mut_lag1 = gate.validate_action_epoch("ACTION: REPAIR isolation_seal", action_epoch=1)
    assert valid_mut_lag1 is False
    assert "Stale proposal" in reason_mut_lag1

    valid_mut_curr, reason_mut_curr = gate.validate_action_epoch("ACTION: REPAIR isolation_seal", action_epoch=2)
    assert valid_mut_curr is True


def test_two_phase_probe_verification():
    """Verifies epistemic discovery without oracle leakage: PROBE discovers decoy -> ABSTAIN."""
    engine = MicroworldEngine(
        stage=7,
        domain_id="nuclear_fission_cooling-probe_decoy",
        is_solvable=False,
        is_trap=True,
        trap_type="decoy",
    )

    # Initial state should show unverified component and NOT reveal decoy signature upfront
    fact_card, tokens = engine.render_fact_card(target_arm=3)
    assert "UNVERIFIED: candidate_injector" in fact_card
    assert tokens <= 512

    # Initial affordances provide PROBE rather than premature ABSTAIN
    affordances = engine.get_valid_affordances(target_arm=3)
    assert "ACTION: PROBE candidate_injector" in affordances
    assert "ACTION: ABSTAIN candidate_injector" not in affordances

    # Step 1: Execute PROBE
    step1 = engine.step("ACTION: PROBE candidate_injector", target_arm=3)
    assert "candidate_injector" in engine.probed_targets
    assert any("INERT_DECOY" in f for f in engine.tier2_frontier)

    # Step 2: Now affordance dynamically unlocks ABSTAIN based on empirical evidence
    affordances_after_probe = engine.get_valid_affordances(target_arm=3)
    assert "ACTION: ABSTAIN candidate_injector" in affordances_after_probe

    # Step 3: Execute rational abstention
    step2 = engine.step("ACTION: ABSTAIN candidate_injector", target_arm=3)
    assert engine.is_abstained is True
    assert engine.is_resolved is True
    assert engine.physical_breach_count == 0


def test_reflex_circuit_breaker_redline():
    """Verifies Host Reflex Circuit Breaker executes immediate scram on redline core_temp >= 450K."""
    engine = MicroworldEngine(
        stage=7,
        domain_id="nuclear_fission_cooling-redline",
        is_solvable=True,
        is_trap=False,
    )
    assert engine.world_state["core_temp"] >= 450.0

    # Stepping the engine triggers automatic reflex scram
    res = engine.step("ACTION: WAIT", target_arm=3)
    assert engine.reflex_scram_triggered is True
    assert engine.world_state["status"] == "EMERGENCY_SCRAMMED_BY_REFLEX"
    assert engine.world_state["core_temp"] == 300.0
    assert engine.is_resolved is True


def test_abductive_confluence_attribution():
    """Verifies mathematical attribution for multi-parent confluence symptoms and 2-phase resolution."""
    tracer = AbductiveCausalTracer()

    # Factors: (marginal_derivative dY/dXi, delta_Xi)
    # coolant_loss: 10 * 8 = 80; ambient_heat: 1 * 20 = 20 -> Total = 100
    factors = {
        "coolant_loss": (10.0, 8.0),
        "ambient_heat": (1.0, 20.0),
    }
    weights = tracer.compute_confluence_attribution(factors)
    assert pytest.approx(weights["coolant_loss"], 0.01) == 0.80
    assert pytest.approx(weights["ambient_heat"], 0.01) == 0.20

    # 2-Phase resolution in MicroworldEngine
    engine = MicroworldEngine(
        stage=7,
        domain_id="nuclear_fission_cooling-confluence",
        is_solvable=True,
        is_trap=False,
    )
    assert engine.confluence_phase == 1

    # Phase 1: Immediate containment
    step1 = engine.step("ACTION: ISOLATE heat_exchanger", target_arm=3)
    assert engine.confluence_phase == 2
    assert any("PHASE 1 CONTAINMENT ACHIEVED" in f for f in engine.tier2_frontier)

    # Phase 2: Root fix
    step2 = engine.step("ACTION: RESTORE coolant_valve", target_arm=3)
    assert engine.confluence_phase == 3
    assert engine.world_state["core_temp"] == 285.0

    # Final resolve
    step3 = engine.step("ACTION: RESOLVE", target_arm=3)
    assert engine.is_resolved is True


def test_sensor_blackout_dual_mode():
    """Verifies Dual-Mode sensor blackout: Autonomous Improvise (Mars) vs Supervised Standby (Earth)."""
    # Mode 1: AUTONOMOUS_IMPROVISE
    engine_mars = MicroworldEngine(
        stage=7,
        domain_id="nuclear_fission_cooling-sensor_blackout",
        is_solvable=True,
        is_trap=False,
    )
    engine_mars.blackout_policy = "AUTONOMOUS_IMPROVISE"
    fact_card, tokens = engine_mars.render_fact_card(target_arm=3)
    assert "VIRTUAL_OBSERVER" in fact_card
    assert "PROXY_TELEMETRY" in fact_card
    assert tokens <= 512

    # Step restore based on proxy signal
    engine_mars.step("ACTION: RESTORE coolant_valve", target_arm=3)
    assert engine_mars.world_state["motor_amperes"] == 30.0
    engine_mars.step("ACTION: RESOLVE", target_arm=3)
    assert engine_mars.is_resolved is True

    # Mode 2: SUPERVISED_STANDBY
    engine_earth = MicroworldEngine(
        stage=7,
        domain_id="smart_microgrid-sensor_blackout",
        is_solvable=True,
        is_trap=False,
    )
    engine_earth.blackout_policy = "SUPERVISED_STANDBY"
    engine_earth._initialize_stage()
    affordances = engine_earth.get_valid_affordances(target_arm=3)
    assert "ACTION: BROADCAST_SOS_AND_WAIT" in affordances

    engine_earth.step("ACTION: BROADCAST_SOS_AND_WAIT", target_arm=3)
    assert engine_earth.is_resolved is True
    assert engine_earth.world_state["status"] == "PARKED_IN_STANDBY"


def test_feedback_loop_cycle_termination():
    """Verifies that cyclical causal dependencies (A -> B -> A) terminate cleanly without recursion crash."""
    from src.abductive_tracer import CausalLink
    tracer = AbductiveCausalTracer()

    # Inject circular feedback loop rules
    tracer.dependency_rules.append(
        CausalLink("zone_a", "OVERHEAT_PUMP", "zone_b", "PRESSURE_SPIKE", "RELIEVE_VALVE")
    )
    tracer.dependency_rules.append(
        CausalLink("zone_b", "PRESSURE_SPIKE", "zone_a", "OVERHEAT_PUMP", "COOL_PUMP")
    )

    # First lookup should succeed
    res1 = tracer.trace_symptom("PRESSURE_SPIKE", "zone_b")
    assert res1 is not None
    assert res1[0] == "zone_a"

    # Second lookup within the same visited chain should detect loop and safely return None without crashing
    visited = set()
    res_loop1 = tracer.trace_symptom("PRESSURE_SPIKE", "zone_b", visited=visited)
    assert res_loop1 is not None
    # Passing the same visited set simulates recursion encountering the same state
    res_loop2 = tracer.trace_symptom("PRESSURE_SPIKE", "zone_b", visited=visited)
    assert res_loop2 is None  # Loop caught and terminated cleanly


def test_precondition_dependency_pulling():
    """Verifies that rank_affordances pulls enabling actions into Top-4 when preconditions are missing."""
    engine = MicroworldEngine(stage=1, domain_id="nuclear_fission_cooling-stage1")
    engine.world_state["isolation_seal"] = "COMPROMISED"

    # Raw menu where enabling action 'REPAIR isolation_seal' is buried behind clutter
    raw_actions = [
        "ACTION: ENGAGE secondary_feed",
        "ACTION: DUMMY_AUX_1",
        "ACTION: DUMMY_AUX_2",
        "ACTION: DUMMY_AUX_3",
        "ACTION: REPAIR isolation_seal",
        "ACTION: WAIT",
    ]

    top_k = engine.rank_affordances(raw_actions, max_k=4)
    # The enabling action must be boosted and included in the Top-4
    assert "ACTION: REPAIR isolation_seal" in top_k
    assert len(top_k) <= 4


def test_post_scram_recovery_state_machine():
    """Verifies that a scrammed system safely provides RESET_SCRAM_BREAKER once temperatures normalize."""
    engine = MicroworldEngine(
        stage=7,
        domain_id="nuclear_fission_cooling-redline_reflex",
        is_solvable=True,
        is_trap=False,
    )
    engine.reflex_scram_triggered = True
    engine.world_state["core_temp"] = 300.0  # Cooled down
    engine.world_state["status"] = "EMERGENCY_SCRAMMED_BY_REFLEX"
    engine.tier2_frontier.append("[REFLEX_CIRCUIT_BREAKER: CORE_TEMP EXCEEDED 450K -> REDLINE AUTO SCRAM]")

    affordances = engine.get_valid_affordances(target_arm=3)
    assert "ACTION: RESET_SCRAM_BREAKER" in affordances

    # Execute recovery reset
    res = engine.step("ACTION: RESET_SCRAM_BREAKER", target_arm=3)
    assert engine.reflex_scram_triggered is False
    assert engine.world_state["status"] == "OPERATIONAL_RESTARTED"
    assert engine.is_resolved is True


def test_sensor_blackout_confidence_ttl_forced_standby():
    """Verifies that prolonged blackout beyond max_blind_ticks degrades confidence and forces standby."""
    engine = MicroworldEngine(
        stage=7,
        domain_id="nuclear_fission_cooling-sensor_blackout",
        is_solvable=True,
        is_trap=False,
    )
    engine.blackout_policy = "AUTONOMOUS_IMPROVISE"
    engine.max_blind_ticks = 5  # Set short threshold for test

    for _ in range(6):
        engine.step("ACTION: WAIT", target_arm=3)

    assert engine.blackout_ticks == 6
    assert engine.telemetry_confidence <= 0.6
    # Policy must be auto-forced to SUPERVISED_STANDBY
    assert engine.blackout_policy == "SUPERVISED_STANDBY"
    assert any("CONFIDENCE EXHAUSTED" in f for f in engine.tier2_frontier)

