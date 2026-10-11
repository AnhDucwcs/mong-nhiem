"""Tests for AutoDream Causal Cards in Stage 3."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from autodream_engine import AutoDreamEngine


def test_autodream_causal_rule_card():
    engine = AutoDreamEngine(
        initial_entities={
            "battery": {
                "entity_type": "storage",
                "properties": {"soc": 80.0},
                "relations": {"powers": "bus"},
            }
        }
    )

    card_str = "[CAUSAL_RULE CRULE_COLLAPSE IF battery.soc<50.0 TRAP BLACKOUT AVOID 'connect_feeder']"
    engine.add_causal_rule_card("CRULE_COLLAPSE", card_str)

    mem_block = engine.render_memory_block()
    assert "[CAUSAL_RULE CRULE_COLLAPSE" in mem_block
    assert "[ENTITY battery:storage" in mem_block

    # Test compaction with telemetry stream
    for turn in range(5):
        engine.ingest_turn(turn, f"ACTION: DISPATCH probe_{turn}", {"battery": {"soc": 80.0 - turn}})

    engine.finalize({"battery": {"entity_type": "storage", "properties": {"soc": 75.0}}})
    ratio = engine.get_compaction_ratio()
    assert ratio >= 0.70
