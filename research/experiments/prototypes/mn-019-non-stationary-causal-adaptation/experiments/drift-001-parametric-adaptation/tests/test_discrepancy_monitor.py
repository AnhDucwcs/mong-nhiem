"""Unit tests for discrepancy monitor error detection and alert cards."""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from discrepancy_monitor import DiscrepancyMonitor, DriftAlert


def test_discrepancy_detection_threshold():
    monitor = DiscrepancyMonitor(custom_thresholds={"temperature": 3.0})

    nominal = {
        "thermal_loop": {"temperature": 60.0},
        "solar_array": {"output_kw": 50.0},
    }
    # Actual has temperature at 65.0 (diff = 5.0 > 3.0 threshold)
    actual = {
        "thermal_loop": {"temperature": 65.0},
        "solar_array": {"output_kw": 50.5},  # diff = 0.5 <= default 2.0
    }

    alerts = monitor.evaluate_step(nominal, actual, current_tick=12)

    assert len(alerts) == 1
    assert alerts[0].entity_id == "thermal_loop"
    assert alerts[0].property_name == "temperature"
    assert alerts[0].discrepancy_magnitude == 5.0
    assert alerts[0].detected_tick == 12

    assert monitor.has_active_drift("thermal_loop", "temperature") is True
    assert monitor.has_active_drift("solar_array") is False


def test_alert_card_rendering():
    alert = DriftAlert(
        entity_id="solar_array",
        property_name="efficiency",
        actual_value=0.55,
        nominal_value=1.0,
        discrepancy_magnitude=0.45,
        detected_tick=25,
    )
    card_str = alert.render_card()
    assert "[DRIFT_ALERT: solar_array efficiency act:0.6 nom:1.0]" == card_str


def test_monitor_resolution():
    monitor = DiscrepancyMonitor(custom_thresholds={"temperature": 4.0})

    nominal = {"thermal_loop": {"temperature": 60.0}}
    actual_drifted = {"thermal_loop": {"temperature": 70.0}}

    monitor.evaluate_step(nominal, actual_drifted, current_tick=5)
    assert monitor.has_active_drift("thermal_loop") is True

    # When discrepancy falls below half threshold (diff <= 2.0)
    actual_recovered = {"thermal_loop": {"temperature": 61.5}}
    monitor.evaluate_step(nominal, actual_recovered, current_tick=10)
    assert monitor.has_active_drift("thermal_loop") is False
