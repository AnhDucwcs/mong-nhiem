"""Unit tests for Schema-Evolved AutoDream Engine."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from autodream_engine import AutoDreamEngine
from microworld_engine import WorldEntity


def test_relational_fact_card_rendering():
    ent = WorldEntity(
        entity_id="aux_cooler",
        entity_type="cooler",
        properties={"cooling_kw": 30.0},
        relations={"cools": "thermal_loop"},
        version=1,
        is_active=True,
    )
    card = ent.render_compact()
    assert "[ENTITY aux_cooler:cooler v1 active" in card
    assert "cooling_kw=30.0" in card
    assert "-> cools:thermal_loop" in card

    # Token length invariant (<= 48 tokens)
    token_len = len(card.split())
    assert token_len <= 48


def test_autodream_compaction_and_pruning():
    autodream = AutoDreamEngine()
    autodream.update_fact_card(
        "aux_cooler",
        {"entity_type": "cooler", "properties": {"cooling_kw": 30.0}, "relations": {"cools": "thermal_loop"}},
    )

    # Ingest several raw turns to simulate history
    for t in range(1, 10):
        autodream.ingest_turn(
            turn_num=t,
            action="activate_secondary_cooler",
            world_state={"aux_cooler": {"cooling_kw": 30.0}, "thermal_loop": {"temperature": 75.0 - t}},
        )

    autodream.finalize({"aux_cooler": {"entity_type": "cooler", "properties": {"cooling_kw": 30.0}}})
    compaction = autodream.get_compaction_ratio()
    assert compaction >= 0.70
