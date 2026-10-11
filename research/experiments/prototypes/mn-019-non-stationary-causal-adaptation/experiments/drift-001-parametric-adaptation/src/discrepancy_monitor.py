"""Host-Authoritative Discrepancy Monitor for Non-Stationary Parametric Drift.

Detects divergence between nominal physical transition expectations and actual
microworld states (|actual - nominal| > epsilon), registers active drift alerts,
and generates compact prompt context cards.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DriftAlert:
    """Discrepancy alert emitted when physical property diverges beyond epsilon."""
    entity_id: str
    property_name: str
    actual_value: float
    nominal_value: float
    discrepancy_magnitude: float
    detected_tick: int

    def render_card(self) -> str:
        """Render compact high-density alert card strictly bounded in length."""
        return (
            f"[DRIFT_ALERT: {self.entity_id} {self.property_name} "
            f"act:{self.actual_value:.1f} nom:{self.nominal_value:.1f}]"
        )


class DiscrepancyMonitor:
    """Monitors state discrepancy vectors and maintains active drift registrations."""

    DEFAULT_THRESHOLDS: Dict[str, float] = {
        "efficiency": 0.15,
        "temperature": 4.0,
        "charge_kwh": 3.0,
        "o2_pressure": 1.5,
        "voltage": 8.0,
        "soc": 5.0,
        "cargo_temp": 2.5,
        "power_kw": 2.0,
        "chamber_pressure": 10.0,
        "core_temp": 5.0,
        "bias_ppm": 20.0,
        "default": 2.0,
    }

    def __init__(self, custom_thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = copy_dict = dict(self.DEFAULT_THRESHOLDS)
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)
        self.active_alerts: Dict[str, DriftAlert] = {}
        self.alert_history: List[DriftAlert] = []

    def evaluate_step(
        self,
        nominal_state: Dict[str, Dict[str, Any]],
        actual_state: Dict[str, Dict[str, Any]],
        current_tick: int,
    ) -> List[DriftAlert]:
        """Compute discrepancy vector across all entities and update active alerts.
        
        Args:
            nominal_state: {entity_id: {prop: val}} expected under nominal parameters.
            actual_state: {entity_id: {prop: val}} post-execution actual state.
            current_tick: Current simulation clock tick.
            
        Returns:
            List of newly registered drift alerts on this step.
        """
        new_alerts: List[DriftAlert] = []

        for eid, act_props in actual_state.items():
            nom_props = nominal_state.get(eid, {})
            for prop_k, act_val in act_props.items():
                if not isinstance(act_val, (int, float)):
                    continue
                nom_val = nom_props.get(prop_k, act_val)
                if not isinstance(nom_val, (int, float)):
                    continue

                diff = abs(float(act_val) - float(nom_val))
                thresh = self.thresholds.get(prop_k, self.thresholds["default"])

                alert_key = f"{eid}:{prop_k}"
                if diff > thresh:
                    alert = DriftAlert(
                        entity_id=eid,
                        property_name=prop_k,
                        actual_value=float(act_val),
                        nominal_value=float(nom_val),
                        discrepancy_magnitude=round(diff, 2),
                        detected_tick=current_tick,
                    )
                    self.active_alerts[alert_key] = alert
                    self.alert_history.append(alert)
                    new_alerts.append(alert)
                else:
                    # Clear resolved alert if discrepancy dropped below threshold
                    if alert_key in self.active_alerts and diff <= (thresh * 0.5):
                        del self.active_alerts[alert_key]

        return new_alerts

    def has_active_drift(self, entity_id: str, property_name: Optional[str] = None) -> bool:
        """Check if an entity or specific property is currently flagged with drift."""
        if property_name:
            return f"{entity_id}:{property_name}" in self.active_alerts
        return any(k.startswith(f"{entity_id}:") for k in self.active_alerts)

    def render_active_drift_cards(self, max_cards: int = 3) -> str:
        """Render active alerts into high-density prompt cards bounded in token length."""
        if not self.active_alerts:
            return ""
        # Return top N by discrepancy magnitude
        sorted_alerts = sorted(
            self.active_alerts.values(),
            key=lambda a: a.discrepancy_magnitude,
            reverse=True,
        )[:max_cards]
        return " ".join(alert.render_card() for alert in sorted_alerts)
