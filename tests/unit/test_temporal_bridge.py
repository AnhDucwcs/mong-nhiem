"""Unit Tests for Promoted Temporal Bridge Module."""

import time

from mong_nhiem.temporal import ClockMode, TemporalBridge


def test_temporal_bridge_simulated_stepping():
    bridge = TemporalBridge(mode=ClockMode.SIMULATED, tick_interval_seconds=1.0)
    assert bridge.simulated_tick == 0

    assert bridge.step_simulated(1) == 1
    assert bridge.step_simulated(4) == 5

    # Alarms in simulated mode
    bridge.register_alarm("alarm_1", delay_seconds=3.0, payload={"event": "maintenance"})
    assert len(bridge.check_alarms()) == 0

    bridge.step_simulated(2)  # tick = 7, target was 5+3=8
    assert len(bridge.check_alarms()) == 0

    bridge.step_simulated(1)  # tick = 8
    due = bridge.check_alarms()
    assert len(due) == 1
    assert due[0].alarm_id == "alarm_1"
    assert due[0].payload == {"event": "maintenance"}


def test_temporal_bridge_real_time_jitter():
    bridge = TemporalBridge(mode=ClockMode.REAL_TIME, tick_interval_seconds=0.01)

    time.sleep(0.015)
    elapsed, jitter_ms = bridge.measure_real_time_tick()
    assert elapsed > 0.01
    assert jitter_ms >= 0.0

    stats = bridge.get_aggregate_jitter_stats()
    assert "mean_jitter_ms" in stats
    assert "max_jitter_ms" in stats
    assert stats["max_jitter_ms"] >= 0.0


def test_temporal_bridge_user_idle_tracking():
    bridge = TemporalBridge()
    t0_idle = bridge.get_idle_seconds()
    time.sleep(0.02)
    assert bridge.get_idle_seconds() >= t0_idle

    bridge.record_user_activity()
    assert bridge.get_idle_seconds() < 0.05
