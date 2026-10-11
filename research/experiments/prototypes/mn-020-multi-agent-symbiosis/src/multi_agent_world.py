"""Shared Multi-Agent Microworld Engine with Physical Conservation Invariants."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class WorldEntity:
    entity_id: str
    entity_type: str
    properties: Dict[str, Any]
    relations: Dict[str, str] = field(default_factory=dict)
    version: int = 1
    is_active: bool = True

    def render_card(self, holder_id: Optional[str] = None) -> str:
        """Render compact declarative Fact Card (<= 32 tokens)."""
        prop_str = " ".join(f"{k}={v}" if isinstance(v, (int, str)) else f"{k}={v:.1f}" for k, v in sorted(self.properties.items()))
        lease_str = f" [LEASE:{holder_id}]" if holder_id else ""
        return f"[ENTITY {self.entity_id}:{self.entity_type} v{self.version} {prop_str}{lease_str}]"


class MultiAgentMicroworld:
    """Stateful shared microworld supporting concurrent agent interactions."""

    def __init__(
        self,
        domain: str,
        initial_entities: Dict[str, Dict[str, Any]],
        invariants: Optional[Dict[str, Any]] = None,
    ):
        self.domain = domain
        self.tick = 0
        self.invariants = invariants or {}
        self.entities: Dict[str, WorldEntity] = {}
        self.history_states: List[Dict[str, Any]] = []

        for eid, edata in initial_entities.items():
            self.entities[eid] = WorldEntity(
                entity_id=eid,
                entity_type=edata.get("entity_type", "generic"),
                properties=copy.deepcopy(edata.get("properties", {})),
                relations=copy.deepcopy(edata.get("relations", {})),
                version=1,
                is_active=True,
            )

    def get_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Return deepcopy of all active entity properties."""
        return {
            eid: {
                "entity_type": e.entity_type,
                "properties": copy.deepcopy(e.properties),
                "version": e.version,
                "is_active": e.is_active,
            }
            for eid, e in self.entities.items()
        }

    def dispatch_action(
        self,
        actor_id: str,
        action_str: str,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute action modifying shared microworld state.
        
        Returns:
            Tuple of (success: bool, status_message: str, delta_signature: dict)
        """
        parts = action_str.strip().split()
        if not parts:
            return False, "EMPTY_ACTION", {}

        verb = parts[0]
        pre_props = {eid: copy.deepcopy(e.properties) for eid, e in self.entities.items()}

        # Domain A: Collaborative Microgrid Balancing
        if self.domain == "collaborative_microgrid":
            if verb == "regulate_wind_pitch":
                target_pitch = float(parts[1]) if len(parts) > 1 else 30.0
                gen = self.entities.get("wind_turbine")
                bus = self.entities.get("critical_bus")
                if gen and bus:
                    gen.properties["pitch_deg"] = target_pitch
                    # Output kw drops as pitch increases (feathering)
                    gen.properties["output_kw"] = max(0.0, 100.0 - target_pitch * 1.5)
                    bus.properties["voltage"] = 320.0 + (gen.properties["output_kw"] * 0.4)
                    gen.version += 1
                    bus.version += 1

            elif verb == "charge_battery_storage":
                rate = float(parts[1]) if len(parts) > 1 else 25.0
                bat = self.entities.get("battery_bank")
                bus = self.entities.get("critical_bus")
                if bat and bus:
                    bat.properties["soc"] = min(100.0, bat.properties.get("soc", 50.0) + rate * 0.5)
                    bat.properties["charge_rate"] = rate
                    bus.properties["voltage"] = max(300.0, bus.properties.get("voltage", 340.0) - rate * 0.3)
                    bat.version += 1
                    bus.version += 1

            elif verb == "discharge_battery_storage":
                rate = float(parts[1]) if len(parts) > 1 else 30.0
                bat = self.entities.get("battery_bank")
                bus = self.entities.get("critical_bus")
                if bat and bus:
                    bat.properties["soc"] = max(0.0, bat.properties.get("soc", 50.0) - rate * 0.5)
                    bat.properties["charge_rate"] = -rate
                    bus.properties["voltage"] = min(420.0, bus.properties.get("voltage", 340.0) + rate * 0.4)
                    bat.version += 1
                    bus.version += 1

            elif verb == "shed_industrial_feeder":
                load = float(parts[1]) if len(parts) > 1 else 40.0
                feeder = self.entities.get("industrial_feeder")
                bus = self.entities.get("critical_bus")
                if feeder and bus:
                    feeder.properties["load_kw"] = max(0.0, feeder.properties.get("load_kw", 80.0) - load)
                    bus.properties["voltage"] = min(380.0, bus.properties.get("voltage", 330.0) + load * 0.2)
                    feeder.version += 1
                    bus.version += 1

            elif verb == "engage_static_compensator":
                bus = self.entities.get("critical_bus")
                comp = self.entities.get("statcom")
                if bus and comp:
                    bus.properties["voltage"] = 340.0  # Ideal target voltage
                    comp.properties["is_engaged"] = True
                    bus.version += 1
                    comp.version += 1

        # Domain B: Concurrent Orbital Maintenance
        elif self.domain == "concurrent_orbital_maintenance":
            if verb == "fire_rcs_attitude":
                pulse = float(parts[1]) if len(parts) > 1 else 10.0
                rcs = self.entities.get("rcs_thruster")
                attitude = self.entities.get("docking_adapter")
                if rcs and attitude:
                    rcs.properties["fuel_kg"] = max(0.0, rcs.properties.get("fuel_kg", 50.0) - pulse * 0.2)
                    attitude.properties["alignment_err_deg"] = max(0.0, attitude.properties.get("alignment_err_deg", 15.0) - pulse * 0.5)
                    rcs.version += 1
                    attitude.version += 1

            elif verb == "align_solar_gimbal":
                angle = float(parts[1]) if len(parts) > 1 else 45.0
                array = self.entities.get("solar_array")
                power = self.entities.get("power_bus")
                if array and power:
                    array.properties["gimbal_deg"] = angle
                    array.properties["efficiency"] = 0.95
                    power.properties["bus_power_kw"] = 45.0
                    array.version += 1
                    power.version += 1

            elif verb == "purge_coolant_loop":
                temp_drop = float(parts[1]) if len(parts) > 1 else 20.0
                thermal = self.entities.get("thermal_radiator")
                if thermal:
                    thermal.properties["temp_c"] = max(20.0, thermal.properties.get("temp_c", 65.0) - temp_drop)
                    thermal.version += 1

            elif verb == "lock_docking_latch":
                dock = self.entities.get("docking_adapter")
                if dock:
                    if dock.properties.get("alignment_err_deg", 0.0) > 2.0:
                        return False, "CONSERVATION_BREACH: DOCKING_LATCH_SHEAR_JAM", {}
                    dock.properties["is_locked"] = True
                    dock.version += 1

        # Domain C: Joint Fleet Logistics
        elif self.domain == "joint_fleet_logistics":
            if verb == "route_haul_convoy":
                dist = float(parts[1]) if len(parts) > 1 else 30.0
                convoy = self.entities.get("convoy_a")
                if convoy:
                    convoy.properties["dist_km"] = convoy.properties.get("dist_km", 0.0) + dist
                    convoy.properties["battery_soc"] = max(0.0, convoy.properties.get("battery_soc", 80.0) - dist * 0.5)
                    convoy.version += 1

            elif verb == "refrigerate_cargo_bay":
                target_t = float(parts[1]) if len(parts) > 1 else -18.0
                reefer = self.entities.get("reefer_b")
                if reefer:
                    reefer.properties["temp_c"] = target_t
                    reefer.version += 1

            elif verb == "queue_fast_charger":
                charge_kw = float(parts[1]) if len(parts) > 1 else 120.0
                hub = self.entities.get("charging_hub")
                if hub:
                    new_load = hub.properties.get("active_load_kw", 0.0) + charge_kw
                    if new_load > 200.0:
                        return False, "CONSERVATION_BREACH: GRID_TRANSFORMER_BLOWOUT", {}
                    hub.properties["active_load_kw"] = new_load
                    hub.version += 1

        # Verify Conservation Invariants
        breach = self._check_invariants()
        if breach:
            # Rollback state
            for eid, props in pre_props.items():
                self.entities[eid].properties = props
            return False, f"CONSERVATION_BREACH: {breach}", {}

        # Compute Delta Signature
        delta = {}
        for eid, ent in self.entities.items():
            pre = pre_props.get(eid, {})
            post = ent.properties
            diff = {}
            for k, v in post.items():
                if pre.get(k) != v:
                    diff[k] = {"from": pre.get(k), "to": v}
            if diff:
                delta[eid] = diff

        return True, "SUCCESS", delta

    def _check_invariants(self) -> Optional[str]:
        """Check domain physical bounds (e.g. voltage limits, zero fuel floor)."""
        if self.domain == "collaborative_microgrid":
            bus = self.entities.get("critical_bus")
            if bus and bus.properties.get("voltage", 340.0) > 400.0:
                return "OVERVOLTAGE_SURGE_THRESHOLD_EXCEEDED"
            bat = self.entities.get("battery_bank")
            if bat and bat.properties.get("soc", 50.0) < 5.0:
                return "BATTERY_DEEP_DISCHARGE_PERMANENT_DAMAGE"

        elif self.domain == "concurrent_orbital_maintenance":
            rcs = self.entities.get("rcs_thruster")
            if rcs and rcs.properties.get("fuel_kg", 50.0) < 0.0:
                return "NEGATIVE_FUEL_CONSERVATION_VIOLATED"
            thermal = self.entities.get("thermal_radiator")
            if thermal and thermal.properties.get("temp_c", 40.0) > 85.0:
                return "THERMAL_OVERHEAT_RUNAWAY"

        elif self.domain == "joint_fleet_logistics":
            hub = self.entities.get("charging_hub")
            if hub and hub.properties.get("active_load_kw", 0.0) > 250.0:
                return "GRID_TRANSFORMER_BLOWOUT"

        return None

    def environmental_tick(self) -> Dict[str, Any]:
        """Advance time by 1 tick, applying passive environmental decay."""
        self.tick += 1
        decay_deltas = {}

        if self.domain == "collaborative_microgrid":
            bus = self.entities.get("critical_bus")
            if bus:
                # Fluctuating wind load
                drift = 1.0 if (self.tick % 2 == 0) else -1.5
                bus.properties["voltage"] = round(bus.properties.get("voltage", 340.0) + drift, 2)
                bus.version += 1
                decay_deltas["critical_bus"] = {"voltage_drift": drift}

        elif self.domain == "concurrent_orbital_maintenance":
            attitude = self.entities.get("docking_adapter")
            if attitude and not attitude.properties.get("is_locked", False):
                # Passive attitude drift
                attitude.properties["alignment_err_deg"] = round(attitude.properties.get("alignment_err_deg", 5.0) + 0.5, 2)
                attitude.version += 1
                decay_deltas["docking_adapter"] = {"alignment_drift": 0.5}

        elif self.domain == "joint_fleet_logistics":
            reefer = self.entities.get("reefer_b")
            if reefer:
                # Passive insulation warming
                reefer.properties["temp_c"] = round(reefer.properties.get("temp_c", -18.0) + 0.3, 2)
                reefer.version += 1
                decay_deltas["reefer_b"] = {"temp_warm": 0.3}

        return decay_deltas
