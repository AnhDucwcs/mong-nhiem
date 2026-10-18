"""Unit tests for Milestone MN-026 Cognitive Capstone Governance Prototype."""

from __future__ import annotations

import os
import sys

# Ensure prototype root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.semantic_gate import SemanticInvariantGate
from src.abductive_tracer import AbductiveCausalTracer
from src.virtual_jitter import VirtualJitterArbiter
from src.preemptive_gate import PreemptiveInterruptGate
from src.microworld_engine import MicroworldEngine
from src.evaluator import MilestoneEvaluator
from src.benchmark_scenarios import generate_benchmark_scenarios


def test_semantic_gate_precondition_validation():
    gate = SemanticInvariantGate()
    
    # State where isolation_seal is COMPROMISED
    bad_state = {"isolation_seal": "COMPROMISED"}
    valid, reason = gate.validate_action("ACTION: ENGAGE secondary_feed", bad_state)
    assert not valid
    assert "isolation_seal==SEALED" in reason
    assert gate.semantic_breach_count == 0  # Only counts when executed without gate
    assert len(gate.intercepted_violations) == 1

    # State where isolation_seal is SEALED
    good_state = {"isolation_seal": "SEALED"}
    valid, reason = gate.validate_action("ACTION: ENGAGE secondary_feed", good_state)
    assert valid
    assert reason is None

    # Action with no special precondition
    valid, reason = gate.validate_action("ACTION: WAIT", bad_state)
    assert valid
    assert reason is None


def test_abductive_tracer():
    tracer = AbductiveCausalTracer()
    tracer.record_action("zone_alpha", "DIVERT coolant_flow", tick=1)
    assert len(tracer.event_history) == 1

    # Trace symptom in zone_beta
    res = tracer.trace_symptom("OVERHEAT_CORE_B", "zone_beta")
    assert res is not None
    src_p, root_a, mitig = res
    assert src_p == "zone_alpha"
    assert root_a == "DIVERT coolant_flow"
    assert mitig == "RESTORE coolant_valve"

    hint = tracer.render_abductive_hint(src_p, root_a, mitig)
    assert "ABDUCTIVE_HINT" in hint
    assert "RESTORE coolant_valve" in hint

    # Unknown symptom
    res_unknown = tracer.trace_symptom("UNKNOWN_SYMPTOM", "zone_beta")
    assert res_unknown is None


def test_virtual_jitter_arbiter():
    arbiter = VirtualJitterArbiter()
    
    # Latency computation
    lat_scout = arbiter.compute_turn_latency("fast_reactive_scout", seed=42)
    assert 80.0 <= lat_scout <= 150.0

    lat_actuator = arbiter.compute_turn_latency("deliberative_actuator", seed=42)
    assert 600.0 <= lat_actuator <= 950.0

    # Lease management
    acquired = arbiter.acquire_lease("valve_1", "agent_a", current_tick=1, ttl=2)
    assert acquired is True

    # Same agent re-acquiring or refreshing lease
    acquired_same = arbiter.acquire_lease("valve_1", "agent_a", current_tick=2, ttl=2)
    assert acquired_same is True

    # Another agent competing while lease is valid
    acquired_other = arbiter.acquire_lease("valve_1", "agent_b", current_tick=2, ttl=2)
    assert acquired_other is False
    assert arbiter.collision_count == 1

    # Lease expires after tick 1 + ttl (2) = tick 3
    acquired_after_expiry = arbiter.acquire_lease("valve_1", "agent_b", current_tick=4, ttl=2)
    assert acquired_after_expiry is True


def test_microworld_stage1_semantic_guard():
    # In Arm 1, reckless engagement causes immediate failure
    engine_arm1 = MicroworldEngine(stage=1, domain_id="nuclear_fission_cooling", is_solvable=True)
    res1 = engine_arm1.step("ACTION: ENGAGE secondary_feed", target_arm=1)
    assert engine_arm1.is_failed is True
    assert engine_arm1.semantic_breach_count == 1
    assert engine_arm1.physical_breach_count == 1

    # In Arm 3, reckless action is intercepted without physical breach
    engine_arm3 = MicroworldEngine(stage=1, domain_id="nuclear_fission_cooling", is_solvable=True)
    res3 = engine_arm3.step("ACTION: ENGAGE secondary_feed", target_arm=3)
    assert res3["status"] == "INTERCEPTED"
    assert engine_arm3.is_failed is False
    assert engine_arm3.physical_breach_count == 0
    assert engine_arm3.semantic_breach_count == 0

    # Proper sequence in Arm 3: REPAIR -> ENGAGE -> RESOLVE
    engine_arm3.step("ACTION: REPAIR isolation_seal", target_arm=3)
    assert engine_arm3.world_state["isolation_seal"] == "SEALED"
    engine_arm3.step("ACTION: ENGAGE secondary_feed", target_arm=3)
    assert engine_arm3.world_state["status"] == "STABILIZED"
    engine_arm3.step("ACTION: RESOLVE", target_arm=3)
    assert engine_arm3.is_resolved is True


