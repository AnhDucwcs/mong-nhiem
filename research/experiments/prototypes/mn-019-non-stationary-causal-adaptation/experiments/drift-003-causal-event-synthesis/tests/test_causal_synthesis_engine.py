"""Tests for CausalSynthesisEngine in Stage 3."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from causal_event_logger import CausalEventLog
from causal_synthesis_engine import CausalRule, CausalSynthesisEngine


def test_causal_rule_trigger():
    rule = CausalRule(
        rule_id="CRULE_TEST",
        domain="orbital_life_support",
        action_prefix="divert_solar_power",
        condition_entity="thermal_loop",
        condition_property="temperature",
        condition_operator=">",
        condition_threshold=70.0,
        trap_consequence="THERMAL_TRIP",
    )

    entities_safe = {"thermal_loop": {"properties": {"temperature": 65.0}}}
    entities_danger = {"thermal_loop": {"properties": {"temperature": 75.0}}}

    assert rule.is_triggered("divert_solar_power cryo_battery 80.0", entities_safe) is False
    assert rule.is_triggered("divert_solar_power cryo_battery 80.0", entities_danger) is True
    assert rule.is_triggered("purge_cabin_heat 40.0", entities_danger) is False


def test_causal_rule_card_rendering():
    rule = CausalRule(
        rule_id="CRULE_TEST",
        domain="orbital_life_support",
        action_prefix="divert_solar_power",
        condition_entity="thermal_loop",
        condition_property="temperature",
        condition_operator=">",
        condition_threshold=70.0,
        trap_consequence="THERMAL_TRIP",
    )
    card = rule.to_card_string()
    assert "[CAUSAL_RULE CRULE_TEST" in card
    assert "IF thermal_loop.temperature>70.0" in card
    assert "TRAP THERMAL_TRIP" in card
    assert "AVOID 'divert_solar_power'" in card


def test_causal_engine_evaluation():
    engine = CausalSynthesisEngine("orbital_life_support")
    entities = {"thermal_loop": {"properties": {"temperature": 75.0}}}

    risk = engine.evaluate_action_causal_risk("divert_solar_power cryo_battery 80.0", entities)
    assert risk is not None
    assert risk.rule_id == "CRULE_SOLAR_HEAT_COUPLING"

    risk_safe = engine.evaluate_action_causal_risk("purge_cabin_heat 40.0", entities)
    assert risk_safe is None
