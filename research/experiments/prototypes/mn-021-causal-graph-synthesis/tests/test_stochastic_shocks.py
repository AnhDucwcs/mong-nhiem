"""Unit tests for Stochastic World Shock Injector Engine (MN-021)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.stochastic_shock_injector import StochasticShockInjector


def test_shock_registration_and_generation():
    injector = StochasticShockInjector(seed=42)
    shock = injector.register_case_shock(
        case_id="MB-005",
        domain="martian_biosphere",
        target_entity="power_grid",
        trigger_tick=3,
        shock_type="dust_squall",
    )

    assert shock.target_entity == "power_grid"
    assert shock.trigger_tick == 3
    assert shock.state_delta["solar_fouling_pct"] == 75
    assert shock.state_delta["grid_power_available"] == 35
    assert "dust squall" in shock.description.lower()
