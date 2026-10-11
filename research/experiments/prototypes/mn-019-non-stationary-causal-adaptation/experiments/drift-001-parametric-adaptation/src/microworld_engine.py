"""Host-Authoritative Simulated Microworld Engine with Non-Stationary Parametric Drift.

Extends physical conservation law invariants and multi-rate simulation clocks
with continuous parametric drift dynamics (linear, exponential, step shock, harmonic oscillation)
and coupled cross-channel degradation.
"""
from __future__ import annotations

import copy
import math
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

    def render_fact_card(self, compact: bool = True) -> str:
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


@dataclass
class ParametricDriftRule:
    """Definition of continuous parametric drift applied to entity properties."""
    target_entity_id: str
    property_name: str
    drift_type: str  # 'linear_decay', 'exponential_decay', 'step_shock', 'harmonic_oscillation'
    rate: float
    start_tick: int
    floor_value: Optional[float] = None
    ceiling_value: Optional[float] = None
    amplitude: float = 0.0
    frequency: float = 0.1
    coupled_entities: List[str] = field(default_factory=list)  # Cross-channel degradation targets

    def compute_multiplier(self, current_tick: int) -> float:
        """Calculate the parametric multiplier at the current simulation tick."""
        if current_tick < self.start_tick:
            return 1.0

        elapsed = current_tick - self.start_tick

        if self.drift_type == "linear_decay":
            mult = max(0.0, 1.0 - (self.rate * elapsed))
        elif self.drift_type == "exponential_decay":
            mult = math.exp(-self.rate * elapsed)
        elif self.drift_type == "step_shock":
            mult = self.rate  # Direct factor reduction (e.g., 0.5)
        elif self.drift_type == "harmonic_oscillation":
            mult = 1.0 + (self.amplitude * math.sin(self.frequency * elapsed)) - (self.rate * elapsed)
            mult = max(0.0, mult)
        else:
            mult = 1.0

        if self.floor_value is not None:
            mult = max(self.floor_value, mult)
        if self.ceiling_value is not None:
            mult = min(self.ceiling_value, mult)

        return float(mult)


