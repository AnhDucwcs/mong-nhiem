"""Host-Authoritative World Clock and Dynamic Environmental Tick Engine.

Provides independent, multi-rate simulation clocks, monotonic entity versioning,
TTL expiration, and rate-of-decay mutators operating asynchronously from agent turns.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class WorldEntity:
    """State representation of a world entity with monotonic version tracking."""
    entity_id: str
    entity_type: str
    version: int = 1
    properties: Dict[str, Any] = field(default_factory=dict)
    ttl: Optional[int] = None
    rate_of_decay: Dict[str, float] = field(default_factory=dict)
    is_active: bool = True

    def is_expired(self) -> bool:
        """Check whether entity lease or existence has expired."""
        if self.ttl is not None and self.ttl <= 0:
            return True
        return not self.is_active

    def render_fact_card(self) -> str:
        """Render compact Fact Card strictly bounded to <= 48 tokens."""
        status = "ACTIVE" if not self.is_expired() else "EXPIRED"
        props_str = " ".join(f"{k}={v}" for k, v in sorted(self.properties.items()))
        ttl_str = f" ttl={self.ttl}" if self.ttl is not None else ""
        return f"[ENTITY {self.entity_id}:{self.entity_type} v{self.version} {status}{ttl_str} {props_str}]"


@dataclass
class ScheduledEvent:
    """A deterministic scheduled background event triggering at a specific tick."""
    trigger_tick: int
    event_name: str
    mutation_fn: Callable[[Dict[str, WorldEntity]], str]
    executed: bool = False


class WorldClock:
    """Manages discrete simulation time in integer ticks."""

    def __init__(self, start_tick: int = 0) -> None:
        self._current_tick: int = start_tick

    @property
    def current_tick(self) -> int:
        return self._current_tick

    def advance(self, delta_ticks: int = 1) -> int:
        if delta_ticks < 0:
            raise ValueError(f"Cannot rewind world clock: delta={delta_ticks}")
        self._current_tick += delta_ticks
        return self._current_tick


class DynamicWorldEngine:
    """Host-authoritative world engine executing background simulation dynamics."""

    def __init__(self, start_tick: int = 0) -> None:
        self.clock = WorldClock(start_tick=start_tick)
        self.entities: Dict[str, WorldEntity] = {}
        self.scheduled_events: List[ScheduledEvent] = []
        self.event_log: List[Dict[str, Any]] = []

    def register_entity(self, entity: WorldEntity) -> None:
        """Register or overwrite a world entity."""
        self.entities[entity.entity_id] = copy.deepcopy(entity)

    def schedule_event(self, trigger_tick: int, event_name: str, mutation_fn: Callable[[Dict[str, WorldEntity]], str]) -> None:
        """Schedule a background world transition at an explicit tick."""
        self.scheduled_events.append(ScheduledEvent(
            trigger_tick=trigger_tick,
            event_name=event_name,
            mutation_fn=mutation_fn,
        ))

    def get_entity(self, entity_id: str) -> Optional[WorldEntity]:
        """Retrieve copy of an entity."""
        entity = self.entities.get(entity_id)
        if entity is None:
            return None
        return copy.deepcopy(entity)

    def step_ticks(self, delta_ticks: int = 1) -> List[str]:
        """Advance world clock and execute all asynchronous environmental state changes.
        
        Returns:
            List of event notification strings emitted during this tick jump.
        """
        emitted_events: List[str] = []
        
        for _ in range(delta_ticks):
            tick = self.clock.advance(1)
            
            # 1. Decay TTLs and rate-of-decay properties
            for entity_id, entity in list(self.entities.items()):
                mutated = False
                
                # Check TTL decay
                if entity.ttl is not None and entity.ttl > 0:
                    entity.ttl -= 1
                    if entity.ttl == 0:
                        entity.is_active = False
                        entity.properties["status"] = "EXPIRED"
                        mutated = True
                        emitted_events.append(f"TICK {tick}: Entity '{entity_id}' TTL expired.")
                
                # Check rate of decay
                for prop_name, decay_amount in entity.rate_of_decay.items():
                    if prop_name in entity.properties and isinstance(entity.properties[prop_name], (int, float)):
                        old_val = entity.properties[prop_name]
                        new_val = max(0.0, old_val + decay_amount)  # decay_amount can be negative
                        entity.properties[prop_name] = round(new_val, 2)
                        mutated = True
                        if old_val > 0.0 and new_val == 0.0:
                            emitted_events.append(f"TICK {tick}: Entity '{entity_id}' property '{prop_name}' depleted to 0.")
                
                if mutated:
                    entity.version += 1

            # 2. Execute scheduled events for this tick
            for event in self.scheduled_events:
                if not event.executed and event.trigger_tick == tick:
                    desc = event.mutation_fn(self.entities)
                    event.executed = True
                    emitted_events.append(f"TICK {tick}: Event '{event.event_name}' executed. {desc}")
        
        # Log background tick events
        if emitted_events:
            self.event_log.append({
                "tick": self.clock.current_tick,
                "delta": delta_ticks,
                "events": emitted_events,
            })
            
        return emitted_events

    def mutate_entity(
        self,
        entity_id: str,
        updates: Dict[str, Any],
        expected_version: Optional[int] = None,
    ) -> Tuple[bool, str, int]:
        """Apply a state mutation from an agent action with optimistic concurrency check.
        
        Args:
            entity_id: Target entity identifier.
            updates: Dictionary of property updates.
            expected_version: The version the agent observed before planning.
            
        Returns:
            (success, message, current_version)
        """
        entity = self.entities.get(entity_id)
        if entity is None:
            return False, f"Entity '{entity_id}' not found.", 0
        
        # Concurrency verification
        if expected_version is not None and entity.version != expected_version:
            return (
                False,
                f"STALE_VERSION_MISMATCH: Target entity '{entity_id}' is at v{entity.version}, but action was planned against v{expected_version}.",
                entity.version,
            )
        
        if entity.is_expired():
            return False, f"ILLEGAL_MUTATION: Entity '{entity_id}' is expired/inactive.", entity.version
        
        # Apply updates
        for k, v in updates.items():
            if k == "ttl":
                entity.ttl = v
                if v and v > 0:
                    entity.is_active = True
            elif k == "is_active":
                entity.is_active = bool(v)
            else:
                entity.properties[k] = v
        
        entity.version += 1
        return True, f"Entity '{entity_id}' updated successfully.", entity.version
