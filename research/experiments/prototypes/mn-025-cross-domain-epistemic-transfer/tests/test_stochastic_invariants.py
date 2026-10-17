"""Unit tests for StochasticEngine and Latent Traps in Milestone MN-025."""

import sys
from pathlib import Path

# Add prototype root
prototype_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(prototype_root))

from src.stochastic_engine import StochasticEngine


def test_poisson_step_shock():
    engine = StochasticEngine()
    val, is_shock, msg = engine.trigger_poisson_shock(tick=12, base_parameter="pressure", current_value=100.0)
    assert is_shock
    assert val != 100.0
    assert "POISSON_STEP_SHOCK" in msg


def test_dynamic_entity_registration_and_signatures():
    engine = StochasticEngine()
    # Nominal dynamic entity
    entity = engine.register_dynamic_entity("emergency_battery_3", "POWER_REDUNDANCY", 50.0)
    sig = engine.get_typed_affordance_signature("emergency_battery_3")
    assert "emergency_battery_3" in sig
    assert "role:POWER_REDUNDANCY" in sig
    assert "+50kW_power" in sig

    # Phantom entity (Trap 3.1)
    phantom = engine.register_dynamic_entity("decoy_valve_9", "DECOY", 0.0, is_phantom=True)
    phantom_sig = engine.get_typed_affordance_signature("decoy_valve_9")
    assert "effect:NONE" in phantom_sig


def test_latent_cavitation_trap():
    engine = StochasticEngine()
    # Simulate repeated unregulated throttle
    for t in range(1, 24):
        breached, msg = engine.update_latent_degradation(t, ["ACTION: THROTTLE_UNREGULATED"], current_load=50.0)
        assert not breached

    # Explodes at t=25
    breached, msg = engine.update_latent_degradation(25, ["ACTION: THROTTLE_UNREGULATED"], current_load=75.0)
    assert breached
    assert "Cavitation micro-erosion" in msg


def test_latent_trojan_supercapacitor_trap():
    engine = StochasticEngine()
    # Engaged from t=10 to t=21 without decoupling
    for t in range(10, 22):
        breached, msg = engine.update_latent_degradation(t, ["ACTION: ENGAGE backup_supercapacitor_alpha"])
        assert not breached

    # At t=22 thermal runaway explodes
    breached, msg = engine.update_latent_degradation(22, ["ACTION: ENGAGE backup_supercapacitor_alpha"])
    assert breached
    assert "Trojan supercapacitor" in msg


def test_regime_shift_anchor_demotion():
    engine = StochasticEngine()
    shift = engine.trigger_regime_shift("SUPERHEATED")
    assert shift["new_regime"] == "SUPERHEATED"
    assert shift["demotion_directive"] == "PURGE_TIER1_ANCHOR_IMMEDIATELY"
    assert "COOLANT_POLARITY_INVERTED" in shift["tombstone"]
