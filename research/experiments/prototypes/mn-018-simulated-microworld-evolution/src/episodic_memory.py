"""Append-Only Episodic Event Store with SHA-256 Provenance Chaining.

Enforces ground-truth auditability: every state transition, telemetry shock,
and agent action is hashed and cryptographically linked to its parent event.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EpisodicEvent:
    """A discrete episodic event in the microworld timeline."""
    event_id: str
    tick: int
    entity_id: str
    action_name: str
    status: str
    details: Dict[str, Any]
    prev_hash: str
    event_hash: str = ""
    timestamp_utc: float = field(default_factory=time.time)

    def compute_hash(self) -> str:
        """Compute SHA-256 hash linking this event to the preceding event."""
        payload = {
            "event_id": self.event_id,
            "tick": self.tick,
            "entity_id": self.entity_id,
            "action_name": self.action_name,
            "status": self.status,
            "details": self.details,
            "prev_hash": self.prev_hash,
        }
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()[:16]


class EpisodicLog:
    """Append-only cryptographic event store for microworld transitions."""

    def __init__(self) -> None:
        self.events: List[EpisodicEvent] = []
        self.last_hash: str = "GENESIS_00000000"
        self.last_consolidated_index: int = 0

    def append(
        self,
        tick: int,
        entity_id: str,
        action_name: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> EpisodicEvent:
        """Create and append an event to the cryptographic chain."""
        details_dict = details or {}
        event_id = f"evt_{len(self.events) + 1:04d}"
        event = EpisodicEvent(
            event_id=event_id,
            tick=tick,
            entity_id=entity_id,
            action_name=action_name,
            status=status,
            details=details_dict,
            prev_hash=self.last_hash,
        )
        event.event_hash = event.compute_hash()
        self.last_hash = event.event_hash
        self.events.append(event)
        return event

    def get_unconsolidated_events(self) -> List[EpisodicEvent]:
        """Return all events appended since the last AutoDream consolidation pass."""
        return self.events[self.last_consolidated_index:]

    def mark_consolidated(self) -> None:
        """Advance consolidation watermark to the end of the current log."""
        self.last_consolidated_index = len(self.events)

    def estimate_raw_tokens(self, events: Optional[List[EpisodicEvent]] = None) -> int:
        """Estimate token footprint of raw event representation (approx 4 chars per token)."""
        target_events = events if events is not None else self.events
        total_chars = 0
        for e in target_events:
            total_chars += len(f"TICK {e.tick} [{e.event_id}] {e.entity_id} {e.action_name} {e.status}: {json.dumps(e.details)}\n")
        return max(1, total_chars // 4)
