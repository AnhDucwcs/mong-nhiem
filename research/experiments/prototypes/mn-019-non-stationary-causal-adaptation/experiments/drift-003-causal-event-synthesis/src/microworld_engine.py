"""Host-Authoritative Simulated Microworld Engine with Causal Latent Coupling for Stage 3.

Supports multi-rate background clocks, dynamic entity topology (emergence, mutation, retirement),
latent causal traps, physical conservation invariant validation, and non-destructive
counterfactual sandbox execution.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from causal_event_logger import CausalEventLog
from schema_evolution_engine import SchemaEvolutionEngine, SchemaEvolutionRule


@dataclass
class WorldEntity:
    """Discrete state container with dynamic schema fields and relational bindings."""
    entity_id: str
    entity_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    relations: Dict[str, str] = field(default_factory=dict)
    version: int = 1
    is_active: bool = True
    ttl: Optional[int] = None
    rate_of_decay: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "properties": copy.deepcopy(self.properties),
            "relations": copy.deepcopy(self.relations),
            "version": self.version,
            "is_active": self.is_active,
            "ttl": self.ttl,
            "rate_of_decay": copy.deepcopy(self.rate_of_decay),
        }

    def render_compact(self) -> str:
        status = "active" if self.is_active else "retired"
        props_str = " ".join(f"{k}={v}" for k, v in sorted(self.properties.items()))
        rel_str = (" -> " + " ".join(f"{k}:{v}" for k, v in sorted(self.relations.items()))) if self.relations else ""
        ttl_str = f" ttl={self.ttl}" if self.ttl is not None else ""
        return f"[ENTITY {self.entity_id}:{self.entity_type} v{self.version} {status}{ttl_str} {props_str}{rel_str}]"


class ConservationGuard:
    """Validates physical conservation laws and schema integrity bounds."""

    @staticmethod
    def validate_invariants(
        domain: str,
        entities: Dict[str, WorldEntity],
        action_target_entity: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        # Schema Invariant: Action cannot reference a non-existent or inactive/retired entity
        if action_target_entity:
            if action_target_entity not in entities:
                return False, f"SCHEMA_VIOLATION: Referenced entity '{action_target_entity}' does not exist in active topology"
            if not entities[action_target_entity].is_active:
                return False, f"SCHEMA_VIOLATION: Referenced entity '{action_target_entity}' has decommissioned/retired"

        # Domain A: orbital_life_support
        if domain == "orbital_life_support":
            thermal = entities.get("thermal_loop")
            if thermal and thermal.is_active and thermal.properties.get("temperature", 0.0) > 95.0:
                return False, f"Radiator thermal equilibrium violated: {thermal.properties.get('temperature')} C > 95.0 C"

            scrubber = entities.get("o2_scrubber")
            if scrubber and scrubber.is_active and scrubber.properties.get("o2_pressure", 0.0) < 18.0:
                return False, f"Oxygen partial pressure depleted below survival bound: {scrubber.properties.get('o2_pressure')} kPa < 18.0 kPa"

            battery = entities.get("cryo_battery")
            if battery and battery.is_active and battery.properties.get("charge_kwh", 0.0) < 0.0:
                return False, f"Cryo battery energy non-negativity breached: {battery.properties.get('charge_kwh')} kWh < 0"

        # Domain B: smart_microgrid
        elif domain == "smart_microgrid":
            bus = entities.get("critical_bus")
            if bus and bus.is_active:
                v = bus.properties.get("voltage", 380.0)
                if v < 342.0 or v > 418.0:
                    return False, f"Bus voltage bounds breached: {v} V not in [342.0, 418.0]"

            battery = entities.get("battery_bank")
            if battery and battery.is_active and battery.properties.get("soc", 100.0) < 0.0:
                return False, f"Battery state of charge depleted: {battery.properties.get('soc')}% < 0"

        # Domain C: fleet_logistics
        elif domain == "fleet_logistics":
            reefer = entities.get("reefer_unit")
            if reefer and reefer.is_active and reefer.properties.get("cargo_temp", -20.0) > -15.0:
                return False, f"Cargo deep freeze temperature breached: {reefer.properties.get('cargo_temp')} C > -15.0 C"

            aux = entities.get("aux_battery")
            if aux and aux.is_active and aux.properties.get("power_kw", 10.0) < 0.0:
                return False, f"Auxiliary battery depleted below zero: {aux.properties.get('power_kw')} kW < 0"

        # Domain D: subsea_hydrothermal
        elif domain == "subsea_hydrothermal":
            ballast = entities.get("depth_ballast")
            if ballast and ballast.is_active:
                p = ballast.properties.get("chamber_pressure", 200.0)
                if p > 320.0:
                    return False, f"Subsea chamber over-pressurization breach: {p} bar > 320.0 bar"
                if p < 100.0:
                    return False, f"Subsea chamber implosion risk: {p} bar < 100.0 bar"

            gen = entities.get("thermoelectric_gen")
            if gen and gen.is_active and gen.properties.get("core_temp", 90.0) > 140.0:
                return False, f"Thermoelectric core thermal runaway: {gen.properties.get('core_temp')} C > 140.0 C"

        return True, None


class SimulatedMicroworld:
    """Host-authoritative world engine with causal latent traps and counterfactual execution."""

    def __init__(
        self,
        domain: str,
        initial_entities: Dict[str, Any],
        schema_rules: Optional[List[SchemaEvolutionRule]] = None,
        event_logger: Optional[CausalEventLog] = None,
    ) -> None:
        self.domain = domain
        self.current_tick: int = 0
        self.event_logger = event_logger or CausalEventLog()
        self.schema_engine = SchemaEvolutionEngine(rules=schema_rules, event_logger=self.event_logger)

        self.entities: Dict[str, WorldEntity] = {}
        for eid, edata in initial_entities.items():
            props = edata.get("properties", {})
            relations = edata.get("relations", {})
            etype = edata.get("entity_type", "generic")
            ver = edata.get("version", 1)
            is_act = edata.get("is_active", True)
            ttl = edata.get("ttl", None)
            decay = edata.get("rate_of_decay", {})
            self.entities[eid] = WorldEntity(
                entity_id=eid,
                entity_type=etype,
                properties=copy.deepcopy(props),
                relations=copy.deepcopy(relations),
                version=ver,
                is_active=is_act,
                ttl=ttl,
                rate_of_decay=copy.deepcopy(decay),
            )

    def tick_simulation(self, elapsed_ticks: int = 1) -> List[Dict[str, Any]]:
        self.current_tick += elapsed_ticks

        for eid, entity in list(self.entities.items()):
            if entity.is_active and entity.ttl is not None:
                entity.ttl -= elapsed_ticks
                if entity.ttl <= 0:
                    entity.is_active = False
                    entity.version += 1
                    self.event_logger.record_event(
                        tick=self.current_tick,
                        event_type="RETIRE",
                        entity_id=eid,
                        pre_state=entity.to_dict(),
                        post_state=entity.to_dict(),
                        delta_signature={"reason": "TTL_EXPIRED"},
                    )

        fired_schema_events = self.schema_engine.evaluate_step(self.current_tick, self.entities)
        return fired_schema_events

    def execute_transition(self, action_str: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        backup_entities = copy.deepcopy(self.entities)
        target_eid = self._extract_target_entity_from_action(action_str)

        valid_schema, schema_err = ConservationGuard.validate_invariants(
            self.domain, self.entities, action_target_entity=target_eid
        )
        if not valid_schema:
            return False, schema_err, {eid: copy.deepcopy(e.properties) for eid, e in self.entities.items()}

        try:
            self._apply_action(self.entities, action_str)
            self.tick_simulation(elapsed_ticks=1)

            valid_physics, phys_err = ConservationGuard.validate_invariants(self.domain, self.entities)
            if not valid_physics:
                # Log latent trap trigger in CausalEventLog
                self.event_logger.record_event(
                    tick=self.current_tick,
                    event_type="TRAP_TRIGGER",
                    entity_id=target_eid or "unknown",
                    pre_state=backup_entities[target_eid].to_dict() if target_eid and target_eid in backup_entities else {},
                    post_state=self.entities[target_eid].to_dict() if target_eid and target_eid in self.entities else {},
                    triggering_action=action_str,
                    delta_signature={"reason": phys_err},
                )
                self.entities = backup_entities
                return False, phys_err, {eid: copy.deepcopy(e.properties) for eid, e in self.entities.items()}

            if target_eid and target_eid in self.entities:
                self.event_logger.record_event(
                    tick=self.current_tick,
                    event_type="ACTION",
                    entity_id=target_eid,
                    pre_state=backup_entities[target_eid].to_dict() if target_eid in backup_entities else {},
                    post_state=self.entities[target_eid].to_dict(),
                    triggering_action=action_str,
                )

            return True, None, {eid: copy.deepcopy(e.properties) for eid, e in self.entities.items()}

        except Exception as ex:
            self.entities = backup_entities
            return False, f"TRANSITION_ERROR: {str(ex)}", {eid: copy.deepcopy(e.properties) for eid, e in self.entities.items()}

    def simulate_counterfactual_step(self, hypothetical_action: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        sandbox_copy = copy.deepcopy(self)
        ok, msg, res = sandbox_copy.execute_transition(hypothetical_action)
        return ok, msg, res

    def _extract_target_entity_from_action(self, action_str: str) -> Optional[str]:
        tokens = action_str.strip().split()
        if not tokens:
            return None
        cmd = tokens[0]

        # Domain A: orbital_life_support
        if cmd in ("divert_solar_power", "couple_secondary_cryo"):
            return tokens[1] if len(tokens) >= 2 else "cryo_battery"
        if cmd in ("purge_cabin_heat", "engage_auxiliary_cryo_pump", "activate_secondary_cooler"):
            return "aux_cooler" if cmd == "activate_secondary_cooler" else "thermal_loop"
        if cmd == "boost_scrubber_oxygen":
            return "o2_scrubber"

        # Domain B: smart_microgrid
        if cmd == "discharge_battery":
            return "battery_bank"
        if cmd == "regulate_wind_pitch":
            return "wind_turbine"
        if cmd in ("engage_static_compensator", "connect_secondary_feeder", "sync_flywheel_reserve"):
            return "secondary_feeder" if cmd == "connect_secondary_feeder" else "critical_bus"

        # Domain C: fleet_logistics
        if cmd in ("chill_reefer_compartment", "activate_emergency_cooling_pack", "engage_booster_trailer"):
            return "booster_trailer" if cmd == "engage_booster_trailer" else "reefer_unit"
        if cmd == "adjust_traction_drive":
            return "traction_motor"

        # Domain D: subsea_hydrothermal
        if cmd in ("throttle_hydrothermal_intake", "engage_cryo_heat_sink"):
            return "thermoelectric_gen"
        if cmd in ("vent_ballast_chamber", "open_auxiliary_vent_hatch"):
            return "aux_vent" if cmd == "open_auxiliary_vent_hatch" else "depth_ballast"
        if cmd in ("flush_salinity_sensor", "calibrate_mineral_beacon"):
            return "mineral_beacon" if cmd == "calibrate_mineral_beacon" else "salinity_sensor"

        return None

    def _apply_action(self, target_entities: Dict[str, WorldEntity], action_str: str) -> None:
        tokens = action_str.strip().split()
        if not tokens:
            return
        cmd = tokens[0]

        # Domain A: orbital_life_support
        if self.domain == "orbital_life_support":
            if cmd == "divert_solar_power" and len(tokens) >= 3:
                pct = float(tokens[2])
                solar = target_entities.get("solar_array")
                battery = target_entities.get("cryo_battery")
                thermal = target_entities.get("thermal_loop")
                scrubber = target_entities.get("o2_scrubber")

                # Latent Causal Trap: high divert when thermal temp > 70.0 causes runaway trip on scrubber
                if pct > 75.0 and thermal and thermal.properties.get("temperature", 75.0) > 70.0 and scrubber:
                    scrubber.properties["o2_pressure"] = 10.0  # Invariant breach: < 18.0 kPa
                    scrubber.version += 1

                if solar and battery:
                    gen_power = solar.properties.get("output_kw", 50.0) * (pct / 100.0)
                    battery.properties["charge_kwh"] = round(battery.properties.get("charge_kwh", 12.0) + (gen_power * 0.1), 2)
                    solar.version += 1
                    battery.version += 1
                    if pct > 75.0 and thermal:
                        thermal.properties["temperature"] = round(thermal.properties.get("temperature", 75.0) + 15.0, 2)
                        thermal.version += 1

            elif cmd == "purge_cabin_heat" and len(tokens) >= 2:
                flow = float(tokens[1])
                thermal = target_entities.get("thermal_loop")
                if thermal:
                    new_t = max(68.0, round(thermal.properties.get("temperature", 75.0) - (flow * 0.5), 2))
                    thermal.properties["temperature"] = new_t
                    thermal.version += 1

            elif cmd == "engage_auxiliary_cryo_pump":
                thermal = target_entities.get("thermal_loop")
                battery = target_entities.get("cryo_battery")
                if thermal and battery:
                    battery.properties["charge_kwh"] = round(battery.properties.get("charge_kwh", 12.0) - 2.0, 2)
                    thermal.properties["temperature"] = round(thermal.properties.get("temperature", 75.0) - 15.0, 2)
                    thermal.version += 1
                    battery.version += 1

            elif cmd == "activate_secondary_cooler":
                aux = target_entities.get("aux_cooler")
                thermal = target_entities.get("thermal_loop")
                if aux and thermal and aux.is_active:
                    cooling_power = aux.properties.get("cooling_kw", 30.0)
                    thermal.properties["temperature"] = round(thermal.properties.get("temperature", 75.0) - (cooling_power * 0.5), 2)
                    thermal.version += 1
                    aux.version += 1

            elif cmd == "boost_scrubber_oxygen" and len(tokens) >= 2:
                rate = float(tokens[1])
                scrubber = target_entities.get("o2_scrubber")
                battery = target_entities.get("cryo_battery")
                if scrubber and battery:
                    battery.properties["charge_kwh"] = round(battery.properties.get("charge_kwh", 12.0) - (rate * 0.8), 2)
                    scrubber.properties["o2_pressure"] = round(scrubber.properties.get("o2_pressure", 20.0) + (rate * 0.4), 2)
                    scrubber.version += 1
                    battery.version += 1

        # Domain B: smart_microgrid
        elif self.domain == "smart_microgrid":
            if cmd == "discharge_battery" and len(tokens) >= 2:
                mw = float(tokens[1])
                battery = target_entities.get("battery_bank")
                bus = target_entities.get("critical_bus")
                if battery and bus:
                    battery.properties["soc"] = round(battery.properties.get("soc", 60.0) - (mw * 0.8), 2)
                    bus.properties["voltage"] = min(375.0, round(bus.properties.get("voltage", 370.0) + 5.0, 2))
                    battery.version += 1
                    bus.version += 1

            elif cmd == "regulate_wind_pitch" and len(tokens) >= 2:
                deg = float(tokens[1])
                wind = target_entities.get("wind_turbine")
                bus = target_entities.get("critical_bus")
                battery = target_entities.get("battery_bank")

                # Latent Causal Trap: excessive pitch > 45.0 deg causes turbine generator over-voltage surge
                if deg > 45.0 and bus:
                    bus.properties["voltage"] = 425.0  # Invariant breach: > 418.0 V
                    bus.version += 1

                if wind and bus:
                    output = deg * 1.2
                    wind.properties["output_kw"] = round(output, 2)
                    bus.properties["voltage"] = min(375.0, round(bus.properties.get("voltage", 370.0) + (output * 0.1), 2))
                    wind.version += 1
                    bus.version += 1
                    if battery:
                        battery.properties["soc"] = round(battery.properties.get("soc", 40.0) + 20.0, 2)
                        battery.version += 1

            elif cmd == "engage_static_compensator":
                bus = target_entities.get("critical_bus")
                if bus:
                    bus.properties["voltage"] = 380.0
                    bus.version += 1

            elif cmd == "connect_secondary_feeder":
                feeder = target_entities.get("secondary_feeder")
                bus = target_entities.get("critical_bus")
                battery = target_entities.get("battery_bank")

                # Latent Causal Trap: connecting feeder when battery SOC < 50% causes inrush bus blackout
                if battery and battery.properties.get("soc", 60.0) < 50.0 and bus:
                    bus.properties["voltage"] = 330.0  # Invariant breach: < 342.0 V
                    bus.version += 1

                if feeder and bus and feeder.is_active:
                    bus.properties["voltage"] = 385.0
                    feeder.version += 1
                    bus.version += 1

            elif cmd == "sync_flywheel_reserve":
                fly = target_entities.get("flywheel_reserve")
                bus = target_entities.get("critical_bus")
                if fly and bus and fly.is_active:
                    bus.properties["voltage"] = 380.0
                    fly.version += 1
                    bus.version += 1

        # Domain C: fleet_logistics
        elif self.domain == "fleet_logistics":
            if cmd == "chill_reefer_compartment" and len(tokens) >= 2:
                level = float(tokens[1])
                reefer = target_entities.get("reefer_unit")
                aux = target_entities.get("aux_battery")
                if reefer and aux:
                    aux.properties["power_kw"] = round(aux.properties.get("power_kw", 20.0) - level, 2)
                    new_t = max(-18.0, round(reefer.properties.get("cargo_temp", -17.0) - (level * 1.2), 2))
                    reefer.properties["cargo_temp"] = new_t
                    reefer.version += 1
                    aux.version += 1

            elif cmd == "adjust_traction_drive" and len(tokens) >= 2:
                speed = float(tokens[1])
                motor = target_entities.get("traction_motor")
                aux = target_entities.get("aux_battery")

                # Latent Causal Trap: highway over-speed > 80 km/h drains aux battery below zero
                if speed > 80.0 and aux:
                    aux.properties["power_kw"] = -3.0  # Invariant breach: < 0.0 kW
                    aux.version += 1

                if motor and aux:
                    drain = speed * 0.1
                    aux.properties["power_kw"] = round(aux.properties.get("power_kw", 15.0) + 10.0 - drain, 2)
                    motor.properties["speed_kph"] = round(speed, 1)
                    motor.version += 1
                    aux.version += 1

            elif cmd == "activate_emergency_cooling_pack":
                reefer = target_entities.get("reefer_unit")
                pack = target_entities.get("coolant_pack")
                if reefer and pack:
                    reefer.properties["cargo_temp"] = -22.0
                    reefer.version += 1

            elif cmd == "engage_booster_trailer":
                booster = target_entities.get("booster_trailer")
                reefer = target_entities.get("reefer_unit")
                aux = target_entities.get("aux_battery")

                # Latent Causal Trap: engaging booster when aux power < 18 kW causes motor starvation
                if aux and aux.properties.get("power_kw", 20.0) < 18.0:
                    aux.properties["power_kw"] = -5.0  # Invariant breach: < 0.0 kW
                    aux.version += 1

                if booster and reefer and booster.is_active:
                    reefer.properties["cargo_temp"] = -25.0
                    booster.version += 1
                    reefer.version += 1

        # Domain D: subsea_hydrothermal
        elif self.domain == "subsea_hydrothermal":
            if cmd == "throttle_hydrothermal_intake" and len(tokens) >= 2:
                pct = float(tokens[1])
                gen = target_entities.get("thermoelectric_gen")
                if gen:
                    gen.properties["core_temp"] = round(gen.properties.get("core_temp", 110.0) + (pct * 0.8), 1)
                    gen.version += 1

            elif cmd == "engage_cryo_heat_sink":
                gen = target_entities.get("thermoelectric_gen")
                if gen:
                    gen.properties["core_temp"] = 85.0
                    gen.version += 1

            elif cmd == "vent_ballast_chamber" and len(tokens) >= 2:
                amount = float(tokens[1])
                ballast = target_entities.get("depth_ballast")
                gen = target_entities.get("thermoelectric_gen")

                # Latent Causal Trap: venting when generator core temp > 100 C causes intake cavitation rupture
                if gen and gen.properties.get("core_temp", 95.0) > 100.0 and ballast:
                    ballast.properties["chamber_pressure"] = 340.0  # Invariant breach: > 320.0 bar
                    ballast.version += 1

                if ballast:
                    new_p = max(215.0, round(ballast.properties.get("chamber_pressure", 220.0) - amount, 1))
                    ballast.properties["chamber_pressure"] = new_p
                    ballast.version += 1

            elif cmd == "open_auxiliary_vent_hatch":
                hatch = target_entities.get("aux_vent")
                ballast = target_entities.get("depth_ballast")
                if hatch and ballast and hatch.is_active:
                    ballast.properties["chamber_pressure"] = round(ballast.properties.get("chamber_pressure", 220.0) - 50.0, 1)
                    hatch.version += 1
                    ballast.version += 1

            elif cmd == "flush_salinity_sensor":
                sensor = target_entities.get("salinity_sensor")
                if sensor:
                    sensor.properties["bias_ppm"] = 0.0
                    sensor.version += 1

            elif cmd == "calibrate_mineral_beacon":
                beacon = target_entities.get("mineral_beacon")
                if beacon and beacon.is_active:
                    beacon.properties["calibration_status"] = "CALIBRATED"
                    beacon.version += 1
