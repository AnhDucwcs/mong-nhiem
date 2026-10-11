"""Dynamic GBNF Affordance Compiler with Causal Proactive Gating for Stage 3.

Dynamically expands the Context-Free Grammar when novel entities emerge,
prunes affordances targeting decommissioned entities, and preemptively
masks actions that trigger latent causal traps.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set

from discrepancy_monitor import DiscrepancyMonitor


class DynamicAffordanceCompiler:
    """Compiles dynamic GBNF grammars adapting to structural shifts and causal risks."""

    EMERGENT_AFFORDANCES: Dict[str, List[str]] = {
        "aux_cooler": ["activate_secondary_cooler"],
        "secondary_feeder": ["connect_secondary_feeder"],
        "flywheel_reserve": ["sync_flywheel_reserve"],
        "booster_trailer": ["engage_booster_trailer"],
        "aux_vent": ["open_auxiliary_vent_hatch"],
        "mineral_beacon": ["calibrate_mineral_beacon"],
    }

    ENTITY_TARGETED_ACTIONS: Dict[str, List[str]] = {
        "aux_cooler": ["activate_secondary_cooler"],
        "secondary_feeder": ["connect_secondary_feeder"],
        "flywheel_reserve": ["sync_flywheel_reserve"],
        "booster_trailer": ["engage_booster_trailer"],
        "aux_vent": ["open_auxiliary_vent_hatch"],
        "mineral_beacon": ["calibrate_mineral_beacon"],
        "thermal_loop": ["purge_cabin_heat 10.0", "purge_cabin_heat 40.0", "engage_auxiliary_cryo_pump"],
        "cryo_battery": ["divert_solar_power cryo_battery 60.0", "divert_solar_power cryo_battery 80.0"],
        "battery_bank": ["discharge_battery 30.0"],
        "critical_bus": ["engage_static_compensator"],
        "wind_turbine": ["regulate_wind_pitch 20.0", "regulate_wind_pitch 30.0"],
        "reefer_unit": ["chill_reefer_compartment 2.0", "chill_reefer_compartment 5.0", "activate_emergency_cooling_pack"],
        "traction_motor": ["adjust_traction_drive 40.0", "adjust_traction_drive 50.0"],
        "thermoelectric_gen": ["throttle_hydrothermal_intake 50.0", "engage_cryo_heat_sink"],
        "depth_ballast": ["vent_ballast_chamber 10.0", "vent_ballast_chamber 20.0"],
        "salinity_sensor": ["flush_salinity_sensor"],
    }

    @classmethod
    def compile_grammar(
        cls,
        allowed_actions: List[str],
        known_entity_ids: List[str],
        allow_resolve: bool = False,
        allow_recall: bool = True,
        negative_actions: Optional[List[str]] = None,
        discrepancy_monitor: Optional[DiscrepancyMonitor] = None,
        active_entities: Optional[Set[str]] = None,
        proactive_pruned_actions: Optional[Set[str]] = None,
    ) -> str:
        """Compile strict GBNF grammar with dynamic emergence and proactive causal gating."""
        effective_actions = list(allowed_actions)
        banned = set(negative_actions or [])
        if proactive_pruned_actions:
            banned.update(proactive_pruned_actions)

        # 1. Expand grammar for active emerged entities
        if active_entities:
            for eid in active_entities:
                if eid in cls.EMERGENT_AFFORDANCES:
                    for aff in cls.EMERGENT_AFFORDANCES[eid]:
                        if aff not in effective_actions and aff not in banned:
                            effective_actions.append(aff)

        # 2. Prune actions targeting non-active/retired entities
        if active_entities is not None:
            filtered = []
            for act in effective_actions:
                target_eid = None
                for eid, acts in cls.ENTITY_TARGETED_ACTIONS.items():
                    if act in acts:
                        target_eid = eid
                        break
                if target_eid and target_eid not in active_entities:
                    continue
                filtered.append(act)
            effective_actions = filtered

        # 3. Apply negative and proactive steering
        effective_actions = [a for a in effective_actions if a not in banned]

        # 4. Construct GBNF rules
        action_alts: List[str] = []
        for act in effective_actions:
            action_alts.append(f'"ACTION: DISPATCH " "{act}"')

        if allow_resolve:
            action_alts.append('"ACTION: RESOLVE COMPLETE"')

        if allow_recall and known_entity_ids:
            recallable = [eid for eid in known_entity_ids if active_entities is None or eid in active_entities]
            if recallable:
                entity_rule = " | ".join(f'"{eid}"' for eid in sorted(recallable))
                action_alts.append(f'"ACTION: RECALL " ({entity_rule})')

        if not action_alts:
            action_alts.append('"ACTION: RESOLVE COMPLETE"')

        alts_str = " | ".join(action_alts)
        return (
            f"root ::= ({alts_str}) [\\n]?\n"
        )