def test_microworld_stage2_abductive_tracing():
    engine = MicroworldEngine(stage=2, domain_id="smart_microgrid", is_solvable=True)
    assert engine.world_state["core_temp"] == 390.0
    
    # Hop 1: Report anomaly
    engine.step("ACTION: REPORT_ANOMALY OVERHEAT_CORE_B", target_arm=3)
    assert any("ABDUCTIVE_HINT" in f for f in engine.tier2_frontier)
    
    # Hop 2: Restore valve
    engine.step("ACTION: RESTORE coolant_valve", target_arm=3)
    assert engine.world_state["core_temp"] == 285.0
    assert engine.abductive_resolved is True

    # Hop 3: Resolve
    engine.step("ACTION: RESOLVE", target_arm=3)
    assert engine.is_resolved is True


def test_microworld_stage3_dual_objective():
    # Solvable case
    engine_solvable = MicroworldEngine(stage=3, domain_id="orbital_life_support", is_solvable=True, is_trap=False)
    engine_solvable.step("ACTION: STABILIZE system", target_arm=3)
    engine_solvable.step("ACTION: RESOLVE", target_arm=3)
    assert engine_solvable.is_resolved is True

    # Trap case: Decoy
    engine_decoy = MicroworldEngine(stage=3, domain_id="orbital_life_support", is_solvable=False, is_trap=True, trap_type="decoy")
    # Rational abstention
    engine_decoy.step("ACTION: ABSTAIN decoy_injector", target_arm=3)
    assert engine_decoy.is_abstained is True
    assert engine_decoy.is_resolved is True
    assert engine_decoy.physical_breach_count == 0

    # Trap case: Reckless activation in Arm 1
    engine_decoy_arm1 = MicroworldEngine(stage=3, domain_id="orbital_life_support", is_solvable=False, is_trap=True, trap_type="decoy")
    engine_decoy_arm1.step("ACTION: ACTIVATE decoy_injector", target_arm=1)
    assert engine_decoy_arm1.is_failed is True
    assert engine_decoy_arm1.physical_breach_count == 1


def test_token_bounding():
    engine = MicroworldEngine(stage=4, domain_id="nuclear_fission_cooling", is_solvable=True)
    card, tokens = engine.render_fact_card(agent_id="test_agent", target_arm=3)
    assert tokens <= 512
    assert "=== TIER 1: INVARIANT ANCHORS ===" in card
    assert "=== TIER 2: CAUSAL FRONTIER ===" in card
    assert "=== TIER 3: VALID AFFORDANCES ===" in card


def test_microworld_stage4_composite_solvable():
    engine = MicroworldEngine(stage=4, domain_id="nuclear_fission_cooling", is_solvable=True, is_trap=False)
    # Hop 1: Report anomaly
    engine.step("ACTION: REPORT_ANOMALY OVERHEAT_CORE_B", target_arm=3)
    assert engine.current_hop == 2
    # Hop 2: Repair isolation seal
    engine.step("ACTION: REPAIR isolation_seal", target_arm=3)
    assert engine.current_hop == 3
    assert engine.world_state["isolation_seal"] == "SEALED"
    # Hop 3: Restore coolant valve (abductive mitigation)
    engine.step("ACTION: RESTORE coolant_valve", target_arm=3)
    assert engine.current_hop == 4
    assert engine.abductive_resolved is True
    # Hop 4: Resolve
    engine.step("ACTION: RESOLVE", target_arm=3)
    assert engine.is_resolved is True
    assert engine.physical_breach_count == 0
    assert engine.semantic_breach_count == 0


def test_benchmark_scenarios_count():
    scenarios = generate_benchmark_scenarios()
    assert len(scenarios) == 120
    stage_counts = {}
    for sc in scenarios:
        stage_counts[sc.stage] = stage_counts.get(sc.stage, 0) + 1
    assert stage_counts == {1: 20, 2: 20, 3: 20, 4: 20, 5: 20, 6: 20}