class ConservationGuard:
    """Host-authoritative physical conservation law and state invariant validator."""

    @staticmethod
    def validate_invariants(
        entities: Dict[str, WorldEntity],
        domain: str,
        nominal_constants: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """Validate strict conservation laws across active entities.
        
        Returns:
            Tuple[is_valid, violation_message_or_None]
        """
        if domain == "orbital_life_support":
            # 1. Total thermal balance: radiator dissipation must keep loop temperature < 95.0 C
            thermal = entities.get("thermal_loop")
            if thermal and thermal.properties.get("temperature", 0.0) > 95.0:
                return False, f"Thermal runaway invariant breached: {thermal.properties.get('temperature')} C > 95.0 C"
            
            # 2. Oxygen pressure non-negativity and minimum survival threshold (>= 18.0 kPa)
            scrubber = entities.get("o2_scrubber")
            if scrubber and scrubber.properties.get("o2_pressure", 0.0) < 18.0:
                return False, f"Oxygen partial pressure depleted below critical survival bound: {scrubber.properties.get('o2_pressure')} kPa"

            # 3. Cryo battery charge capacity non-negativity (>= 0.0 kWh)
            battery = entities.get("cryo_battery")
            if battery and battery.properties.get("charge_kwh", 0.0) < 0.0:
                return False, f"Cryo battery energy non-negativity breached: {battery.properties.get('charge_kwh')} kWh < 0"

        elif domain == "smart_microgrid":
            # 1. Instantaneous bus voltage stability (380V +/- 10%: [342.0, 418.0])
            bus = entities.get("critical_bus")
            if bus:
                v = bus.properties.get("voltage", 380.0)
                if v < 342.0 or v > 418.0:
                    return False, f"Bus voltage bounds breached: {v} V not in [342.0, 418.0]"

            # 2. Battery state of charge (SoC non-negative)
            battery = entities.get("battery_bank")
            if battery and battery.properties.get("soc", 100.0) < 0.0:
                return False, f"Battery state of charge depleted: {battery.properties.get('soc')}% < 0"

        elif domain == "fleet_logistics":
            # 1. Reefer temperature must stay below freezing limit (<= -15.0 C for deep freeze)
            reefer = entities.get("reefer_unit")
            if reefer and reefer.properties.get("cargo_temp", -20.0) > -15.0:
                return False, f"Cargo deep freeze temperature breached: {reefer.properties.get('cargo_temp')} C > -15.0 C"

            # 2. Auxiliary power non-negative
            aux = entities.get("aux_battery")
            if aux and aux.properties.get("power_kw", 10.0) < 0.0:
                return False, f"Auxiliary battery depleted below zero: {aux.properties.get('power_kw')} kW < 0"

        elif domain == "subsea_hydrothermal":
            # 1. Hydrothermal intake pressure bounds ([150.0, 320.0] bar)
            ballast = entities.get("depth_ballast")
            if ballast:
                p = ballast.properties.get("chamber_pressure", 200.0)
                if p > 320.0:
                    return False, f"Subsea chamber over-pressurization breach: {p} bar > 320.0 bar"
                if p < 100.0:
                    return False, f"Subsea chamber implosion risk: {p} bar < 100.0 bar"

            # 2. Generator core temperature threshold (<= 140.0 C)
            gen = entities.get("thermoelectric_gen")
            if gen and gen.properties.get("core_temp", 90.0) > 140.0:
                return False, f"Thermoelectric core thermal runaway: {gen.properties.get('core_temp')} C > 140.0 C"

        return True, None


class SimulatedMicroworld:
    """Multi-rate discrete-event microworld with non-stationary drift dynamics."""

    def __init__(
        self,
        domain: str,
        initial_entities: Dict[str, WorldEntity],
        nominal_constants: Optional[Dict[str, Any]] = None,
        drift_rules: Optional[List[ParametricDriftRule]] = None,
    ):
        self.domain = domain
        self.entities = copy.deepcopy(initial_entities)
        self.nominal_constants = nominal_constants or {}
        self.drift_rules = drift_rules or []
        self.current_tick = 0
        self.event_log: List[Dict[str, Any]] = []

    def tick_simulation(self, elapsed_ticks: int = 1) -> None:
        """Advance multi-rate simulation clocks and apply decay."""
        self.current_tick += elapsed_ticks

        for eid, entity in list(self.entities.items()):
            if not entity.is_active:
                continue

            # Decrement TTL
            if entity.ttl is not None:
                entity.ttl -= elapsed_ticks
                if entity.ttl <= 0:
                    entity.is_active = False
                    self.event_log.append({
                        "tick": self.current_tick,
                        "event": "ENTITY_EXPIRED",
                        "entity_id": eid,
                    })

            # Apply natural decay rates
            for prop_key, decay_rate in entity.rate_of_decay.items():
                if prop_key in entity.properties and isinstance(entity.properties[prop_key], (int, float)):
                    # Compute drift multiplier for this property if rule exists
                    mult = self.get_drift_multiplier(eid, prop_key)
                    # Natural decay modified by drift
                    val = entity.properties[prop_key] - (decay_rate * mult * elapsed_ticks)
                    entity.properties[prop_key] = round(val, 2)
                    entity.version += 1

    def get_drift_multiplier(self, entity_id: str, property_name: str) -> float:
        """Retrieve compounded drift multiplier for an entity property."""
        multiplier = 1.0
        for rule in self.drift_rules:
            if rule.target_entity_id == entity_id and rule.property_name == property_name:
                multiplier *= rule.compute_multiplier(self.current_tick)
            elif entity_id in rule.coupled_entities:
                # Coupled cross-channel degradation
                base_mult = rule.compute_multiplier(self.current_tick)
                # Suffer 50% coupled severity
                coupled_factor = 1.0 - ((1.0 - base_mult) * 0.5)
                multiplier *= coupled_factor
        return multiplier

    def compute_nominal_transition(self, action_str: str) -> Dict[str, Any]:
        """Compute the expected nominal state assuming 1.0 conversion efficiencies."""
        nominal_entities = copy.deepcopy(self.entities)
        self._apply_action_effects(nominal_entities, action_str, drift_aware=False)
        return {eid: copy.deepcopy(e.properties) for eid, e in nominal_entities.items()}

    def execute_actual_transition(self, action_str: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Apply true actual action transition with real parametric drift factors.
        
        Returns:
            Tuple[is_success, error_or_None, updated_state_dict]
        """
        # Save snapshot for atomic rollback in case of invariant violation
        backup_entities = copy.deepcopy(self.entities)

        try:
            # Apply actual action effects factoring in drift
            self._apply_action_effects(self.entities, action_str, drift_aware=True)
            
            # Tick clocks forward 1 tick on action execution
            self.tick_simulation(elapsed_ticks=1)

            # Validate physical conservation laws
            valid, breach_msg = ConservationGuard.validate_invariants(
                self.entities, self.domain, self.nominal_constants
            )

            if not valid:
                # Rollback to pre-action state
                self.entities = backup_entities
                self.event_log.append({
                    "tick": self.current_tick,
                    "event": "INVARIANT_BREACH_INTERCEPTED",
                    "action": action_str,
                    "reason": breach_msg,
                })
                return False, breach_msg, {eid: copy.deepcopy(e.properties) for eid, e in self.entities.items()}

            self.event_log.append({
                "tick": self.current_tick,
                "event": "ACTION_COMMITTED",
                "action": action_str,
            })
            return True, None, {eid: copy.deepcopy(e.properties) for eid, e in self.entities.items()}

        except Exception as ex:
            self.entities = backup_entities
            return False, f"Execution exception: {str(ex)}", {eid: copy.deepcopy(e.properties) for eid, e in self.entities.items()}

    def _apply_action_effects(self, target_entities: Dict[str, WorldEntity], action_str: str, drift_aware: bool) -> None:
        """Internal helper to mutate entity state based on parsed action command."""
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
                if solar and battery:
                    eff = self.get_drift_multiplier("solar_array", "efficiency") if drift_aware else 1.0
                    gen_power = solar.properties.get("output_kw", 50.0) * (pct / 100.0) * eff
                    battery.properties["charge_kwh"] = round(battery.properties.get("charge_kwh", 12.0) + (gen_power * 0.1), 2)
                    solar.version += 1
                    battery.version += 1
                    if pct > 80.0 and thermal:
                        # High unbuffered power diversion creates bus thermal surge
                        thermal.properties["temperature"] = round(thermal.properties.get("temperature", 75.0) + 25.0, 2)
                        thermal.version += 1

            elif cmd == "purge_cabin_heat" and len(tokens) >= 2:
                flow = float(tokens[1])
                thermal = target_entities.get("thermal_loop")
                if thermal:
                    eff = self.get_drift_multiplier("thermal_loop", "coolant_flow") if drift_aware else 1.0
                    cooling = flow * 0.5 * eff
                    thermal.properties["temperature"] = round(thermal.properties.get("temperature", 75.0) - cooling, 2)
                    thermal.version += 1

            elif cmd == "boost_scrubber_oxygen" and len(tokens) >= 2:
                rate = float(tokens[1])
                scrubber = target_entities.get("o2_scrubber")
                battery = target_entities.get("cryo_battery")
                if scrubber and battery:
                    eff = self.get_drift_multiplier("o2_scrubber", "filter_permeability") if drift_aware else 1.0
                    power_cost = rate * 0.8 * (1.0 / max(0.15, eff))
                    battery.properties["charge_kwh"] = round(battery.properties.get("charge_kwh", 12.0) - power_cost, 2)
                    scrubber.properties["o2_pressure"] = round(scrubber.properties.get("o2_pressure", 20.0) + (rate * 0.4 * eff), 2)
                    scrubber.version += 1
                    battery.version += 1

            elif cmd == "engage_auxiliary_cryo_pump":
                thermal = target_entities.get("thermal_loop")
                battery = target_entities.get("cryo_battery")
                if thermal and battery:
                    battery.properties["charge_kwh"] = round(battery.properties.get("charge_kwh", 12.0) - 2.0, 2)
                    thermal.properties["temperature"] = round(thermal.properties.get("temperature", 75.0) - 15.0, 2)
                    thermal.version += 1
                    battery.version += 1

        # Domain B: smart_microgrid
        elif self.domain == "smart_microgrid":
            if cmd == "discharge_battery" and len(tokens) >= 2:
                mw = float(tokens[1])
                battery = target_entities.get("battery_bank")
                bus = target_entities.get("critical_bus")
                if battery and bus:
                    impedance_mult = self.get_drift_multiplier("battery_bank", "internal_resistance") if drift_aware else 1.0
                    voltage_sag = mw * 1.5 * impedance_mult
                    battery.properties["soc"] = round(battery.properties.get("soc", 60.0) - (mw * 0.8), 2)
                    bus.properties["voltage"] = round(bus.properties.get("voltage", 375.0) + 10.0 - voltage_sag, 2)
                    battery.version += 1
                    bus.version += 1

            elif cmd == "regulate_wind_pitch" and len(tokens) >= 2:
                deg = float(tokens[1])
                wind = target_entities.get("wind_turbine")
                bus = target_entities.get("critical_bus")
                if wind and bus:
                    wind_mult = self.get_drift_multiplier("wind_turbine", "shear_stability") if drift_aware else 1.0
                    output = deg * 1.2 * wind_mult
                    wind.properties["output_kw"] = round(output, 2)
                    bus.properties["voltage"] = round(bus.properties.get("voltage", 375.0) + (output * 0.1), 2)
                    wind.version += 1
                    bus.version += 1

            elif cmd == "engage_static_compensator":
                bus = target_entities.get("critical_bus")
                if bus:
                    bus.properties["voltage"] = 380.0
                    bus.version += 1

        # Domain C: fleet_logistics
        elif self.domain == "fleet_logistics":
            if cmd == "chill_reefer_compartment" and len(tokens) >= 2:
                level = float(tokens[1])
                reefer = target_entities.get("reefer_unit")
                aux = target_entities.get("aux_battery")
                if reefer and aux:
                    insul_eff = self.get_drift_multiplier("reefer_unit", "insulation_r_value") if drift_aware else 1.0
                    power_drain = level * 1.0 * (1.0 / max(0.2, insul_eff))
                    aux.properties["power_kw"] = round(aux.properties.get("power_kw", 20.0) - power_drain, 2)
                    cooling = level * 1.2 * insul_eff
                    reefer.properties["cargo_temp"] = round(reefer.properties.get("cargo_temp", -17.0) - cooling, 2)
                    reefer.version += 1
                    aux.version += 1

            elif cmd == "adjust_traction_drive" and len(tokens) >= 2:
                speed = float(tokens[1])
                motor = target_entities.get("traction_motor")
                aux = target_entities.get("aux_battery")
                if motor and aux:
                    fric_mult = self.get_drift_multiplier("traction_motor", "bearing_friction") if drift_aware else 1.0
                    drain = speed * 0.3 * fric_mult
                    aux.properties["power_kw"] = round(aux.properties.get("power_kw", 20.0) - drain, 2)
                    motor.properties["speed_kph"] = round(speed, 1)
                    motor.version += 1
                    aux.version += 1

            elif cmd == "activate_emergency_cooling_pack":
                reefer = target_entities.get("reefer_unit")
                pack = target_entities.get("coolant_pack")
                if reefer and pack:
                    pack.properties["charges"] = max(0, pack.properties.get("charges", 3) - 1)
                    reefer.properties["cargo_temp"] = -22.0
                    reefer.version += 1

        # Domain D: subsea_hydrothermal
        elif self.domain == "subsea_hydrothermal":
            if cmd == "throttle_hydrothermal_intake" and len(tokens) >= 2:
                pct = float(tokens[1])
                gen = target_entities.get("thermoelectric_gen")
                ballast = target_entities.get("depth_ballast")
                if gen and ballast:
                    foul_mult = self.get_drift_multiplier("thermoelectric_gen", "heat_sink_fouling") if drift_aware else 1.0
                    heat_rise = pct * 0.8 * foul_mult
                    pressure_change = pct * 1.5
                    gen.properties["core_temp"] = round(gen.properties.get("core_temp", 110.0) + heat_rise, 1)
                    ballast.properties["chamber_pressure"] = round(ballast.properties.get("chamber_pressure", 240.0) + pressure_change, 1)
                    gen.version += 1
                    ballast.version += 1

            elif cmd == "flush_salinity_sensor":
                sensor = target_entities.get("salinity_sensor")
                if sensor:
                    sensor.properties["bias_ppm"] = 0.0
                    sensor.version += 1

            elif cmd == "vent_ballast_chamber" and len(tokens) >= 2:
                bar = float(tokens[1])
                ballast = target_entities.get("depth_ballast")
                if ballast:
                    ballast.properties["chamber_pressure"] = round(ballast.properties.get("chamber_pressure", 240.0) - bar, 1)
                    ballast.version += 1

            elif cmd == "engage_cryo_heat_sink":
                gen = target_entities.get("thermoelectric_gen")
                if gen:
                    gen.properties["core_temp"] = round(gen.properties.get("core_temp", 110.0) - 30.0, 1)
                    gen.version += 1
