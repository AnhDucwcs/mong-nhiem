"""Cumulative Telemetry Residual Accumulator.

Tracks rolling integrals of subtle sub-threshold micro-fluctuations over long horizons.
Synthesizes non-evictable FactCards when cumulative variance exceeds structural thresholds.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from mong_nhiem.extensions.autodream.fact_cards import FactCard


class CumulativeTelemetryTracker:
    """Accumulates sub-threshold parameter drifts across rolling time windows."""

    def __init__(self, window_size: int = 100, anomaly_threshold: float = 0.50) -> None:
        self.window_size = window_size
        self.anomaly_threshold = anomaly_threshold
        self._history: dict[str, list[tuple[int, float]]] = {}

    def record_sample(self, metric: str, value: float, tick: int) -> None:
        """Records a metric telemetry sample."""
        if metric not in self._history:
            self._history[metric] = []
        self._history[metric].append((tick, abs(value)))
        # Enforce rolling window
        if len(self._history[metric]) > self.window_size:
            self._history[metric].pop(0)

    def synthesize_cumulative_fact_card(self, metric: str) -> FactCard | None:
        """Computes rolling sum and produces non-evictable FactCard if threshold breached."""
        if metric not in self._history:
            return None

        samples = self._history[metric]
        rolling_sum = sum(val for _, val in samples)

        if rolling_sum >= self.anomaly_threshold:
            return FactCard(
                entity=metric,
                value=round(rolling_sum, 4),
                priority="CRITICAL_PERSISTENT",
                properties={"sample_count": len(samples), "window": self.window_size},
            )

        return None
