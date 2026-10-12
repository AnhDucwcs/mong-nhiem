"""Core cryptographic events and causal link models for Mộng Nhiễm."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CausalEvent:
    """Immutable hash-chained causal event emitted or committed by the host."""

    event_id: str
    tick: int
    agent_id: str
    action_type: str
    target: str
    payload: Dict[str, Any] = field(default_factory=dict)
    parent_hashes: List[str] = field(default_factory=list)
    status: str = "COMMITTED"
    signature: Optional[str] = None

    def __post_init__(self):
        if not self.signature:
            self.signature = self.compute_hash()

    def compute_hash(self) -> str:
        """Computes deterministic SHA-256 fingerprint over canonical event fields."""
        data = {
            "event_id": self.event_id,
            "tick": self.tick,
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "target": self.target,
            "payload": self.payload,
            "parent_hashes": sorted(self.parent_hashes),
            "status": self.status,
        }
        encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def verify_integrity(self) -> bool:
        """Verifies that signature matches computed SHA-256 hash."""
        return self.signature == self.compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes event to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CausalEvent:
        """Deserializes event from dictionary."""
        return cls(**data)
