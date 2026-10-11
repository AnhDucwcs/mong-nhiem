"""Dynamic GBNF Affordance Compiler with Active Parametric Drift Adaptation.

Dynamically compiles Context-Free GBNF Grammars parameterizing allowed actions
strictly to the active sub-goal and current environmental drift state. Prunes
inviable actions under degraded parameters and injects safe compensatory affordances.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set

from discrepancy_monitor import DiscrepancyMonitor


class DynamicAffordanceCompiler:
    """Compiles GBNF grammar definitions enforcing active sub-goal and drift affordances."""

    # Compensatory action injection map when drift is detected
    COMPENSATORY_AFFORDANCES: Dict[str, List[str]] = {
        "solar_array": ["engage_auxiliary_cryo_pump"],
        "thermal_loop": ["engage_auxiliary_cryo_pump"],
        "battery_bank": ["engage_static_compensator"],
        "critical_bus": ["engage_static_compensator"],
        "reefer_unit": ["activate_emergency_cooling_pack"],
        "traction_motor": ["activate_emergency_cooling_pack"],
        "thermoelectric_gen": ["engage_cryo_heat_sink"],
        "depth_ballast": ["flush_salinity_sensor", "vent_ballast_chamber 20.0"],
    }

    # High-draw or risky actions pruned when relevant entity is degraded
    INVIABLE_UNDER_DRIFT: Dict[str, List[str]] = {
        "solar_array": ["divert_solar_power cryo_battery 100.0"],
        "thermal_loop": ["purge_cabin_heat 40.0", "boost_scrubber_oxygen 15.0"],
        "battery_bank": ["discharge_battery 30.0"],
        "critical_bus": ["discharge_battery 30.0"],
        "reefer_unit": ["adjust_traction_drive 80.0"],
        "traction_motor": ["adjust_traction_drive 80.0"],
        "thermoelectric_gen": ["throttle_hydrothermal_intake 50.0"],
        "depth_ballast": ["throttle_hydrothermal_intake 50.0"],
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
    ) -> str:
        """Compile a strict GBNF grammar factoring in active drift alerts.
        
        Args:
            allowed_actions: Base candidate actions for current phase.
            known_entity_ids: Entities eligible for ACTION: RECALL.
            allow_resolve: Whether ACTION: RESOLVE COMPLETE is permissible.
            allow_recall: Whether ACTION: RECALL is permitted.
            negative_actions: Banned actions (e.g. from Memento rollbacks).
            discrepancy_monitor: Optional active monitor indicating drift state.
            
        Returns:
            Valid GBNF grammar string.
        """
        candidate_set: Set[str] = set(allowed_actions)
        neg_set: Set[str] = set(negative_actions or [])

        # Active Drift Pruning & Compensatory Injection
        if discrepancy_monitor and discrepancy_monitor.active_alerts:
            for alert_key in list(discrepancy_monitor.active_alerts.keys()):
                eid = alert_key.split(":")[0]
                # Prune inviable actions under drift
                for inviable in cls.INVIABLE_UNDER_DRIFT.get(eid, []):
                    candidate_set.discard(inviable)
                # Inject compensatory affordances
                for comp_act in cls.COMPENSATORY_AFFORDANCES.get(eid, []):
                    candidate_set.add(comp_act)

        branches: List[str] = []

        # Action dispatch branches
        for act in sorted(candidate_set):
            if act in neg_set:
                continue
            safe_act = act.replace('"', '\\"')
            branches.append(f'"ACTION: DISPATCH {safe_act}"')

        # Recall branches (with active entity pruning)
        if allow_recall and known_entity_ids:
            for eid in sorted(set(known_entity_ids)):
                recall_act = f"RECALL {eid}"
                if recall_act in neg_set:
                    continue
                safe_eid = eid.replace('"', '\\"')
                branches.append(f'"ACTION: RECALL {safe_eid}"')

        # Resolve branch
        if allow_resolve:
            branches.append('"ACTION: RESOLVE COMPLETE"')

        if not branches:
            branches.append('"ACTION: RESOLVE COMPLETE"')

        branches_str = " | ".join(branches)

        return (
            f"root ::= action\n"
            f"action ::= {branches_str}\n"
        )
