"""Unit tests for AutoDream fact card projection and memory consolidation."""

from mong_nhiem.extensions.autodream.consolidator import AutoDreamConsolidator, FrontierBranchPruner
from mong_nhiem.extensions.autodream.fact_cards import FactCardProjector


def test_fact_card_projector_formatting():
    projector = FactCardProjector(default_token_ceiling=512)
    card = projector.render_card(
        entity_id="substation_a",
        version=3,
        properties={"balance": 40.0, "status": "ACTIVE"},
        holder="agent_1",
    )
    assert card == "[substation_a v3 holder:agent_1 balance:40 status:ACTIVE]"

    entities = {
        "res_1": {"version": 1, "holder": "a1", "val": 10},
        "res_2": {"version": 2, "holder": None, "val": 20},
    }
    text, tokens = projector.project_fact_cards(entities, header="ACTIVE RESOURCES:")
    assert "ACTIVE RESOURCES:" in text
    assert "[res_1 v1 holder:a1 val:10]" in text
    assert "[res_2 v2 val:20]" in text
    assert tokens < 512


def test_autodream_consolidator_compaction():
    consolidator = AutoDreamConsolidator(target_compaction_ratio=0.70)
    # Simulate a stream of 20 interaction events mutating 3 entities
    event_log = []
    for i in range(20):
        target = f"target_{i % 3}"
        event_log.append({
            "target": target,
            "action_type": "ACT",
            "payload": {"step": i, "val": i * 10},
            "tick": i,
            "status": "COMMITTED",
        })

    consolidated, metrics = consolidator.consolidate_episodes(event_log)
    assert len(consolidated) == 3
    assert metrics["raw_event_count"] == 20.0
    assert metrics["consolidated_entity_count"] == 3.0
    assert metrics["compaction_ratio"] >= 0.70
    assert metrics["target_compaction_met"] == 1.0


def test_frontier_branch_pruner():
    pruner = FrontierBranchPruner(frontier_window=3)
    nodes = {
        "h1": {"tick": 1, "event_id": "e1"},
        "h2": {"tick": 3, "event_id": "e2"},
        "h3": {"tick": 7, "event_id": "e3"},
        "h4": {"tick": 8, "event_id": "e4"},
    }
    pruner.update_frontier("h1", [])
    pruner.update_frontier("h2", ["h1"])
    pruner.update_frontier("h3", ["h2"])
    pruner.update_frontier("h4", [])

    active = pruner.prune_frontier(nodes, current_tick=8)
    # At tick 8 with window 3, min_active_tick = 5. Only h3 (tick 7) and h4 (tick 8) remain active
    active_ids = [n["event_id"] for n in active]
    assert "e3" in active_ids
    assert "e4" in active_ids
    assert "e1" not in active_ids
    assert "e2" not in active_ids
