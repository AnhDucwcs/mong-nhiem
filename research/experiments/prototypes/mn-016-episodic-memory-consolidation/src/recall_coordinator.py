"""AutoDream Coordinator and Recall Affordance Integration.

Integrates Host-Authoritative AutoDream memory with Mộng Nhiễm's Dual-Layer
Orchestration framework (mong_nhiem.orchestration):
- Dynamic GBNF compilation for `ACTION: RECALL <entity_id>`.
- Injects INDEX.md as bounded prior (<= 128 tokens).
- Injects recalled Fact Cards dynamically (<= 48 tokens per card, max 2 cards).
- Monitors token pressure and executes emergency consolidation at >= 400 tokens.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from mong_nhiem.orchestration import (
    ActionType,
    AffordanceSpec,
    DynamicGBNFCompiler,
    ToolAction,
    format_action,
    parse_action,
)

try:
    from .auto_dream_trigger import AutonomousAutoDreamTrigger, TriggerConfig, TriggerType
    from .dream_engine import HostDreamEngine
    from .provenance import EpisodicEvent, EpisodicStream, EventProvenance
except ImportError:
    from auto_dream_trigger import AutonomousAutoDreamTrigger, TriggerConfig, TriggerType
    from dream_engine import HostDreamEngine
    from provenance import EpisodicEvent, EpisodicStream, EventProvenance


@dataclass
class AutoDreamResult:
    """Outcome of an extended orchestrator execution with memory."""

    status: str
    turns: int
    final_payload: str
    events_recorded: int
    consolidations_triggered: int
    peak_tokens: int
    history: list[dict[str, Any]] = field(default_factory=list)


class AutoDreamCoordinator:
    """Orchestrates long-horizon task execution with AutoDream memory consolidation."""

    MAX_RECALL_BUFFER_CARDS = 2
    TOKEN_PRESSURE_LIMIT = 400

    def __init__(
        self,
        memory_dir: Path,
        stream_path: Path | None = None,
        trigger_config: TriggerConfig | None = None,
    ) -> None:
        self.memory_dir = memory_dir
        self.stream = EpisodicStream(stream_path)
        self.trigger = AutonomousAutoDreamTrigger(memory_dir, trigger_config)
        self.engine = HostDreamEngine(memory_dir)
        self.recalled_cards: dict[str, str] = {}  # entity_id -> card content

    def compile_gbnf_grammar(
        self,
        base_spec: AffordanceSpec,
        known_entities: list[str],
    ) -> str:
        """Compile dynamic GBNF grammar including RECALL affordances."""
        base_gbnf = DynamicGBNFCompiler.compile(base_spec)

        if not known_entities:
            return base_gbnf

        # Build recall rule: model generates "ACTION: " followed by "RECALL <target>"
        entity_alts = " | ".join(f'"{e}"' for e in sorted(known_entities))
        recall_rule = (
            f'recall-action ::= "RECALL " valid-recall-target\n'
            f'valid-recall-target ::= {entity_alts}'
        )

        # Inject recall into action production
        if 'action ::= "ACTION: " (' in base_gbnf:
            modified_gbnf = base_gbnf.replace(
                'action ::= "ACTION: " (',
                'action ::= "ACTION: " ( recall-action |',
            )
        elif 'action ::= "ACTION: "' in base_gbnf:
            prefix = 'action ::= "ACTION: "'
            idx = base_gbnf.find(prefix) + len(prefix)
            end_line = base_gbnf.find("\n", idx)
            single_branch = base_gbnf[idx:end_line].strip()
            modified_gbnf = (
                base_gbnf[:idx]
                + f" ( recall-action | {single_branch} )"
                + base_gbnf[end_line:]
            )
        else:
            modified_gbnf = base_gbnf

        return modified_gbnf + "\n\n" + recall_rule

    def format_working_prompt(
        self,
        task_instruction: str,
        current_state_summary: str,
        recent_turns: list[str],
    ) -> str:
        """Assemble the complete working prompt with INDEX and Active Recall cards."""
        sections = [f"TASK: {task_instruction}"]

        # 1. Bounded Index Prior (<= 128 tokens)
        index_content = self.engine.get_index_content()
        if index_content:
            sections.append(f"MEMORY_INDEX:\n{index_content}")

        # 2. Active Recall Cards (<= 2 cards, <= 96 tokens)
        if self.recalled_cards:
            cards_str = "\n".join(
                f"[RECALLED: {card}]" for card in self.recalled_cards.values()
            )
            sections.append(f"RECALLED_FACTS:\n{cards_str}")

        # 3. Current Working State
        if current_state_summary:
            sections.append(f"CURRENT_STATE: {current_state_summary}")

        # 4. Recent Turn History
        if recent_turns:
            history_str = "\n".join(recent_turns)
            sections.append(f"RECENT_TURNS:\n{history_str}")

        sections.append("Provide exactly ONE action matching the grammar.")
        return "\n\n".join(sections)

    def handle_recall(self, entity_id: str) -> str | None:
        """Fetch entity card and place it into the active recall buffer."""
        card = self.engine.get_entity_card(entity_id)
        if card:
            # Maintain FIFO sliding buffer of size 2
            if len(self.recalled_cards) >= self.MAX_RECALL_BUFFER_CARDS:
                oldest_key = next(iter(self.recalled_cards))
                del self.recalled_cards[oldest_key]
            self.recalled_cards[entity_id] = card
        return card

    def record_and_evaluate(
        self,
        tick: int,
        entity_id: str,
        action_name: str,
        success: bool,
        state_delta: dict[str, Any],
        error_code: str | None,
        working_tokens: int,
    ) -> bool:
        """Record event and evaluate whether AutoDream should consolidate immediately."""
        # Record with SHA-256 provenance
        prov_hash = EventProvenance.compute_hash(state_delta or error_code or action_name)
        provenance = EventProvenance(
            event_id=f"evt_{tick}_{action_name}",
            tick=tick,
            source_channel="tool_execution",
            raw_payload_hash=prov_hash,
        )
        event = EpisodicEvent(
            event_id=f"evt_{tick}_{action_name}",
            tick=tick,
            entity_id=entity_id,
            action_name=action_name,
            success=success,
            state_delta=state_delta,
            error_code=error_code,
            provenance=provenance,
        )
        self.stream.append(event)

        # Evaluate Dual-Trigger check
        state = self.engine.lock.load_state()
        mutations = self.stream.count_mutations_since_tick(state.last_consolidated_tick)
        trig = self.trigger.evaluate(
            state=state,
            current_tick=tick,
            unconsolidated_mutations=mutations,
            current_working_tokens=working_tokens,
        )

        if trig.should_consolidate:
            # Execute Dream Cycle
            self.engine.run_dream_cycle(self.stream, current_tick=tick)
            # If emergency pressure, flush active recall buffer to free tokens
            if trig.trigger_type == TriggerType.EMERGENCY_PRESSURE:
                self.recalled_cards.clear()
            return True

        return False
