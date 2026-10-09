"""Deterministic Conflict Resolver and State Machine Replay.

Maintains ground truth: Takes an episodic event stream, replays events sequentially,
and deterministically resolves state contradictions using monotonic timestamps and
authoritative state deltas. Older superseded facts are completely purged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    from .provenance import EpisodicEvent
except ImportError:
    from provenance import EpisodicEvent


@dataclass
class EntityState:
    """Consolidated state representation for an entity."""

    entity_id: str
    status: str
    attributes: dict[str, Any] = field(default_factory=dict)
    last_updated_tick: int = 0
    causal_event_id: str = ""

    def format_card(self) -> str:
        """Format as an ultra-compact declarative Fact Card (<= 48 tokens)."""
        attrs_str = ",".join(f"{k}={v}" for k, v in sorted(self.attributes.items()))
        if attrs_str:
            return (
                f"ENTITY: {self.entity_id} | STATUS: {self.status} | "
                f"ATTRS: {attrs_str} | AT_TICK: {self.last_updated_tick}"
            )
        return (
            f"ENTITY: {self.entity_id} | STATUS: {self.status} | "
            f"AT_TICK: {self.last_updated_tick}"
        )

    def format_index_line(self) -> str:
        """Format as a single-line hook for INDEX.md (<= 16 tokens)."""
        summary = f"status={self.status}"
        if "balance" in self.attributes:
            summary += f",bal={self.attributes['balance']}"
        elif "target" in self.attributes:
            summary += f",target={self.attributes['target']}"
        return f"- [{self.entity_id}]({self.entity_id}.md): {summary} (t={self.last_updated_tick})"


class DeterministicConflictResolver:
    """Replays chronological events and builds consistent authoritative entity states."""

    @classmethod
    def resolve(
        cls,
        events: list[EpisodicEvent],
        initial_states: dict[str, EntityState] | None = None,
    ) -> dict[str, EntityState]:
        """Replay events and resolve all state transitions deterministically."""
        states: dict[str, EntityState] = {}
        if initial_states:
            for k, v in initial_states.items():
                states[k] = EntityState(
                    entity_id=v.entity_id,
                    status=v.status,
                    attributes=dict(v.attributes),
                    last_updated_tick=v.last_updated_tick,
                    causal_event_id=v.causal_event_id,
                )

        # Sort events by tick to enforce monotonic causal ordering
        sorted_events = sorted(events, key=lambda e: (e.tick, e.event_id))

        for event in sorted_events:
            entity_id = event.entity_id
            if not entity_id:
                continue

            current = states.get(entity_id)
            if current is None:
                current = EntityState(
                    entity_id=entity_id,
                    status="ACTIVE",
                    attributes={},
                    last_updated_tick=event.tick,
                    causal_event_id=event.event_id,
                )
                states[entity_id] = current

            if event.is_mutation():
                # Apply authoritative state deltas
                delta = event.state_delta
                for key, val in delta.items():
                    if key == "status":
                        current.status = str(val)
                    else:
                        current.attributes[key] = val

                current.last_updated_tick = max(current.last_updated_tick, event.tick)
                current.causal_event_id = event.event_id

        return states
