"""Dual-Clock Temporal Bridge & Real-World Event Reactor.

Bridges real-world monotonic wall-clock intervals with discrete causal ticks.
Supports deterministic SIMULATED benchmark stepping and live REAL_TIME scheduling.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ClockMode(str, Enum):
    """Operational mode of the temporal bridge."""

    SIMULATED = "SIMULATED"  # Deterministic discrete stepping for benchmark reproduction
    REAL_TIME = "REAL_TIME"  # Live monotonic wall-clock scheduling for production deployment


@dataclass
class TemporalAlarm:
    """Scheduled temporal event."""

    alarm_id: str
    target_timestamp: float
    payload: dict[str, Any]
    triggered: bool = False


class TemporalBridge:
    """Manages system time progression, jitter measurement, and real-world alarms."""

    def __init__(
        self,
        mode: ClockMode = ClockMode.SIMULATED,
        tick_interval_seconds: float = 1.0,
    ) -> None:
        self.mode: ClockMode = mode
        self.tick_interval: float = tick_interval_seconds

        # Simulated clock state
        self.simulated_tick: int = 0

        # Real-time state
        self.start_monotonic: float = time.monotonic()
        self.last_tick_monotonic: float = self.start_monotonic
        self.last_user_activity_monotonic: float = self.start_monotonic

        # Jitter metrics
        self.max_jitter_ms: float = 0.0
        self.jitter_history_ms: list[float] = []

        # Alarms
        self.alarms: dict[str, TemporalAlarm] = {}

    def step_simulated(self, delta_ticks: int = 1) -> int:
        """Advances simulated discrete time by delta_ticks."""
        self.simulated_tick += delta_ticks
        return self.simulated_tick

    def register_alarm(self, alarm_id: str, delay_seconds: float, payload: dict[str, Any] | None = None) -> None:
        """Registers an alarm to trigger after delay_seconds."""
        now = time.monotonic() if self.mode == ClockMode.REAL_TIME else float(self.simulated_tick)
        self.alarms[alarm_id] = TemporalAlarm(
            alarm_id=alarm_id,
            target_timestamp=now + delay_seconds,
            payload=dict(payload or {}),
            triggered=False,
        )

    def check_alarms(self) -> list[TemporalAlarm]:
        """Returns and marks all pending alarms that have matured."""
        now = time.monotonic() if self.mode == ClockMode.REAL_TIME else float(self.simulated_tick)
        due: list[TemporalAlarm] = []
        for alarm in self.alarms.values():
            if not alarm.triggered and now >= alarm.target_timestamp:
                alarm.triggered = True
                due.append(alarm)
        return due

    def record_user_activity(self) -> None:
        """Resets idle timer upon user input."""
        self.last_user_activity_monotonic = time.monotonic()

    def get_idle_seconds(self) -> float:
        """Returns elapsed seconds since last user interaction."""
        return time.monotonic() - self.last_user_activity_monotonic

    def measure_real_time_tick(self) -> tuple[float, float]:
        """Measures elapsed interval and scheduling jitter under real-time execution.

        Returns:
            Tuple of (elapsed_seconds, jitter_ms).
        """
        now = time.monotonic()
        elapsed = now - self.last_tick_monotonic
        jitter_ms = abs(elapsed - self.tick_interval) * 1000.0

        self.last_tick_monotonic = now
        self.jitter_history_ms.append(jitter_ms)
        self.max_jitter_ms = max(self.max_jitter_ms, jitter_ms)

        return elapsed, jitter_ms

    def get_aggregate_jitter_stats(self) -> dict[str, float]:
        """Returns summary statistics for real-time tick synchronization."""
        if not self.jitter_history_ms:
            return {"mean_jitter_ms": 0.0, "max_jitter_ms": 0.0, "p95_jitter_ms": 0.0}

        sorted_j = sorted(self.jitter_history_ms)
        p95_idx = int(0.95 * len(sorted_j))
        return {
            "mean_jitter_ms": round(sum(sorted_j) / len(sorted_j), 3),
            "max_jitter_ms": round(self.max_jitter_ms, 3),
            "p95_jitter_ms": round(sorted_j[min(p95_idx, len(sorted_j) - 1)], 3),
        }
