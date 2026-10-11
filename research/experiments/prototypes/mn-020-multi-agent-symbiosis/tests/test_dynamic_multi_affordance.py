"""Unit tests for Dynamic Multi-Affordance GBNF Compiler."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from concurrency_arbiter import ConcurrencyArbiter
from dynamic_multi_affordance import DynamicMultiAffordanceCompiler


def test_grammar_masks_contested_entities():
    arb = ConcurrencyArbiter()
    # Agent 1 holds lease on battery_bank
    arb.request_lease("agent_1", "battery_bank", current_tick=1)

    allowed = ["charge_battery_storage 25.0", "shed_industrial_feeder 40.0"]

    # Compile grammar for Agent 2: action targeting battery_bank MUST BE PRUNED
    g2 = DynamicMultiAffordanceCompiler.compile_agent_grammar(
        agent_id="agent_2",
        allowed_actions=allowed,
        arbiter=arb,
        current_tick=1,
        known_entity_ids=["battery_bank", "industrial_feeder"],
        peer_agent_id="agent_1",
    )

    assert "charge_battery_storage" not in g2
    assert "shed_industrial_feeder" in g2
    assert "ACQUIRE_LEASE" in g2
    assert "SIGNAL agent_1" in g2


def test_grammar_admits_own_leased_entities():
    arb = ConcurrencyArbiter()
    arb.request_lease("agent_1", "battery_bank", current_tick=1)

    allowed = ["charge_battery_storage 25.0"]

    # Compile grammar for Agent 1 (the lease holder): action MUST BE ADMITTED
    g1 = DynamicMultiAffordanceCompiler.compile_agent_grammar(
        agent_id="agent_1",
        allowed_actions=allowed,
        arbiter=arb,
        current_tick=1,
        known_entity_ids=["battery_bank"],
        peer_agent_id="agent_2",
    )

    assert "charge_battery_storage 25.0" in g1
    assert "YIELD_LEASE" in g1
