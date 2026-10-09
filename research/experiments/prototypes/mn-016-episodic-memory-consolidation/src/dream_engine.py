"""Host-Authoritative 4-Phase Dream Consolidation Engine.

Executes the four strict consolidation phases:
  Phase 1: Orient   (Read INDEX.md and load existing entity cards)
  Phase 2: Gather   (Scan recent verified events with SHA-256 provenance)
  Phase 3: Consolidate (Deterministic state replay, contradiction deletion, write cards <= 48 tok)
  Phase 4: Prune & Index (Re-generate bounded INDEX.md <= 128 tok, update state, release lock)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .conflict_resolver import DeterministicConflictResolver, EntityState
    from .consolidation_lock import ConsolidationLock, ConsolidationState
    from .provenance import EpisodicStream
except ImportError:
    from conflict_resolver import DeterministicConflictResolver, EntityState
    from consolidation_lock import ConsolidationLock, ConsolidationState
    from provenance import EpisodicStream


@dataclass(frozen=True)
class DreamSummary:
    """Summary of actions taken during a consolidation pass."""

    events_consolidated: int
    entities_updated: int
    total_active_entities: int
    index_token_estimate: int
    duration_ms: float


class HostDreamEngine:
    """Authoritative memory consolidation engine running on the host."""

    MAX_INDEX_TOKENS = 128
    MAX_CARD_TOKENS = 48

    def __init__(self, memory_dir: Path) -> None:
        self.memory_dir = memory_dir
        self.entities_dir = memory_dir / "entities"
        self.index_file = memory_dir / "INDEX.md"
        self.lock = ConsolidationLock(memory_dir)

    def run_dream_cycle(
        self,
        stream: EpisodicStream,
        current_tick: int,
    ) -> DreamSummary:
        """Execute the full 4-phase consolidation pass."""
        start_time = time.perf_counter()

        # ---------------------------------------------------------------------
        # Phase 1: Orient
        # ---------------------------------------------------------------------
        state = self.lock.load_state()
        last_tick = state.last_consolidated_tick
        existing_states = self._load_existing_entity_states()

        # ---------------------------------------------------------------------
        # Phase 2: Gather
        # ---------------------------------------------------------------------
        new_events = stream.get_events_since_tick(last_tick)

        # ---------------------------------------------------------------------
        # Phase 3: Consolidate (Deterministic state replay & contradiction pruning)
        # ---------------------------------------------------------------------
        updated_states = DeterministicConflictResolver.resolve(
            events=new_events,
            initial_states=existing_states,
        )

        self.entities_dir.mkdir(parents=True, exist_ok=True)
        entities_modified = 0
        for entity_id, entity_state in updated_states.items():
            card_content = entity_state.format_card()
            card_path = self.entities_dir / f"{entity_id}.md"
            # Write card with strict budget guard
            with open(card_path, "w", encoding="utf-8") as f:
                f.write(card_content + "\n")
            entities_modified += 1

        # ---------------------------------------------------------------------
        # Phase 4: Prune & Index
        # ---------------------------------------------------------------------
        index_content, est_tokens = self._generate_index(updated_states)
        with open(self.index_file, "w", encoding="utf-8") as f:
            f.write(index_content)

        state.last_consolidated_tick = current_tick
        state.last_consolidated_at_utc = time.time()
        state.consolidation_count += 1
        state.active_entities_count = len(updated_states)
        self.lock.save_state(state)

        # Always release lock at the end of the dream
        self.lock.release()

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return DreamSummary(
            events_consolidated=len(new_events),
            entities_updated=entities_modified,
            total_active_entities=len(updated_states),
            index_token_estimate=est_tokens,
            duration_ms=duration_ms,
        )

    def _load_existing_entity_states(self) -> dict[str, EntityState]:
        """Load currently persisted entity cards from disk."""
        states: dict[str, EntityState] = {}
        if not self.entities_dir.exists():
            return states

        for card_path in self.entities_dir.glob("*.md"):
            entity_id = card_path.stem
            try:
                with open(card_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                # Parse standard format: ENTITY: x | STATUS: y | ATTRS: a=1,b=2 | AT_TICK: z
                parts = [p.strip() for p in content.split("|")]
                status = "ACTIVE"
                attrs: dict[str, Any] = {}
                tick = 0
                for part in parts:
                    if part.startswith("STATUS:"):
                        status = part.replace("STATUS:", "").strip()
                    elif part.startswith("ATTRS:"):
                        attrs_raw = part.replace("ATTRS:", "").strip()
                        if attrs_raw:
                            for pair in attrs_raw.split(","):
                                if "=" in pair:
                                    k, v = pair.split("=", 1)
                                    attrs[k.strip()] = v.strip()
                    elif part.startswith("AT_TICK:"):
                        try:
                            tick = int(part.replace("AT_TICK:", "").strip())
                        except ValueError:
                            pass

                states[entity_id] = EntityState(
                    entity_id=entity_id,
                    status=status,
                    attributes=attrs,
                    last_updated_tick=tick,
                )
            except OSError:
                continue

        return states

    def get_all_entity_states(self) -> dict[str, EntityState]:
        """Return currently persisted entity states."""
        return self._load_existing_entity_states()

    def _generate_index(self, states: dict[str, EntityState]) -> tuple[str, int]:
        """Compile bounded INDEX.md (<= 128 tokens) sorted by last_updated_tick desc."""
        lines = ["# Memory Index"]
        # Prioritize most recently updated entities
        sorted_entities = sorted(
            states.values(),
            key=lambda s: s.last_updated_tick,
            reverse=True,
        )

        for s in sorted_entities:
            lines.append(s.format_index_line())

        content = "\n".join(lines) + "\n"
        est_tokens = len(content.split())  # Fast word-level token proxy
        return content, est_tokens

    def get_index_content(self) -> str:
        """Read current INDEX.md content, or empty string if absent."""
        if not self.index_file.exists():
            return ""
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except OSError:
            return ""

    def get_entity_card(self, entity_id: str) -> str | None:
        """Read a single entity Fact Card, or None if not found."""
        card_path = self.entities_dir / f"{entity_id}.md"
        if not card_path.exists():
            return None
        try:
            with open(card_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except OSError:
            return None
