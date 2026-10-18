"""Dual-Mode Sensor Blackout Telemetry Observer.

Provides proxy telemetry estimation from secondary physical correlates, decays
telemetry confidence under dead-reckoning, and halts blind drift via supervised standby.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class BlackoutMode(str, Enum):
    """Operational mode when primary telemetry sensors are compromised."""

    AUTONOMOUS_IMPROVISE = "AUTONOMOUS_IMPROVISE"
    SUPERVISED_STANDBY = "SUPERVISED_STANDBY"


@dataclass(frozen=True)
class ProxyEstimator:
    """Estimates an unobserved physical metric from an observable correlated metric."""

    target_metric: str
    source_metric: str
    estimator_fn: Callable[[float], float]


class TelemetryObserver:
    """Manages sensor blackout recovery, proxy telemetry synthesis, and confidence TTL."""

    def __init__(
        self,
        mode: BlackoutMode = BlackoutMode.AUTONOMOUS_IMPROVISE,
        decay_rate_per_tick: float = 0.08,
        max_blind_ticks: int = 10,
        estimators: Optional[Dict[str, ProxyEstimator]] = None,
    ) -> None:
        self.mode: BlackoutMode = mode
        self.decay_rate: float = decay_rate_per_tick
        self.max_blind_ticks: int = max_blind_ticks
        self.estimators: Dict[str, ProxyEstimator] = dict(estimators or {})

        # Blackout state
        self.in_blackout: bool = False
        self.blackout_ticks: int = 0
        self.telemetry_confidence: float = 1.0
        self.ttl_exceeded: bool = False

    def register_estimator(self, estimator: ProxyEstimator) -> None:
        """Registers a proxy estimation function for an unobserved metric."""
        self.estimators[estimator.target_metric] = estimator

    def start_blackout(self) -> None:
        """Signals initiation of sensor blackout."""
        self.in_blackout = True
        self.blackout_ticks = 0
        self.telemetry_confidence = 1.0
        self.ttl_exceeded = False

    def end_blackout(self) -> None:
        """Restores nominal sensor operation."""
        self.in_blackout = False
        self.blackout_ticks = 0
        self.telemetry_confidence = 1.0
        self.ttl_exceeded = False

    def step_blackout_tick(self) -> Tuple[float, bool]:
        """Advances blackout duration by one tick, decaying confidence and checking TTL.

        Returns:
            Tuple of (current_confidence: float, is_ttl_exceeded: bool).
        """
        if not self.in_blackout:
            return 1.0, False

        self.blackout_ticks += 1
        self.telemetry_confidence = max(0.0, round(1.0 - (self.blackout_ticks * self.decay_rate), 4))

        if self.blackout_ticks > self.max_blind_ticks:
            self.ttl_exceeded = True
            # Force transition to standby to prevent uncontrolled state drift
            self.mode = BlackoutMode.SUPERVISED_STANDBY

        return self.telemetry_confidence, self.ttl_exceeded

    def estimate_metric(
        self, metric_key: str, available_telemetry: Dict[str, Any]
    ) -> Optional[float]:
        """Synthesizes an unobserved metric from observable correlates using registered estimators."""
        if metric_key not in self.estimators:
            return None

        est = self.estimators[metric_key]
        if est.source_metric in available_telemetry:
            raw_val = float(available_telemetry[est.source_metric])
            return round(est.estimator_fn(raw_val), 2)

        return None
