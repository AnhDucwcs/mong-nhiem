"""Unit tests verifying core invariants for MN-023 Minimal Controlled Microworld."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from epistemic_mask import EpistemicMaskEngine
from microworld_engine import MicroworldEngine
from benchmark_scenarios import generate_benchmark_scenarios


def test_epistemic_mask_zero_leakage():
    """Verifies Clause M3: Unobserved private secrets are completely masked from subjective view."""
    mask = EpistemicMaskEngine(
        agent_ids=["agent_1", "agent_2"],
        public_entities={"corridor"},
        agent_initial_visibility={"agent_1": {"terminal_alpha"}},
        private_secrets={"vault_code": "SECRET_999"},
    )

    world = {
        "corridor": {"state": "CLEAR"},
        "terminal_alpha": {"state": "READY", "vault_code": "SECRET_999"},
    }

    # Agent 2 only sees public corridor
    sub_view_2 = mask.filter_state_for_agent("agent_2", world)
    assert "terminal_alpha" not in sub_view_2
    assert "corridor" in sub_view_2

    # Prompt check for agent 2
    prompt_agent_2 = f"STATUS: {sub_view_2}"
    leakage = mask.audit_leakage("agent_2", prompt_agent_2)
    assert leakage == 0.0  # Zero leakage!


def test_non_omniscient_action_groundedness():
    """Verifies Clause M10: Actions attempting to use undiscovered secrets are rejected."""
    mask = EpistemicMaskEngine(
        agent_ids=["agent_1", "agent_2"],
        public_entities={"vault_door"},
        private_secrets={"passcode": "OMEGA_42"},
    )

    world = {"vault_door": {"state": "LOCKED", "passcode": "OMEGA_42"}}
    engine = MicroworldEngine(
        domain_name="test_domain",
        initial_entities=world,
        agent_ids=["agent_1", "agent_2"],
        mask_engine=mask,
    )

    # Agent 2 tries to guess or telepathically open the vault with OMEGA_42 without observing it
    ok, msg, _ = engine.step_action("agent_2", "ACT", "vault_door", {"passcode": "OMEGA_42"})
    assert ok is False
    assert "REJECTED_GROUNDEDNESS_VIOLATION" in msg
    assert engine.groundedness_violations == 1

    # Legitimate path: Agent 2 is granted the secret
    mask.grant_secret("agent_2", "passcode")
    engine.arbiter.acquire("vault_door", "agent_2", 0)
    ok2, msg2, _ = engine.step_action("agent_2", "ACT", "vault_door", {"passcode": "OMEGA_42"})
    assert ok2 is True
    assert msg2 == "COMMITTED"


def test_physical_conservation_invariant_intercept():
    """Verifies Clause M4: Out-of-bounds physical mutations are intercepted with zero committed breaches."""
    mask = EpistemicMaskEngine(["agent_1"], public_entities={"battery"})
    world = {"battery": {"voltage": 240.0}}
    engine = MicroworldEngine(
        domain_name="grid",
        initial_entities=world,
        agent_ids=["agent_1"],
        mask_engine=mask,
        invariant_bounds={"voltage": (200.0, 260.0)},
    )

    engine.arbiter.acquire("battery", "agent_1", 0)
    # Mutation exceeding upper bound (300.0 > 260.0)
    ok, msg, _ = engine.step_action("agent_1", "ACT", "battery", {"property": "voltage", "value": 300.0})
    assert ok is False
    assert "REJECTED_INVARIANT_BREACH" in msg
    assert engine.physical_breaches == 1
    # State remains uncorrupted at 240.0
    assert engine.entities["battery"]["voltage"] == 240.0


def test_concurrency_race_collision_prevention():
    """Verifies Clause M5: Arbiter prevents unmanaged concurrent lease contention."""
    mask = EpistemicMaskEngine(["agent_1", "agent_2"], public_entities={"resource_x"})
    world = {"resource_x": {"state": "IDLE"}}
    engine = MicroworldEngine(
        domain_name="facility",
        initial_entities=world,
        agent_ids=["agent_1", "agent_2"],
        mask_engine=mask,
    )

    # Agent 1 acquires resource_x
    ok1, _ = engine.arbiter.acquire("resource_x", "agent_1", 0)
    assert ok1 is True

    # Agent 2 attempts to act without lease
    ok2, msg2, _ = engine.step_action("agent_2", "ACT", "resource_x", {"property": "state", "value": "RUNNING"})
    assert ok2 is False
    assert "REJECTED_UNAUTHORIZED_NO_LEASE" in msg2
