"""Unit tests for AutoDreamCoordinator and RECALL affordances."""

import sys
import tempfile
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from mong_nhiem.orchestration import AffordanceSpec

from auto_dream_trigger import TriggerConfig
from recall_coordinator import AutoDreamCoordinator


def test_recall_gbnf_grammar_compilation() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        coord = AutoDreamCoordinator(Path(tmpdir))
        spec = AffordanceSpec(reads=["doc1"], dispatches=[("fetch", "key")])

        # Grammar without known recallable entities
        base_gbnf = coord.compile_gbnf_grammar(spec, known_entities=[])
        assert "recall-action" not in base_gbnf

        # Grammar with known recallable entities
        recall_gbnf = coord.compile_gbnf_grammar(
            spec,
            known_entities=["vault_alpha", "vault_beta"],
        )
        assert "recall-action" in recall_gbnf
        assert '"vault_alpha"' in recall_gbnf
        assert '"vault_beta"' in recall_gbnf
        assert 'action ::= "ACTION: " ( recall-action |' in recall_gbnf


def test_recall_and_working_prompt_assembly() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        coord = AutoDreamCoordinator(memory_dir)

        # Record events and run dream
        coord.record_and_evaluate(
            tick=1,
            entity_id="vault_alpha",
            action_name="init",
            success=True,
            state_delta={"balance": 500, "status": "ACTIVE"},
            error_code=None,
            working_tokens=150,
        )
        coord.engine.run_dream_cycle(coord.stream, current_tick=1)

        # Issue recall
        card = coord.handle_recall("vault_alpha")
        assert card is not None
        assert "vault_alpha" in card
        assert "balance=500" in card

        # Assemble prompt
        prompt = coord.format_working_prompt(
            task_instruction="Audit vault_alpha",
            current_state_summary="Turn 2",
            recent_turns=["ACTION: RECALL vault_alpha"],
        )

        assert "MEMORY_INDEX:" in prompt
        assert "[vault_alpha]" in prompt
        assert "RECALLED_FACTS:" in prompt
        assert "[RECALLED: ENTITY: vault_alpha" in prompt
        # Verify token budget is well within <= 512
        assert len(prompt.split()) < 300


def test_emergency_pressure_triggers_dream_and_flushes_buffer() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        config = TriggerConfig(context_pressure_token_threshold=400)
        coord = AutoDreamCoordinator(memory_dir, trigger_config=config)

        # Set up a recalled card in buffer
        coord.recalled_cards["temp_entity"] = "DUMMY_CARD"
        assert len(coord.recalled_cards) == 1

        # Record event under severe token pressure (420 tokens >= 400)
        dream_fired = coord.record_and_evaluate(
            tick=5,
            entity_id="vault_burst",
            action_name="deposit",
            success=True,
            state_delta={"balance": 999},
            error_code=None,
            working_tokens=420,
        )

        assert dream_fired is True
        # Emergency pressure must flush active recall cards to free memory
        assert len(coord.recalled_cards) == 0

        # Memory card for vault_burst should now exist in persistent storage
        burst_card = coord.engine.get_entity_card("vault_burst")
        assert burst_card is not None
        assert "balance=999" in burst_card
