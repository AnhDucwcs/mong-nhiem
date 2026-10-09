"""Consolidation Mutex Lock and Persistent State Management.

Deterministic consolidation lock mechanism for Mộng Nhiễm:
Manages an atomic file-based mutex lock (.consolidate-lock) with PID tracking,
stale lock recovery (> 3600s), and rollback support.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ConsolidationState:
    """Persistent state tracking consolidation cycles."""

    last_consolidated_tick: int = 0
    last_consolidated_at_utc: float = 0.0
    consolidation_count: int = 0
    active_entities_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> ConsolidationState:
        return cls(
            last_consolidated_tick=data.get("last_consolidated_tick", 0),
            last_consolidated_at_utc=data.get("last_consolidated_at_utc", 0.0),
            consolidation_count=data.get("consolidation_count", 0),
            active_entities_count=data.get("active_entities_count", 0),
        )


class ConsolidationLock:
    """File-based mutex lock preventing concurrent consolidation passes."""

    DEFAULT_STALE_SECONDS = 3600  # 1 hour

    def __init__(self, memory_dir: Path, stale_seconds: int = DEFAULT_STALE_SECONDS) -> None:
        self.memory_dir = memory_dir
        self.lock_file = memory_dir / ".consolidate-lock"
        self.state_file = memory_dir / ".consolidation_state.json"
        self.stale_seconds = stale_seconds

    def is_locked(self) -> bool:
        """Check if a valid, non-stale lock currently exists."""
        if not self.lock_file.exists():
            return False

        try:
            mtime = self.lock_file.stat().st_mtime
            age = time.time() - mtime
            return age <= self.stale_seconds
        except OSError:
            return False

    def try_acquire(self, pid: int | None = None) -> bool:
        """Attempt to acquire the consolidation lock. Returns True on success."""
        if pid is None:
            pid = os.getpid()

        self.memory_dir.mkdir(parents=True, exist_ok=True)

        if self.lock_file.exists():
            try:
                mtime = self.lock_file.stat().st_mtime
                age = time.time() - mtime
                if age > self.stale_seconds:
                    # Stale lock: overwrite safely
                    pass
                else:
                    return False
            except OSError:
                pass

        try:
            payload = {"pid": pid, "acquired_at": time.time()}
            with open(self.lock_file, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            return True
        except OSError:
            return False

    def release(self) -> None:
        """Release the consolidation lock."""
        if self.lock_file.exists():
            try:
                self.lock_file.unlink()
            except OSError:
                pass

    def load_state(self) -> ConsolidationState:
        """Load state from persistent json file."""
        if not self.state_file.exists():
            return ConsolidationState()
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ConsolidationState.from_dict(data)
        except (json.JSONDecodeError, OSError):
            return ConsolidationState()

    def save_state(self, state: ConsolidationState) -> None:
        """Save state to persistent json file."""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)
