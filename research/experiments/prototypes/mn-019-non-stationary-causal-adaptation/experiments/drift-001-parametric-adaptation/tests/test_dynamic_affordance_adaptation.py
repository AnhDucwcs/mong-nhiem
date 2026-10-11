"""Unit tests for GBNF grammar generation with active drift pruning."""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from discrepancy_monitor import DiscrepancyMonitor
from dynamic_affordance import DynamicAffordanceCompiler


def test_nominal_grammar_compilation():
    allowed = ["divert_solar_power cryo_battery 50.0", "purge_cabin_heat 20.0"]
    grammar = DynamicAffordanceCompiler.compile_grammar(
        allowed_actions=allowed,
        known_entity_ids=["solar_array", "cryo_battery"],
        allow_resolve=False,
        allow_recall=True,
    )
    assert '"ACTION: DISPATCH divert_solar_power cryo_battery 50.0"' in grammar
    assert '"ACTION: DISPATCH purge_cabin_heat 20.0"' in grammar
    assert '"ACTION: RECALL solar_array"' in grammar
    assert '"ACTION: RESOLVE COMPLETE"' not in grammar


def test_active_drift_pruning_and_injection():
    monitor = DiscrepancyMonitor()
    # Simulate active drift on thermal_loop
    monitor.evaluate_step(
        {"thermal_loop": {"temperature": 60.0}},
        {"thermal_loop": {"temperature": 75.0}},
        current_tick=15,
    )

    allowed = ["purge_cabin_heat 40.0", "boost_scrubber_oxygen 5.0"]
    grammar = DynamicAffordanceCompiler.compile_grammar(
        allowed_actions=allowed,
        known_entity_ids=["thermal_loop"],
        allow_resolve=False,
        allow_recall=False,
        discrepancy_monitor=monitor,
    )

    # Inviable action under thermal drift ("purge_cabin_heat 40.0") must be PRUNED!
    assert '"ACTION: DISPATCH purge_cabin_heat 40.0"' not in grammar
    # Compensatory action ("engage_auxiliary_cryo_pump") must be INJECTED!
    assert '"ACTION: DISPATCH engage_auxiliary_cryo_pump"' in grammar
    assert '"ACTION: DISPATCH boost_scrubber_oxygen 5.0"' in grammar
