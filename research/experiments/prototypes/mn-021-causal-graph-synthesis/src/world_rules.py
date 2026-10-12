"""World Invariants and Domain Physical Transition Rules for MN-021.

Defines physical conservation constraints and transition predicates for:
- Domain A: Martian Biosphere Colony Life Support
- Domain B: Subsea Hydrothermal Energy Grid
- Domain C: Orbital Constellation Satellite Relay
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class WorldRule:
    """A formal causal invariant or transition law governing physical microworld state."""
    rule_id: str
    name: str
    domain: str
    description: str
    validator: Callable[[Dict[str, Any], Dict[str, Any]], Tuple[bool, Optional[str]]]


class WorldRuleEngine:
    """Host-authoritative physical rule evaluation and conservation validator."""

    def __init__(self, domain: str):
        self.domain = domain
        self._rules: List[WorldRule] = []
        self._setup_domain_rules()

    def _setup_domain_rules(self):
        """Register domain-specific conservation and transition invariants."""
        if self.domain == "martian_biosphere":
            self._register_martian_rules()
        elif self.domain == "subsea_hydrothermal":
            self._register_subsea_rules()
        elif self.domain == "orbital_constellation":
            self._register_orbital_rules()
        else:
            raise ValueError(f"Unknown domain: {self.domain}")

    def _register_martian_rules(self):
        # Rule 1: Scrubber requires power bus capacity >= 25 kW
        def check_scrubber_power(state: Dict[str, Any], delta: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
            if delta.get("scrubber_state") == "ACTIVE":
                available = state.get("grid_power_available", 0) - state.get("grid_power_consumed", 0)
                if available < 25:
                    return False, "BREACH: Insufficient power for scrubber (requires 25 kW)"
            return True, None

        # Rule 2: Water line pressure must not exceed 150 bar
        def check_pressure_limit(state: Dict[str, Any], delta: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
            new_pressure = delta.get("water_line_pressure", state.get("water_line_pressure", 100))
            if new_pressure > 150:
                return False, f"BREACH: Water line pressure {new_pressure} bar exceeds 150 bar burst ceiling"
            return True, None

        # Rule 3: O2 level must stay above 19.0%
        def check_o2_floor(state: Dict[str, Any], delta: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
            new_o2 = delta.get("o2_level", state.get("o2_level", 21.0))
            if new_o2 < 19.0:
                return False, f"BREACH: O2 level {new_o2}% dropped below hypoxia limit (19.0%)"
            return True, None

        self._rules = [
            WorldRule("MB-R1", "ScrubberPowerRequirement", "martian_biosphere", "Scrubber requires 25kW available", check_scrubber_power),
            WorldRule("MB-R2", "WaterPressureBurstCeiling", "martian_biosphere", "Water pressure <= 150 bar", check_pressure_limit),
            WorldRule("MB-R3", "O2HypoxiaFloor", "martian_biosphere", "O2 level >= 19.0%", check_o2_floor),
        ]

    def _register_subsea_rules(self):
        # Rule 1: Turbine cavitation limit - pressure ratio must be >= 1.2
        def check_cavitation(state: Dict[str, Any], delta: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
            ratio = delta.get("cavitation_index", state.get("cavitation_index", 1.5))
            if ratio < 1.2:
                return False, f"BREACH: Turbine cavitation index {ratio} < 1.2 (destructive impeller vibration)"
            return True, None

        # Rule 2: Geothermal loop core temperature <= 350 C
        def check_core_temp(state: Dict[str, Any], delta: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
            temp = delta.get("core_temp_c", state.get("core_temp_c", 280))
            if temp > 350:
                return False, f"BREACH: Core temperature {temp}C exceeds 350C thermal runaway ceiling"
            return True, None

        # Rule 3: Bus load balance - consumption <= capacity
        def check_power_balance(state: Dict[str, Any], delta: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
            gen = delta.get("power_generation_kw", state.get("power_generation_kw", 200))
            load = delta.get("power_load_kw", state.get("power_load_kw", 150))
            if load > gen + 10:
                return False, f"BREACH: Subsea power overload: load {load} kW exceeds generation {gen} kW"
            return True, None

        self._rules = [
            WorldRule("SH-R1", "TurbineCavitationCeiling", "subsea_hydrothermal", "Cavitation index >= 1.2", check_cavitation),
            WorldRule("SH-R2", "CoreThermalCeiling", "subsea_hydrothermal", "Core temperature <= 350C", check_core_temp),
            WorldRule("SH-R3", "PowerBusBalance", "subsea_hydrothermal", "Load <= Generation", check_power_balance),
        ]

    def _register_orbital_rules(self):
        # Rule 1: Battery Depth of Discharge - charge >= 20%
        def check_battery_floor(state: Dict[str, Any], delta: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
            charge = delta.get("battery_soc_pct", state.get("battery_soc_pct", 80))
            if charge < 20:
                return False, f"BREACH: Battery SOC {charge}% dropped below 20% critical survival threshold"
            return True, None

        # Rule 2: Pointing error <= 0.05 degrees for active laser link
        def check_laser_pointing(state: Dict[str, Any], delta: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
            if delta.get("laser_link_state") == "ACTIVE":
                pointing_err = state.get("attitude_error_deg", 0.01)
                if pointing_err > 0.05:
                    return False, f"BREACH: Cannot establish laser link with attitude pointing error {pointing_err} > 0.05 deg"
            return True, None

        # Rule 3: Propellant mass conservation - cannot increase without refuel
        def check_prop_conservation(state: Dict[str, Any], delta: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
            new_prop = delta.get("propellant_kg", state.get("propellant_kg", 50.0))
            curr_prop = state.get("propellant_kg", 50.0)
            if new_prop > curr_prop and not state.get("refueling_docked", False):
                return False, "BREACH: Spontaneous propellant generation without docking (Conservation of Mass)"
            return True, None

        self._rules = [
            WorldRule("OC-R1", "BatteryCriticalFloor", "orbital_constellation", "Battery SOC >= 20%", check_battery_floor),
            WorldRule("OC-R2", "LaserPointingAccuracy", "orbital_constellation", "Attitude error <= 0.05 deg", check_laser_pointing),
            WorldRule("OC-R3", "PropellantConservation", "orbital_constellation", "Propellant mass <= previous", check_prop_conservation),
        ]

    def validate_action_transition(
        self,
        current_state: Dict[str, Any],
        proposed_delta: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """Evaluate all domain rules against the proposed transition delta."""
        for rule in self._rules:
            valid, reason = rule.validator(current_state, proposed_delta)
            if not valid:
                return False, reason
        return True, None

    def get_rule_summaries(self) -> List[str]:
        """Return compact string summaries of active rules for prompt construction."""
        return [f"[{r.rule_id} {r.name}: {r.description}]" for r in self._rules]
