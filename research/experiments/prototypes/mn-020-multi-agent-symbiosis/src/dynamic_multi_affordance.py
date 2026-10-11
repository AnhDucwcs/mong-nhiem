"""Dynamic Multi-Agent GBNF Grammar Compiler.

Compiles strict Context-Free Grammars per agent per turn, dynamically masking out
contested entities leased to peer agents and injecting discrete coordination signals.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set

from concurrency_arbiter import ConcurrencyArbiter


class DynamicMultiAffordanceCompiler:
    """Compiles agent-specific GBNF grammars enforcing host concurrency leases."""

    # Action prefix to targeted entity mapping
    ACTION_TARGET_ENTITIES: Dict[str, str] = {
        "regulate_wind_pitch": "wind_turbine",
        "charge_battery_storage": "battery_bank",
        "discharge_battery_storage": "battery_bank",
        "shed_industrial_feeder": "industrial_feeder",
        "engage_static_compensator": "statcom",
        "fire_rcs_attitude": "rcs_thruster",
        "align_solar_gimbal": "solar_array",
        "purge_coolant_loop": "thermal_radiator",
        "lock_docking_latch": "docking_adapter",
        "route_haul_convoy": "convoy_a",
        "refrigerate_cargo_bay": "reefer_b",
        "queue_fast_charger": "charging_hub",
    }

    @classmethod
    def compile_agent_grammar(
        cls,
        agent_id: str,
        allowed_actions: List[str],
        arbiter: ConcurrencyArbiter,
        current_tick: int,
        known_entity_ids: List[str],
        peer_agent_id: Optional[str] = None,
        allow_resolve: bool = False,
        stagnant_actions: Optional[Set[str]] = None,
    ) -> str:
        """Compile strict GBNF grammar for agent_id at current_tick."""
        effective_actions: List[str] = []
        stagnant = stagnant_actions or set()

        # 1. Filter actions targeting contested entities leased to peer
        for act in allowed_actions:
            if act in stagnant:
                continue

            verb = act.strip().split()[0]
            target_entity = cls.ACTION_TARGET_ENTITIES.get(verb)

            if target_entity:
                holder = arbiter.get_lease_holder(target_entity, current_tick)
                if holder and holder != agent_id:
                    # Contested! Prune action from this agent's grammar
                    continue

            effective_actions.append(act)

        # 2. Build GBNF alternatives
        action_alts: List[str] = []
        for act in effective_actions:
            action_alts.append(f'"ACTION: DISPATCH {act}"')

        # 3. Add Coordination Affordances
        # a) Lease Acquisition for contested or critical entities
        if known_entity_ids:
            unleased = [
                eid for eid in known_entity_ids
                if arbiter.get_lease_holder(eid, current_tick) is None
            ]
            if unleased:
                e_rule = " | ".join(f'"{eid}"' for eid in sorted(unleased))
                action_alts.append(f'"ACTION: ACQUIRE_LEASE " ({e_rule})')

        # b) Lease Yielding for entities currently held by this agent
        held = [
            eid for eid, lease in arbiter.leases.items()
            if lease.holder_id == agent_id and not lease.is_expired(current_tick)
        ]
        if held:
            h_rule = " | ".join(f'"{eid}"' for eid in sorted(held))
            action_alts.append(f'"ACTION: YIELD_LEASE " ({h_rule})')

        # c) Inter-Agent Signalling (discrete, non-chatty)
        if peer_agent_id:
            sig_types = '"YIELD_REQUEST" | "LEASE_GRANTED" | "PHASE_SYNC" | "STANDBY"'
            action_alts.append(f'"ACTION: SIGNAL {peer_agent_id} " ({sig_types})')

        # d) Resolution
        if allow_resolve:
            action_alts.append('"ACTION: RESOLVE COMPLETE"')

        # 4. Non-deadlocking Fallback Invariant
        if not action_alts:
            if peer_agent_id:
                action_alts.append(f'"ACTION: SIGNAL {peer_agent_id} STANDBY"')
            else:
                action_alts.append('"ACTION: RESOLVE COMPLETE"')

        root_rule = " | ".join(action_alts)
        grammar = (
            "root ::= action\n"
            f"action ::= {root_rule}\n"
        )
        return grammar
