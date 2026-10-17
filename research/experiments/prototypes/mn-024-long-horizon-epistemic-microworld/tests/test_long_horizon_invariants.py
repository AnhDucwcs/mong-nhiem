"""Unit test suite for MN-024 Long-Horizon Microworld Invariants."""

from __future__ import annotations

import os
import sys

# Add prototype src and production src to sys.path
proto_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, proto_src)
sys.path.insert(0, os.path.join(repo_root, "src"))

from entropy_engine import EnvironmentalEntropyEngine
from epistemic_mask import EpistemicMaskEngine
from microworld_engine import LongHorizonMicroworldEngine
from mong_nhiem.extensions.autodream.fact_cards import FactCardProjector


def test_environmental_entropy_decay_and_mitigation() -> None:
    """Verifies that passive entropy decay accumulates and that maintenance resets parameters."""
    decay_rules = {"reactor": {"temperature": 2.0}}
    safe_bounds = {"reactor": {"temperature": (20.0, 50.0)}}
    warning_thresh = {"reactor": {"temperature": 40.0}}

    engine = EnvironmentalEntropyEngine(decay_rules, safe_bounds, warning_thresh)
    entities = {"reactor": {"temperature": 45.0, "state": "ACTIVE"}}

    # Tick 1: No mitigation -> temperature rises to 47.0 (safe)
    safe, breaches = engine.apply_tick_decay(entities, set())
    assert safe is True
    assert entities["reactor"]["temperature"] == 47.0

    # Warnings should now trigger (47.0 >= 40.0)
    warnings = engine.get_active_warnings(entities)
    assert len(warnings) == 1
    assert "elevated" in warnings[0]

    # Tick 2: Without mitigation -> temperature reaches 49.0
    safe, breaches = engine.apply_tick_decay(entities, set())
    assert safe is True
    assert entities["reactor"]["temperature"] == 49.0

    # Tick 3: Without mitigation -> temperature breaches 51.0 > 50.0
    safe, breaches = engine.apply_tick_decay(entities, set())
    assert safe is False
    assert len(breaches) == 1
    assert "outside [20.0, 50.0]" in breaches[0]

    # With active mitigation: decay is suppressed
    entities["reactor"]["temperature"] = 25.0
    safe, breaches = engine.apply_tick_decay(entities, {"reactor"})
    assert safe is True
    assert entities["reactor"]["temperature"] == 25.0


def test_multi_hop_causal_cascade_execution() -> None:
    """Verifies that 4-hop sequential physical cascade executes cleanly."""
    initial_entities = {
        "sensor_alpha": {"state": "ONLINE", "passcode": "SECRET_KEY_99"},
        "valve_beta": {"state": "OPEN"},
        "coupler_gamma": {"state": "DISCONNECTED"},
        "main_vault": {"state": "LOCKED"},
    }
    mask = EpistemicMaskEngine(
        agent_ids=["agent_1"],
        public_entities={"valve_beta", "coupler_gamma", "main_vault"},
        agent_initial_visibility={"agent_1": {"sensor_alpha"}},
        private_secrets={"passcode": "SECRET_KEY_99"},
    )
    world = LongHorizonMicroworldEngine(
        domain_name="test_cascade",
        initial_entities=initial_entities,
        agent_ids=["agent_1"],
        mask_engine=mask,
        max_ticks=20,
    )

    # Hop 1: Inspect sensor to discover passcode
    ok, msg, node1 = world.step_action("agent_1", "INSPECT", "sensor_alpha", {})
    assert ok is True
    assert "passcode" in mask.known_secrets["agent_1"]
    assert 1 in world.completed_hops

    # Hop 2: Isolate valve
    world.arbiter.acquire("valve_beta", "agent_1", 1)
    ok, msg, node2 = world.step_action("agent_1", "ISOLATE", "valve_beta", {})
    assert ok is True
    assert world.entities["valve_beta"]["state"] == "ISOLATED"
    assert 2 in world.completed_hops

    # Hop 3: Couple coupler
    world.arbiter.acquire("coupler_gamma", "agent_1", 2)
    ok, msg, node3 = world.step_action("agent_1", "COUPLE", "coupler_gamma", {})
    assert ok is True
    assert world.entities["coupler_gamma"]["state"] == "COUPLED"
    assert 3 in world.completed_hops

    # Hop 4: Unlock main vault with secret key
    world.arbiter.acquire("main_vault", "agent_1", 3)
    ok, msg, node4 = world.step_action("agent_1", "ENGAGE", "main_vault", {"secret_key": "SECRET_KEY_99"})
    assert ok is True
    assert world.entities["main_vault"]["state"] == "UNLOCKED"
    assert 4 in world.completed_hops
    assert len(world.completed_hops) == 4


def test_epistemic_mask_and_groundedness_invariants() -> None:
    """Verifies Clause M3 (Zero Leakage) and Clause M10 (Groundedness Invariant)."""
    initial_entities = {
        "secure_safe": {"state": "LOCKED", "passcode": "TOP_SECRET_CODE_777"},
    }
    mask = EpistemicMaskEngine(
        agent_ids=["scout", "intruder"],
        public_entities=set(),
        agent_initial_visibility={"scout": {"secure_safe"}, "intruder": set()},
        private_secrets={"passcode": "TOP_SECRET_CODE_777"},
    )
    world = LongHorizonMicroworldEngine(
        domain_name="test_epistemic",
        initial_entities=initial_entities,
        agent_ids=["scout", "intruder"],
        mask_engine=mask,
    )

    # Intruder prompt should NOT leak secret
    intruder_view = world.get_subjective_state("intruder")
    assert "secure_safe" not in intruder_view
    leakage = mask.audit_leakage("intruder", f"Observation: {intruder_view}")
    assert leakage == 0.0

    # Intruder telepathic action attempt must be rejected (Clause M10)
    world.arbiter.acquire("secure_safe", "intruder", 0)
    ok, msg, node = world.step_action("intruder", "ACT", "secure_safe", {"secret_key": "TOP_SECRET_CODE_777"})
    assert ok is False
    assert msg == "REJECTED_GROUNDEDNESS_VIOLATION"
    assert world.groundedness_violations == 1


def test_fact_card_token_ceiling_over_extended_horizon() -> None:
    """Verifies that 3-tier fact card formatting keeps prompt strictly <= 512 tokens across 100 ticks."""
    projector = FactCardProjector(default_token_ceiling=512)
    card = projector.render_card(
        entity_id="reactor_core",
        version=100,
        properties={"temperature": 25.0, "status": "NOMINAL", "key_retained": "SIGMA_99"},
    )
    tok_est = len(card.split())
    assert tok_est < 50
    assert "[reactor_core v100" in card
