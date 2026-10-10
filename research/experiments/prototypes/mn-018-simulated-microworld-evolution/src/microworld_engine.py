"""Host-Authoritative Simulated Microworld Engine with Conservation Law Invariants.

Provides multi-rate simulation clocks, physical conservation law validation,
environmental decay drift, scheduled shocks, and optimistic concurrency versioning.
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

    def render_fact_card(self, compact: bool = False) -> str:
        """Render compact Fact Card strictly bounded to <= 48 tokens.
        
        Args:
            compact: If True, format as high-density representation for AutoDream memory.
        """
        if compact:
            props = []
            for k, v in sorted(self.properties.items()):
                if isinstance(v, float):
                    v_str = f"{v:.1f}".rstrip('0').rstrip('.')
                else:
                    v_str = str(v)
                props.append(f"{k}:{v_str}")
            props_str = " ".join(props)
            exp_str = " EXPIRED" if self.is_expired() else ""
            return f"[{self.entity_id} v{self.version}{exp_str} {props_str}]"
        status = "ACTIVE" if not self.is_expired() else "EXPIRED"
        props_str = " ".join(f"{k}={v}" for k, v in sorted(self.properties.items()))
        ttl_str = f" ttl={self.ttl}" if self.ttl is not None else ""
        return f"[ENTITY {self.entity_id}:{self.entity_type} v{self.version} {status}{ttl_str} {props_str}]"


class ConservationGuard:
    """Host-authoritative physical conservation law and state invariant validator."""

    @staticmethod
    def validate_invariants(
        entities: Dict[str, WorldEntity],
        domain: str,
        nominal_constants: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """Verify that world state preserves physical and logical invariants.
        
        Args:
            entities: Current world entity dictionary.
            domain: Domain identifier ('orbital_station', 'industrial_microgrid', 'fleet_supply_chain').
            nominal_constants: Dictionary of nominal physical conservation constants.
            
        Returns:
            (is_valid, failure_reason)
        """
        # Generic Non-Negativity Check
        for eid, entity in entities.items():
            for prop, val in entity.properties.items():
                if isinstance(val, (int, float)):
                    if prop in ("inventory", "payload", "battery", "soc", "pressure", "oxygen", "coolant", "stored_energy"):
                        if val < 0.0:
                            return False, f"INVARIANT_BREACH: Entity '{eid}' has negative physical value for '{prop}': {val}"

        if domain == "orbital_station":
            # Domain A: Autonomous Orbital Station Life Support
            # Invariant A1: Total Energy >= 0
            power_bus = entities.get("power_bus")
            if power_bus:
                stored = power_bus.properties.get("stored_kwh", 0.0)
                if stored < 0.0:
                    return False, f"CONSERVATION_BREACH: Power bus stored energy depleted below zero: {stored} kWh"

            # Invariant A2: Oxygen fraction in [19.5, 23.5]%
            life_support = entities.get("life_support")
            if life_support:
                o2 = life_support.properties.get("o2_percent", 21.0)
                if o2 < 19.5 or o2 > 23.5:
                    return False, f"CONSERVATION_BREACH: Atmospheric O2 fraction out of safe bounds [19.5, 23.5]%: {o2}%"
                
                pressure = life_support.properties.get("pressure_kpa", 101.3)
                if pressure < 95.0:
                    return False, f"CONSERVATION_BREACH: Cabin atmospheric pressure breached minimum 95.0 kPa: {pressure} kPa"

            # Invariant A3: Total coolant volume conserved
            nominal_coolant = nominal_constants.get("nominal_coolant_liters")
            if nominal_coolant is not None:
                loop_a = entities.get("coolant_loop_a")
                loop_b = entities.get("coolant_loop_b")
                reserve = entities.get("coolant_reserve")
                if loop_a and loop_b and reserve:
                    total_coolant = (
                        loop_a.properties.get("volume_liters", 0.0)
                        + loop_b.properties.get("volume_liters", 0.0)
                        + reserve.properties.get("volume_liters", 0.0)
                    )
                    if round(total_coolant, 1) != round(nominal_coolant, 1):
                        return False, f"CONSERVATION_BREACH: Total coolant volume mismatch: {total_coolant} L != {nominal_coolant} L"

        elif domain == "industrial_microgrid":
            # Domain B: Smart Industrial Microgrid & Storage
            # Invariant B1: Critical hospital load uninterrupted
            hosp = entities.get("hospital_ward")
            if hosp:
                supplied = hosp.properties.get("power_kw", 0.0)
                required = hosp.properties.get("min_required_kw", 50.0)
                if supplied < required:
                    return False, f"CONSERVATION_BREACH: Critical hospital power dropped below required {required} kW: {supplied} kW"

            # Invariant B2: Battery SOC in [0.0, 100.0]%
            bess = entities.get("bess_unit")
            if bess:
                soc = bess.properties.get("soc_percent", 50.0)
                if soc < 0.0 or soc > 100.0:
                    return False, f"CONSERVATION_BREACH: Battery SOC out of physical limits [0.0, 100.0]%: {soc}%"

            # Invariant B3: Energy balance: Generation == Load + Battery Net Flow
            grid = entities.get("grid_controller")
            if grid:
                gen_kw = grid.properties.get("generation_kw", 0.0)
                load_kw = grid.properties.get("load_kw", 0.0)
                net_battery_kw = grid.properties.get("battery_net_kw", 0.0)  # positive = charging, negative = discharging
                imbalance = abs(gen_kw - (load_kw + net_battery_kw))
                if imbalance > 1.0:  # Allow 1.0 kW tolerance for numerical roundoff
                    return False, f"CONSERVATION_BREACH: Microgrid energy balance violated: Gen={gen_kw} kW != Load+Battery={load_kw + net_battery_kw} kW (imbalance={imbalance})"

        elif domain == "fleet_supply_chain":
            # Domain C: Multi-Hub Autonomous Fleet Supply Chain
            # Invariant C1: Drone payload <= max capacity and battery >= 0
            for eid, ent in entities.items():
                if ent.entity_type == "drone":
                    payload = ent.properties.get("payload_units", 0)
                    max_cap = ent.properties.get("max_capacity", 5)
                    battery = ent.properties.get("battery_percent", 100.0)
                    if payload > max_cap:
                        return False, f"CONSERVATION_BREACH: Drone '{eid}' payload exceeds capacity: {payload} > {max_cap}"
                    if battery < 0.0:
                        return False, f"CONSERVATION_BREACH: Drone '{eid}' battery depleted below zero: {battery}%"

            # Invariant C2: Total inventory conserved (Hubs + In-transit Drones)
            nominal_inv = nominal_constants.get("nominal_total_inventory")
            if nominal_inv is not None:
                current_total = 0
                for eid, ent in entities.items():
                    if ent.entity_type == "hub":
                        current_total += ent.properties.get("inventory_units", 0)
                    elif ent.entity_type == "drone":
                        current_total += ent.properties.get("payload_units", 0)
                if current_total != nominal_inv:
                    return False, f"CONSERVATION_BREACH: Total fleet inventory conserved violation: {current_total} != nominal {nominal_inv}"

        return True, None


@dataclass
class ScheduledEvent:
    """A deterministic scheduled background event triggering at an explicit tick."""
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


class MicroworldEngine:
    """Host-authoritative world engine executing physics, dynamics, and conservation checks."""

    def __init__(
        self,
        domain: str = "orbital_station",
        nominal_constants: Optional[Dict[str, Any]] = None,
        start_tick: int = 0,
    ) -> None:
        self.domain = domain
        self.nominal_constants = nominal_constants or {}
        self.clock = WorldClock(start_tick=start_tick)
        self.entities: Dict[str, WorldEntity] = {}
        self.scheduled_events: List[ScheduledEvent] = []
        self.event_log: List[Dict[str, Any]] = []

    def register_entity(self, entity: WorldEntity) -> None:
        """Register or overwrite a world entity."""
        self.entities[entity.entity_id] = copy.deepcopy(entity)

    def schedule_event(
        self,
        trigger_tick: int,
        event_name: str,
        mutation_fn: Callable[[Dict[str, WorldEntity]], str],
    ) -> None:
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

    def create_snapshot(self) -> Dict[str, Any]:
        """Create a deep snapshot of world state for Memento checkpoints."""
        return {
            "tick": self.clock.current_tick,
            "entities": copy.deepcopy(self.entities),
            "scheduled_events": copy.deepcopy(self.scheduled_events),
            "event_log_len": len(self.event_log),
        }

    def restore_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Restore world state from a Memento snapshot."""
        self.clock._current_tick = snapshot["tick"]
        self.entities = copy.deepcopy(snapshot["entities"])
        self.scheduled_events = copy.deepcopy(snapshot["scheduled_events"])
        self.event_log = self.event_log[:snapshot["event_log_len"]]

    def step_ticks(self, delta_ticks: int = 1) -> List[str]:
        """Advance world clock and execute all asynchronous environmental state changes.
        
        Returns:
            List of event notification strings emitted during this tick advance.
        """
        emitted_events: List[str] = []

        for _ in range(delta_ticks):
            tick = self.clock.advance(1)

            # 1. Decay TTLs and continuous rates of decay
            for entity_id, entity in list(self.entities.items()):
                mutated = False

                # TTL check
                if entity.ttl is not None and entity.ttl > 0:
                    entity.ttl -= 1
                    if entity.ttl == 0:
                        entity.is_active = False
                        entity.properties["status"] = "EXPIRED"
                        mutated = True
                        emitted_events.append(f"TICK {tick}: Entity '{entity_id}' TTL expired.")

                # Continuous decay properties
                for prop_name, decay_amount in entity.rate_of_decay.items():
                    if prop_name in entity.properties and isinstance(entity.properties[prop_name], (int, float)):
                        old_val = entity.properties[prop_name]
                        new_val = max(0.0, old_val + decay_amount)
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
                    emitted_events.append(f"TICK {tick}: Background event '{event.event_name}' occurred: {desc}")

        if emitted_events:
            self.event_log.append({
                "tick": self.clock.current_tick,
                "delta": delta_ticks,
                "events": emitted_events,
            })

        return emitted_events

    def apply_transaction(
        self,
        mutations: Dict[str, Dict[str, Any]],
        expected_versions: Optional[Dict[str, int]] = None,
    ) -> Tuple[bool, str, Dict[str, int]]:
        """Apply an atomic multi-entity transaction with concurrency and conservation checks.
        
        Args:
            mutations: Dict mapping entity_id to dict of property updates.
            expected_versions: Optional dict mapping entity_id to expected observed version.
            
        Returns:
            (success, message, new_versions_dict)
        """
        # 1. Verify existence and concurrency for all touched entities
        for eid in mutations:
            ent = self.entities.get(eid)
            if ent is None:
                return False, f"Entity '{eid}' not found.", {}
            if expected_versions and eid in expected_versions:
                exp_v = expected_versions[eid]
                if exp_v is not None and ent.version != exp_v:
                    return (
                        False,
                        f"STALE_VERSION_MISMATCH: Target entity '{eid}' is at v{ent.version}, but action was planned against v{exp_v}.",
                        {},
                    )
            if ent.is_expired():
                return False, f"ILLEGAL_MUTATION: Entity '{eid}' is expired/inactive.", {}

        # 2. Trial mutation on deepcopy to verify physical conservation laws
        trial_entities = copy.deepcopy(self.entities)
        for eid, updates in mutations.items():
            t_ent = trial_entities[eid]
            for k, v in updates.items():
                if k == "ttl":
                    t_ent.ttl = v
                    if v and v > 0:
                        t_ent.is_active = True
                elif k == "is_active":
                    t_ent.is_active = bool(v)
                else:
                    t_ent.properties[k] = v

        valid, err_msg = ConservationGuard.validate_invariants(
            entities=trial_entities,
            domain=self.domain,
            nominal_constants=self.nominal_constants,
        )
        if not valid:
            return False, err_msg or "CONSERVATION_LAW_BREACH", {}

        # 3. Commit mutations
        new_versions: Dict[str, int] = {}
        for eid, updates in mutations.items():
            ent = self.entities[eid]
            for k, v in updates.items():
                if k == "ttl":
                    ent.ttl = v
                    if v and v > 0:
                        ent.is_active = True
                elif k == "is_active":
                    ent.is_active = bool(v)
                else:
                    ent.properties[k] = v
            ent.version += 1
            new_versions[eid] = ent.version

        return True, "Transaction committed successfully.", new_versions

    def mutate_entity(
        self,
        entity_id: str,
        updates: Dict[str, Any],
        expected_version: Optional[int] = None,
    ) -> Tuple[bool, str, int]:
        """Apply a single entity state mutation."""
        exp_dict = {entity_id: expected_version} if expected_version is not None else None
        success, msg, v_dict = self.apply_transaction({entity_id: updates}, exp_dict)
        return success, msg, v_dict.get(entity_id, self.entities.get(entity_id, WorldEntity(entity_id, "")).version)
