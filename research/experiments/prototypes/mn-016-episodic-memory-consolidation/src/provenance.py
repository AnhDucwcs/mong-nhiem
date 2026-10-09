"""Event Provenance and Immutable Episodic Event Stream.

Enforces ground truth: Events are recorded directly from tool execution return values
and environment state transitions, accompanied by cryptographic hashes and causal links.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EventProvenance:
    """Immutable audit trail for an episodic event."""

    event_id: str
    tick: int
    source_channel: str
    raw_payload_hash: str
    causal_parent: str | None = None
    created_at_utc: float = field(default_factory=time.time)

    @staticmethod
    def compute_hash(payload: Any) -> str:
        """Compute deterministic SHA-256 hash of payload."""
        if isinstance(payload, str):
            data = payload.encode("utf-8")
        else:
            data = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(data).hexdigest()[:16]


@dataclass(frozen=True)
class EpisodicEvent:
    """A single discrete event in the episodic stream."""

    event_id: str
    tick: int
    entity_id: str
    action_name: str
    success: bool
    state_delta: dict[str, Any]
    error_code: str | None = None
    provenance: EventProvenance | None = None

    def is_mutation(self) -> bool:
        """Whether this event mutated state or produced a notable transition."""
        return self.success and bool(self.state_delta)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to serializable dictionary."""
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EpisodicEvent:
        """Reconstruct event from dictionary."""
        prov_data = data.get("provenance")
        prov = EventProvenance(**prov_data) if prov_data else None
        return cls(
            event_id=data["event_id"],
            tick=data["tick"],
            entity_id=data["entity_id"],
            action_name=data["action_name"],
            success=data["success"],
            state_delta=data.get("state_delta", {}),
            error_code=data.get("error_code"),
            provenance=prov,
        )


class EpisodicStream:
    """Append-only in-memory and disk-backed event stream with entity indexing."""

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = storage_path
        self._events: list[EpisodicEvent] = []
        self._entity_index: dict[str, list[EpisodicEvent]] = {}
        if self.storage_path and self.storage_path.exists():
            self._load_from_disk()

    def append(self, event: EpisodicEvent) -> None:
        """Append an event to the stream and update index."""
        self._events.append(event)
        self._entity_index.setdefault(event.entity_id, []).append(event)
        if self.storage_path:
            self._append_to_disk(event)

    def get_all_events(self) -> list[EpisodicEvent]:
        """Return all events chronologically."""
        return list(self._events)

    def get_events_since_tick(self, tick: int) -> list[EpisodicEvent]:
        """Return events recorded strictly after the given tick."""
        return [e for e in self._events if e.tick > tick]

    def get_events_for_entity(self, entity_id: str) -> list[EpisodicEvent]:
        """Return all events concerning a specific entity."""
        return list(self._entity_index.get(entity_id, []))

    def count_mutations_since_tick(self, tick: int) -> int:
        """Count state-mutating events since given tick."""
        return sum(1 for e in self._events if e.tick > tick and e.is_mutation())

    def __len__(self) -> int:
        return len(self._events)

    def _append_to_disk(self, event: EpisodicEvent) -> None:
        """Append a single event JSON line to disk."""
        assert self.storage_path is not None
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def _load_from_disk(self) -> None:
        """Load stream from disk JSONL file."""
        assert self.storage_path is not None
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                event = EpisodicEvent.from_dict(data)
                self._events.append(event)
                self._entity_index.setdefault(event.entity_id, []).append(event)
