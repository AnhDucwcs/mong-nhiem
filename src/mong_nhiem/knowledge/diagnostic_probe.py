"""Diagnostic Probe Enforcement under Byzantine Sensor Equifinality.

When abductive causal reasoning yields conflicting hypotheses (equifinality)
and sensor telemetry exhibits zero-variance stuck-at hardware faults,
forces diagnostic PROBE actions and masks all mutating physical actuations.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DiagnosticDecision:
    """Outcome of diagnostic affordance evaluation."""

    must_probe: bool
    recommended_action: str
    blocked_actions: list[str] = field(default_factory=list)


class DiagnosticProbeEnforcer:
    """Enforces active diagnostic probing when causal equifinality meets untrusted sensors."""

    def evaluate_diagnostic_affordance(
        self,
        symptom: str,
        candidates: list[str],
        telemetry_history: dict[str, list[float]],
    ) -> DiagnosticDecision:
        """Evaluates whether system must probe rather than take blind mutating action."""
        # Check if multiple conflicting candidates exist (equifinality)
        is_equifinal = len(candidates) > 1

        # Check for stuck-at sensor faults (variance == 0 across >= 3 historical samples)
        stuck_sensors: list[str] = []
        for sensor_name, history in telemetry_history.items():
            if len(history) >= 3:
                first = history[0]
                if all(abs(val - first) < 1e-6 for val in history):
                    stuck_sensors.append(sensor_name)

        if is_equifinal and stuck_sensors:
            probe_target = stuck_sensors[0]
            return DiagnosticDecision(
                must_probe=True,
                recommended_action=f"ACTION: PROBE {probe_target}",
                blocked_actions=["ACTION: INCREASE_PUMP", "ACTION: DECREASE_PUMP", "ACTION: ISOLATE_PIPE"],
            )

        return DiagnosticDecision(
            must_probe=False,
            recommended_action="ACTION: DISPATCH_NOMINAL",
            blocked_actions=[],
        )
