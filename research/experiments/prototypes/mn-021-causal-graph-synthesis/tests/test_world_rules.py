"""Unit tests for World Rule Engine and Invariant Verification (MN-021)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.world_rules import WorldRuleEngine


def test_martian_biosphere_invariants():
    engine = WorldRuleEngine("martian_biosphere")

    # Valid scrubber start with sufficient power
    valid, err = engine.validate_action_transition(
        {"grid_power_available": 60, "grid_power_consumed": 20},
        {"scrubber_state": "ACTIVE"},
    )
    assert valid is True
    assert err is None

    # Invalid scrubber start: insufficient power (requires 25 kW)
    valid, err = engine.validate_action_transition(
        {"grid_power_available": 30, "grid_power_consumed": 20},
        {"scrubber_state": "ACTIVE"},
    )
    assert valid is False
    assert "Insufficient power" in err

    # Burst ceiling test
    valid, err = engine.validate_action_transition(
        {"water_line_pressure": 120},
        {"water_line_pressure": 155},
    )
    assert valid is False
    assert "burst ceiling" in err


def test_subsea_hydrothermal_invariants():
    engine = WorldRuleEngine("subsea_hydrothermal")

    # Cavitation ceiling breach
    valid, err = engine.validate_action_transition(
        {"cavitation_index": 1.4},
        {"cavitation_index": 1.1},
    )
    assert valid is False
    assert "cavitation index" in err


def test_orbital_constellation_invariants():
    engine = WorldRuleEngine("orbital_constellation")

    # Pointing error breach
    valid, err = engine.validate_action_transition(
        {"attitude_error_deg": 0.08},
        {"laser_link_state": "ACTIVE"},
    )
    assert valid is False
    assert "pointing error" in err
