"""Unit tests for HostDreamEngine 4-Phase Consolidation Lifecycle."""

import sys
import tempfile
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from dream_engine import HostDreamEngine
from provenance import EpisodicEvent, EpisodicStream


def test_four_phase_dream_consolidation_lifecycle() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        engine = HostDreamEngine(memory_dir)
        stream = EpisodicStream()

        # Add 3 events across 2 entities
        stream.append(
            EpisodicEvent(
                event_id="e1",
                tick=5,
                entity_id="vault_alpha",
                action_name="init",
                success=True,
                state_delta={"balance": 100, "status": "ACTIVE"},
            )
        )
        stream.append(
            EpisodicEvent(
                event_id="e2",
                tick=10,
                entity_id="vault_beta",
                action_name="init",
                success=True,
                state_delta={"balance": 500, "status": "ACTIVE"},
            )
        )
        stream.append(
            EpisodicEvent(
                event_id="e3",
                tick=15,
                entity_id="vault_alpha",
                action_name="drain",
                success=True,
                state_delta={"balance": 0, "status": "CLOSED"},
            )
        )

        # Run dream cycle
        summary = engine.run_dream_cycle(stream, current_tick=20)

        assert summary.events_consolidated == 3
        assert summary.entities_updated == 2
        assert summary.total_active_entities == 2
        assert summary.duration_ms < 50.0  # Host consolidation is sub-millisecond to low ms

        # Verify entity cards exist and are formatted correctly
        card_alpha = engine.get_entity_card("vault_alpha")
        assert card_alpha is not None
        assert "STATUS: CLOSED" in card_alpha
        assert "balance=0" in card_alpha
        assert "AT_TICK: 15" in card_alpha

        card_beta = engine.get_entity_card("vault_beta")
        assert card_beta is not None
        assert "STATUS: ACTIVE" in card_beta
        assert "balance=500" in card_beta

        # Verify INDEX.md content and budget bounds
        index_text = engine.get_index_content()
        assert "# Memory Index" in index_text
        assert "[vault_alpha]" in index_text
        assert "[vault_beta]" in index_text
        # Enforce budget <= 128 tokens
        assert len(index_text.split()) < 128
