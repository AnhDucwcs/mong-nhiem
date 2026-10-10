"""Concurrency Guard and Stale-State Invariant Reconciliation.

Prevents stale-state overwrites caused by independent background World Ticks,
detects version drift between agent working context and Host state store,
and generates compact delta refresh notices (<= 64 tokens).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from microworld_engine import MicroworldEngine, WorldEntity


@dataclass
class VersionSnapshot:
    """Snapshot of entity version at the moment it was provided to agent context."""
    entity_id: str
    read_version: int
    read_tick: int


class ConcurrencyGuard:
    """Host-side concurrency inspector validating optimistic version constraints."""

    def __init__(self) -> None:
        self.observed_versions: Dict[str, VersionSnapshot] = {}
        self.stale_violations_intercepted: int = 0
        self.stale_overwrites_committed: int = 0  # Only increments if guard is bypassed (e.g. Arm 1/2)

    def record_observation(self, entity_id: str, version: int, tick: int) -> None:
        """Record the version of an entity presented to agent working memory."""
        self.observed_versions[entity_id] = VersionSnapshot(
            entity_id=entity_id,
            read_version=version,
            read_tick=tick,
        )

    def validate_action(
        self,
        entity_id: str,
        engine: MicroworldEngine,
        enforce_guard: bool = True,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate whether an action targeting entity_id is safe or stale.
        
        Args:
            entity_id: Target entity identifier.
            engine: Current dynamic world engine.
            enforce_guard: If True (Arm 3), intercepts stale mutations. If False (Arm 1/2), allows stale overwrite.
            
        Returns:
            (is_allowed, error_code, delta_notice)
        """
        current_entity = engine.get_entity(entity_id)
        if current_entity is None:
            return False, "ENTITY_NOT_FOUND", f"[ERROR: Entity '{entity_id}' does not exist.]"

        snapshot = self.observed_versions.get(entity_id)

        # If never observed, consider unobserved
        if snapshot is None:
            return True, None, None

        # Check if world has mutated since observation
        if current_entity.version > snapshot.read_version:
            if enforce_guard:
                self.stale_violations_intercepted += 1
                fresh_card = current_entity.render_fact_card()
                notice = (
                    f"[DELTA NOTICE: Entity '{entity_id}' mutated at tick {engine.clock.current_tick} "
                    f"(was v{snapshot.read_version}, now v{current_entity.version}). "
                    f"Updated: {fresh_card}]"
                )
                self.record_observation(entity_id, current_entity.version, engine.clock.current_tick)
                return False, "STALE_VERSION_INTERCEPTED", notice
            else:
                self.stale_overwrites_committed += 1
                return True, "STALE_OVERWRITE_PERMITTED", None

        # Check if entity expired in the interim
        if current_entity.is_expired():
            if enforce_guard:
                self.stale_violations_intercepted += 1
                notice = f"[DELTA NOTICE: Entity '{entity_id}' lease expired. Current status: EXPIRED.]"
                return False, "ENTITY_EXPIRED", notice
            else:
                self.stale_overwrites_committed += 1
                return True, "MUTATE_EXPIRED_PERMITTED", None

        return True, None, None