def test_preemptive_interrupt_gate():
    gate = PreemptiveInterruptGate()
    assert gate.world_epoch == 1
    assert gate.emergency_active is False

    # Stale action rejection before shock
    valid, reason = gate.validate_action_epoch("ACTION: PREPARE system", action_epoch=0)
    assert not valid
    assert "Stale proposal epoch" in reason
    assert gate.preempted_stale_count == 1

    # Trigger emergency shock at t+1
    shock = gate.trigger_shock("shock_1", "pipe_1", "PRESSURE_SPIKE", trigger_tick=2, required_mitigation="ENGAGE emergency_scram")
    assert gate.world_epoch == 2
    assert gate.emergency_active is True
    assert shock.required_mitigation == "ENGAGE emergency_scram"

    # Action planned on epoch 1 during epoch 2 is preempted and safely dropped
    valid, reason = gate.validate_action_epoch("ACTION: PREPARE system", action_epoch=1)
    assert not valid
    assert "PREEMPTED" in reason
    assert gate.preempted_stale_count == 2
    assert gate.unhandled_shock_breaches == 0

    # Emergency mitigation on current epoch succeeds
    valid_mitig, reason_mitig = gate.validate_action_epoch("ACTION: ENGAGE emergency_scram", action_epoch=2)
    assert valid_mitig is True
    assert reason_mitig is None

    resolved = gate.resolve_emergency("ACTION: ENGAGE emergency_scram")
    assert resolved is True
    assert gate.emergency_active is False
    assert gate.emergency_mitigations_count == 1


def test_microworld_stage5_preemptive_interrupt():
    # Solvable case: at tick 1, shock triggers at t+1
    engine = MicroworldEngine(stage=5, domain_id="nuclear_fission_cooling", is_solvable=True)
    
    # Tick 1: Prepare system
    engine.step("ACTION: PREPARE system", target_arm=3)
    assert engine.preemptive_gate.emergency_active is True
    assert engine.preemptive_gate.world_epoch == 2

    # Tick 2: If an action is submitted with stale epoch 1, it is safely dropped
    res_stale = engine.step("ACTION: PREPARE system", target_arm=3, action_epoch=1)
    assert res_stale["status"] == "PREEMPTED"
    assert engine.is_failed is False
    assert engine.physical_breach_count == 0

    # Tick 3: Mitigate emergency shock with scram on valid epoch
    res_mitig = engine.step("ACTION: ENGAGE emergency_scram", target_arm=3, action_epoch=2)
    assert engine.preemptive_gate.emergency_active is False
    assert engine.world_state["status"] == "EMERGENCY_SCRAMMED_SAFELY"

    # Tick 4: Resolve
    engine.step("ACTION: RESOLVE", target_arm=3)
    assert engine.is_resolved is True
    assert engine.physical_breach_count == 0


def test_microworld_stage6_long_horizon_composite():
    # Solvable case: long horizon T=50 with passive entropy decay and pipe rupture shock
    engine = MicroworldEngine(stage=6, domain_id="nuclear_fission_cooling", is_solvable=True, max_ticks=50)
    assert engine.world_state["core_temp"] == 398.0

    # Hop 1: Report anomaly
    engine.step("ACTION: REPORT_ANOMALY OVERHEAT_CORE_B", target_arm=3)
    assert engine.current_hop == 2
    # Verify passive decay
    assert engine.world_state["core_temp"] > 398.0

    # Hop 2: Repair isolation seal (at end of tick 2, shock triggers!)
    engine.step("ACTION: REPAIR isolation_seal", target_arm=3)
    assert engine.current_hop == 3
    assert engine.preemptive_gate.emergency_active is True
    assert engine.preemptive_gate.active_shock.shock_type == "PIPE_RUPTURE"

    # Hop 3: Emergency mitigation
    engine.step("ACTION: ISOLATE breach_valve", target_arm=3)
    assert engine.preemptive_gate.emergency_active is False
    assert engine.world_state["bypass_valve"] == "ISOLATED"

    # Hop 4: Resume plan: Restore coolant valve (abductive mitigation)
    engine.step("ACTION: RESTORE coolant_valve", target_arm=3)
    assert engine.world_state["core_temp"] == 285.0
    assert engine.abductive_resolved is True

    # Hop 5: Resolve
    engine.step("ACTION: RESOLVE", target_arm=3)
    assert engine.is_resolved is True
    assert engine.physical_breach_count == 0
    assert engine.semantic_breach_count == 0
