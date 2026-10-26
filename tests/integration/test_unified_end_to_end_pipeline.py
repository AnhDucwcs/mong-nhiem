"""End-to-End Unified Pipeline Integration Test for Mộng Nhiễm Kernel.

Demonstrates that a consumer initializes a single MongNhiemKernel instance,
loads a schema configuration, and only calls kernel.tick() in a loop while
all 9 adversarial cognitive frontier safeguards automatically fire in cohesion:
1. Trajectory lookahead safety (O(1) projection)
2. Commit-time live state double-check
3. Byzantine stuck-at sensor diagnostic probe forcing
4. Cumulative sub-threshold drift retention (FactCards)
5. Bimodal action-communication coherence arbitration
6. Starvation-free livelock preemption (Urgency-Cost + Aging)
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import time
from typing import Any

from mong_nhiem.bimodal import CommClass
from mong_nhiem.kernel import MongNhiemKernel, StepResult
from mong_nhiem.runtime.backends import BaseInferenceBackend


class DynamicAdversarialBackend(BaseInferenceBackend):
    """Controllable backend for driving unified adversarial pipeline scenarios."""

    def __init__(self) -> None:
        self.next_action: str = "COOL_FAST"
        self.next_intent: str = "INFORM:EXPEDITE"
        self.next_message: str = "Executing command"
        self.delay_sec: float = 0.0
        self.on_delay_midpoint: Any = None

    def set_response(
        self,
        action: str,
        intent: str = "INFORM:EXPEDITE",
        message: str = "Executing command",
        delay_sec: float = 0.0,
        on_delay_midpoint: Any = None,
    ) -> None:
        self.next_action = action
        self.next_intent = intent
        self.next_message = message
        self.delay_sec = delay_sec
        self.on_delay_midpoint = on_delay_midpoint

    def generate(self, prompt: str, grammar: str | None = None, session_id: str = "default") -> str:
        if self.delay_sec > 0:
            if self.on_delay_midpoint:
                time.sleep(self.delay_sec / 2.0)
                self.on_delay_midpoint()
                time.sleep(self.delay_sec / 2.0)
            else:
                time.sleep(self.delay_sec)

        return (
            f"ACTION: {self.next_action}\n"
            f"COMMUNICATE [{self.next_intent}]: \"{self.next_message}\""
        )

    def close(self) -> None:
        pass


def test_unified_end_to_end_pipeline() -> None:
    """Verifies all cognitive and physical safeguards operating cohesively in a single kernel."""
    schema_dict: dict[str, Any] = {
        "schema_name": "unified_fission_power_station",
        "description": "Integrated Cyber-Physical Nuclear Reactor and Power Grid",
        "continuous_traits": [
            {
                "name": "coolant_pressure",
                "initial_value": 75.0,
                "min_val": 0.0,
                "max_val": 150.0,
                "rate_per_sec": 0.10,
                "is_decay": False,
            },
            {
                "name": "aux_pressure",
                "initial_value": 18.0,
                "min_val": 0.0,
                "max_val": 100.0,
                "rate_per_sec": 0.05,
                "is_decay": True,
            },
            {
                "name": "vibration_amplitude",
                "initial_value": 0.0,
                "min_val": 0.0,
                "max_val": 10.0,
                "rate_per_sec": 0.20,
                "is_decay": False,
            },
            {
                "name": "sensor_secondary_stuck",
                "initial_value": 50.0,
                "min_val": 0.0,
                "max_val": 100.0,
                "rate_per_sec": 0.0,
                "is_decay": False,
            },
        ],
        "invariants": [
            {
                "id": "inv_high_pressure_trip",
                "condition": "coolant_pressure >= 80.0",
                "target_metric": "coolant_pressure",
                "threshold": 80.0,
                "comparator": ">=",
                "trigger_action": "SCRAM_EMERGENCY",
            },
            {
                "id": "inv_aux_pressure_deadlock",
                "condition": "aux_pressure <= 0.0",
                "target_metric": "aux_pressure",
                "threshold": 0.0,
                "comparator": "<=",
                "trigger_action": "LOCKOUT_VALVE",
            },
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
            {
                "action_verb": "PURGE_OXYGEN",
                "required_states": {},
                "prohibited_states": {},
            },
            {
                "action_verb": "PROBE",
                "required_states": {},
                "prohibited_states": {},
            },
        ],
    }

    backend = DynamicAdversarialBackend()
    kernel = MongNhiemKernel(schema=schema_dict, backend=backend)

    # ------------------------------------------------------------------------
    # STEP 1: Cumulative Sub-Threshold Micro-Drift Accumulation
    # ------------------------------------------------------------------------
    # Advance 4 discrete ticks; vibration_amplitude increases by 0.20 each tick
    for t in range(4):
        res = kernel.tick(stimulus=f"Tick {t} nominal observation", delta_time=1.0)

    # After 4 ticks, cumulative vibration reaches 4 * 0.20 = 0.80 >= 0.50 threshold
    assert len(res.fact_cards) > 0, "Cumulative tracker must synthesize FactCard for rolling micro-drift"
    vibration_card = next((c for c in res.fact_cards if c.entity == "vibration_amplitude"), None)
    assert vibration_card is not None
    assert vibration_card.priority == "CRITICAL_PERSISTENT"
    assert vibration_card.value >= 0.80

    # ------------------------------------------------------------------------
    # STEP 2: Byzantine Stuck-at Sensor & Equifinality Diagnostic Probe
    # ------------------------------------------------------------------------
    # sensor_secondary_stuck has been static at 50.0 for 4 ticks (zero variance)
    kernel.set_candidate_hypotheses(["LEAK", "PUMP_STALL"])
    probe_res = kernel.tick(stimulus="Pressure drop detected", delta_time=0.1)
    assert "PROBE" in probe_res.action_verb, f"Must enforce PROBE when equifinality meets stuck sensor, got: {probe_res.action_verb}"
    assert "sensor_secondary_stuck" in probe_res.action_verb

    # Clear hypotheses to proceed to next test phase
    kernel.set_candidate_hypotheses([])

    # ------------------------------------------------------------------------
    # STEP 3: Trajectory Lookahead Deadlock Trap (4-Step Forward Projection)
    # ------------------------------------------------------------------------
    # COOL_FAST depletes aux_pressure by 5.0 per step (at T+4: 18 - 20 = -2 <= 0.0 deadlock)
    backend.set_response(action="COOL_FAST", intent="INFORM:EXPEDITE", message="Initiating rapid cooling")
    lookahead_res = kernel.tick(stimulus="Core temperature slightly elevated", delta_time=1.0)
    assert lookahead_res.action_verb == "ABSTAIN_LOOKAHEAD_DEADLOCK_TRAP"
    assert lookahead_res.preempted is True

    # ------------------------------------------------------------------------
    # STEP 4: Mid-Inference Physical State Invalidation (Commit-Time Double Check)
    # ------------------------------------------------------------------------
    # Safe action COOL_MODERATE proposed, but during 150ms inference, pressure spikes to 83.2 bar
    def spike_pressure_during_inference() -> None:
        kernel.state_engine.set_variable("coolant_pressure", 83.2)

    backend.set_response(
        action="COOL_MODERATE",
        intent="INFORM:OPERATE",
        message="Maintaining moderate flow",
        delay_sec=0.10,
        on_delay_midpoint=spike_pressure_during_inference,
    )
    mid_res = kernel.tick(stimulus="Nominal maintenance", delta_time=0.01)
    assert "ABSTAIN_INFERENCE_INVALIDATED" in mid_res.action_verb
    assert "SCRAM_EMERGENCY" in mid_res.action_verb

    # Reset coolant_pressure to safe level for remaining checks
    kernel.state_engine.set_variable("coolant_pressure", 50.0)

    # ------------------------------------------------------------------------
    # STEP 5: Bimodal Action-Communication Coherence & Anti-False-Positive
    # ------------------------------------------------------------------------
    # Case A: Contradictory emission (PURGE with SECURE intent tag)
    backend.set_response(action="PURGE_OXYGEN", intent="INFORM:SECURE", message="Emergency purge underway")
    desync_res = kernel.tick(stimulus="Containment alert", delta_time=0.01)
    assert desync_res.action_verb == "ABSTAIN_DESYNC_BLOCKED"

    # Case B: Contrastive natural language with matching intent tag
    backend.set_response(
        action="PURGE_OXYGEN",
        intent="INFORM:PURGE",
        message="Toi buoc phai xa oxy chu khong the giu an toan cho khoang nay duoc nua!",
    )
    coherent_res = kernel.tick(stimulus="High oxygen alert", delta_time=0.01)
    assert coherent_res.action_verb == "PURGE_OXYGEN"

    # ------------------------------------------------------------------------
    # STEP 6: Starvation-Free Livelock Preemption (Urgency-Cost + Aging Wait)
    # ------------------------------------------------------------------------
    # Simulate cyclic STANDBY between Agent_Aux (margin=20.0) and Agent_Core (margin=1.5)
    kernel.livelock_detector.update_agent_telemetry("Agent_Aux", margin_to_scram=20.0)
    kernel.livelock_detector.update_agent_telemetry("Agent_Core", margin_to_scram=1.5)

    assert kernel.record_agent_standby("Agent_Aux", waiting_for="Agent_Core") is False
    assert kernel.record_agent_standby("Agent_Core", waiting_for="Agent_Aux") is False

    kernel.record_agent_standby("Agent_Aux", waiting_for="Agent_Core")
    kernel.record_agent_standby("Agent_Core", waiting_for="Agent_Aux")

    # Tick 3: Threshold met -> livelock broken!
    is_broken_1 = kernel.record_agent_standby("Agent_Aux", waiting_for="Agent_Core")
    is_broken_2 = kernel.record_agent_standby("Agent_Core", waiting_for="Agent_Aux")
    assert (is_broken_1 or is_broken_2) is True
    # Verify Agent_Core wins despite alphabetical ordering, proving Priority Inversion is eliminated
    assert kernel.livelock_detector.get_elected_agent() == "Agent_Core"

    kernel.close()
