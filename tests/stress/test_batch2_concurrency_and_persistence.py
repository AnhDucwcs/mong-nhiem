"""Batch 2 Adversarial Stress Tests: Concurrency, Lookahead & Crash Persistence.

Adversarial Stress Test Battery for Milestone MN-029:
- Test 1: Delayed Cascading Dilemma (Multi-step lookahead beyond 1-step affordance)
- Test 7: Multi-Agent Livelock & Starvation (Circular STANDBY dependency breaking)
- Test 9: Mid-Tick Crash & Desync Recovery (3-way Transactional Rollback + Slot Invalidation)
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

from mong_nhiem.kernel import MongNhiemKernel, StepResult
from mong_nhiem.runtime.backends import BaseInferenceBackend


# ============================================================================
# TEST 1: Delayed Cascading Dilemma
# ============================================================================

def test_delayed_cascading_dilemma_baseline() -> None:
    """Test 1: Evaluates whether 4-step lookahead detects delayed physical deadlocks."""
    # Define a microworld where Action A (COOL_FAST) drops aux_pressure by 5.0/tick.
    # At T0, aux_pressure = 18.0 (cutoff is <= 0.0 at T0+4).
    # Action B (COOL_MODERATE) drops aux_pressure by 1.0/tick (remains > 10.0 for 5 ticks).
    schema_dict = {
        "schema_name": "delayed_cascading_microworld",
        "description": "Reactor with delayed auxiliary pressure drop",
        "continuous_traits": [
            {
                "name": "core_temp",
                "initial_value": 350.0,
                "min_val": 0.0,
                "max_val": 1000.0,
                "rate_per_sec": 10.0,
                "is_decay": True,
            },
            {
                "name": "aux_pressure",
                "initial_value": 18.0,
                "min_val": 0.0,
                "max_val": 100.0,
                "rate_per_sec": 0.0,
                "is_decay": False,
            },
        ],
        "invariants": [
            {
                "id": "inv_aux_pressure_deadlock",
                "condition": "aux_pressure <= 0.0",
                "target_metric": "aux_pressure",
                "threshold": 0.0,
                "comparator": "<=",
                "trigger_action": "OXYGEN_VALVE_DEADLOCK",
            }
        ],
        "preconditions": [
            {
                "action_verb": "COOL_FAST",
                "required_states": {},
                "prohibited_states": {},
            },
            {
                "action_verb": "COOL_MODERATE",
                "required_states": {},
                "prohibited_states": {},
            },
        ],
    }

    kernel = MongNhiemKernel(schema=schema_dict)

    # Check if the kernel or lookahead simulator can project trajectory 4 steps forward
    has_lookahead = hasattr(kernel, "check_trajectory_safety") or hasattr(kernel, "lookahead_simulator")
    if not has_lookahead:
        # BASELINE EMPIRICAL EVIDENCE: Unhardened kernel only evaluates T0 preconditions
        pytest.xfail("BASELINE VULNERABILITY: Kernel lacks 4-step Forward Lookahead Trajectory Simulator")

    # If hardened: verify that COOL_FAST is flagged as unsafe across 4 steps
    # (COOL_FAST: aux_pressure decreases by 5.0/step -> at step 4: 18 - 20 = -2 <= 0.0 deadlock)
    # COOL_MODERATE: aux_pressure decreases by 1.0/step -> at step 4: 18 - 4 = 14 > 0 safe
    is_safe_fast = kernel.check_trajectory_safety(action="COOL_FAST", steps=4, delta_time=1.0)
    is_safe_mod = kernel.check_trajectory_safety(action="COOL_MODERATE", steps=4, delta_time=1.0)

    assert is_safe_fast is False, "COOL_FAST must be detected as leading to deadlock at T+4"
    assert is_safe_mod is True, "COOL_MODERATE must be safe across 4 steps"


# ============================================================================
# TEST 7: Multi-Agent Livelock & Starvation
# ============================================================================

def test_multi_agent_livelock_detection_baseline() -> None:
    """Test 7: Tests detection and breaking of circular wait-for STANDBY loops."""
    # Check if LivelockDetector exists in orchestration module
    try:
        from mong_nhiem.orchestration.livelock_detector import LivelockDetector
    except ImportError:
        # BASELINE EMPIRICAL EVIDENCE: Concurrency Arbiter prevents race conditions but lacks Livelock breaker
        pytest.xfail("BASELINE VULNERABILITY: LivelockDetector not yet implemented in v0.2.0")

    detector = LivelockDetector(cycle_threshold_ticks=3)

    # Simulate 2 agents: Agent_Thermal waiting for Voltage >= 50V; Agent_Power waiting for Temp <= 60C
    # Tick 1: Both issue STANDBY
    assert detector.record_agent_standby("Agent_Thermal", waiting_for="Agent_Power") is False
    assert detector.record_agent_standby("Agent_Power", waiting_for="Agent_Thermal") is False

    # Tick 2: Cycle persists
    detector.record_agent_standby("Agent_Thermal", waiting_for="Agent_Power")
    detector.record_agent_standby("Agent_Power", waiting_for="Agent_Thermal")

    # Tick 3: Threshold met -> Livelock broken!
    is_livelock_a = detector.record_agent_standby("Agent_Thermal", waiting_for="Agent_Power")
    is_livelock_b = detector.record_agent_standby("Agent_Power", waiting_for="Agent_Thermal")

    assert (is_livelock_a or is_livelock_b) is True, "Livelock detector must trigger preemption at tick >= 3"
    assert detector.get_preemption_resolution() == "FORCE_DECOUPLED_DISPATCH"


# ============================================================================
# TEST 9: Mid-Tick Crash & Desync Recovery
# ============================================================================

def test_mid_tick_crash_three_way_sync_baseline() -> None:
    """Test 9: Verifies 3-way transactional commit and dirty slot cache invalidation on crash recovery."""
    try:
        from mong_nhiem.state.transactional_sync import TransactionalStateSync
    except ImportError:
        # BASELINE EMPIRICAL EVIDENCE: Atomic JSON exists, but lacks 3-way epoch hash parity and slot invalidation
        pytest.xfail("BASELINE VULNERABILITY: TransactionalStateSync with slot invalidation not implemented")

    temp_dir = tempfile.mkdtemp()
    try:
        sync_manager = TransactionalStateSync(storage_dir=temp_dir)

        # Commit Tick 44 successfully across all 3 components
        sync_manager.commit_epoch(epoch_id=44, state_hash="hash_tick_44", slot_id=0)

        # Simulate mid-write crash at Tick 45: Rust wrote 45, but Python DAG only wrote partial, and slot is dirty
        sync_manager.simulate_partial_crash_write(epoch_id=45, corrupted_component="python_dag")

        # System reboots: Verify recovery
        recovery_result = sync_manager.recover_on_startup()
        assert recovery_result.recovered_epoch == 44, "Must rollback all components to mutually agreed epoch 44"
        assert recovery_result.slot_erased is True, "Must invalidate/erase dirty KV slot cache in llama.cpp"
    finally:
        shutil.rmtree(temp_dir)
