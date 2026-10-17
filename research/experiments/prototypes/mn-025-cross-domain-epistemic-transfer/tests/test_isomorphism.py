"""Unit tests for IsomorphismEngine in Milestone MN-025."""

import sys
from pathlib import Path

# Add prototype root
prototype_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(prototype_root))

from src.isomorphism_engine import DOMAIN_BINDINGS, FunctionalRole, IsomorphismEngine


def test_abstract_schema_chain():
    chain = IsomorphismEngine.get_abstract_schema()
    assert len(chain) == 3
    assert chain[0] == (FunctionalRole.SENSOR, FunctionalRole.ISOLATOR)
    assert chain[1] == (FunctionalRole.ISOLATOR, FunctionalRole.ACTUATOR)
    assert chain[2] == (FunctionalRole.ACTUATOR, FunctionalRole.STABILIZER)


def test_topological_schema_card_rendering():
    card_hab = IsomorphismEngine.render_topological_schema_card("orbital_habitat")
    assert "TOPOLOGICAL_SCHEMA" in card_hab
    assert "SEAL regulator_intake_seal" in card_hab
    assert "ENGAGE compressor_cabin_circulation" in card_hab

    card_grid = IsomorphismEngine.render_topological_schema_card("smart_microgrid")
    assert "ISOLATE breaker_islanding_switch" in card_grid
    assert "ENGAGE inverter_bess_discharge" in card_grid


def test_negative_transfer_interception():
    # Trap 1.1: Venting in Orbital Habitat must be intercepted
    is_valid, reason = IsomorphismEngine.validate_action("orbital_habitat", "VENT", "pressure_relief")
    assert not is_valid
    assert "NEGATIVE_TRANSFER_VIOLATION" in reason
    assert "Atmospheric decompression" in reason

    # Trap 1.2: Direct cross-connect in Microgrid must be intercepted
    is_valid, reason = IsomorphismEngine.validate_action("smart_microgrid", "CROSS_CONNECT", "busbar")
    assert not is_valid
    assert "NEGATIVE_TRANSFER_VIOLATION" in reason
    assert "Short-circuit breach" in reason

    # Valid action passes
    is_valid, reason = IsomorphismEngine.validate_action("orbital_habitat", "SEAL", "regulator_intake_seal")
    assert is_valid
    assert reason is None
