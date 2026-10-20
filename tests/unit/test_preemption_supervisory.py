"""Unit Tests for Promoted Human Supervisory Preemption Bridge."""

from mong_nhiem.orchestration.preemption_gate import PreemptiveInterruptGate
from mong_nhiem.preemption import HumanSupervisoryBridge


def test_human_supervisory_standby_and_injection():
    gate = PreemptiveInterruptGate()
    bridge = HumanSupervisoryBridge(preemption_gate=gate)

    assert bridge.in_standby is False
    assert bridge.awaiting_human is False

    # 1. Enter standby on QUERY
    bridge.enter_standby(reason="SLM requested user confirmation for high-voltage breaker")
    assert bridge.in_standby is True
    assert bridge.awaiting_human is True

    # Check status
    status = bridge.get_standby_status()
    assert status["in_standby"] is True
    assert status["awaiting_human"] is True

    # 2. Human injects command
    old_epoch = gate.world_epoch
    new_epoch = bridge.inject_human_command(
        raw_command="Override breaker open, maintain standby",
        action_override="ACTION: TRIP_BREAKER",
    )
    assert new_epoch > old_epoch
    assert bridge.in_standby is False
    assert bridge.awaiting_human is False
    assert bridge.last_human_directive == "Override breaker open, maintain standby"
    assert len(bridge.command_history) == 1
    assert bridge.command_history[0].resolved_standby is True


def test_validate_action_epoch_preemption():
    gate = PreemptiveInterruptGate()
    bridge = HumanSupervisoryBridge(preemption_gate=gate)

    start_epoch = gate.world_epoch

    # Proposed action matching epoch passes
    valid, _reason = bridge.validate_action_against_human_epoch("ACTION: NOMINAL_STEP", start_epoch)
    assert valid is True

    # Human intervenes
    bridge.inject_human_command(raw_command="Emergency stop")

    # Stale proposal from old epoch is dropped
    valid_stale, reason_stale = bridge.validate_action_against_human_epoch("ACTION: NOMINAL_STEP", start_epoch)
    assert valid_stale is False
    assert "STALE" in reason_stale.upper() or "EPOCH" in reason_stale.upper()
