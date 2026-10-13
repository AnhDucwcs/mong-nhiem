"""Host-Authoritative Discrete Microworld Runtime for MN-023.

Enforces:
- Physical conservation invariants (Clause M4: breaches == 0).
- Concurrency arbitration and race collision prevention (Clause M5: collisions == 0).
- Non-omniscient action groundedness checking (Clause M10: F_grounded == 100.0%).
- Multi-Parent Causal Event DAG logging with Vector Clock synchronization.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Set, Tuple

from mong_nhiem.core.invariants import ConservationInvariantGuard
from mong_nhiem.core.vector_clock import VectorClock
from mong_nhiem.knowledge.causal_dag import CausalEventDAG, CausalNode
from mong_nhiem.orchestration.arbiter import MultiResourceArbiter
try:
    from src.epistemic_mask import EpistemicMaskEngine
except ImportError:
    from epistemic_mask import EpistemicMaskEngine


class MicroworldEngine:
    """Authoritative physical simulation engine enforcing domain invariants and causality."""

    def __init__(
        self,
        domain_name: str,
        initial_entities: Dict[str, Dict[str, Any]],
        agent_ids: List[str],
        mask_engine: EpistemicMaskEngine,
        max_ticks: int = 30,
        invariant_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> None:
        self.domain_name = domain_name
        self.entities: Dict[str, Dict[str, Any]] = copy.deepcopy(initial_entities)
        self.agent_ids = agent_ids
        self.mask_engine = mask_engine
        self.max_ticks = max_ticks
        self.current_tick: int = 0

        # Subsystems from production mong_nhiem
        self.arbiter = MultiResourceArbiter(default_ttl=4)
        for eid in self.entities:
            self.arbiter.register_resource(eid)

        self.invariant_guard = ConservationInvariantGuard(invariant_bounds or {})
        self.causal_dag = CausalEventDAG()
        self.agent_clocks: Dict[str, VectorClock] = {
            aid: VectorClock({a: 0 for a in agent_ids}) for aid in agent_ids
        }
        self.agent_heads: Dict[str, str] = {}
        self.last_resource_events: Dict[str, str] = {}

        # Metric telemetry counters
        self.physical_breaches: int = 0
        self.race_collisions: int = 0
        self.groundedness_violations: int = 0
        self.total_actions_evaluated: int = 0
        self.is_resolved: bool = False

    def get_subjective_state(self, agent_id: str) -> Dict[str, Dict[str, Any]]:
        """Returns filtered world entities conforming to agent's observation mask."""
        return self.mask_engine.filter_state_for_agent(agent_id, self.entities)

    def verify_action_groundedness(
        self,
        agent_id: str,
        action_type: str,
        target_entity: str,
        params: Dict[str, Any],
    ) -> bool:
        """Verifies Clause M10: Agent only acts on facts/secrets it has legitimately observed."""
        self.total_actions_evaluated += 1

        # Check if action attempts to supply a secret parameter (e.g. passcode, private key)
        claimed_secret = params.get("secret_key") or params.get("passcode")
        if claimed_secret:
            known = self.mask_engine.known_secrets.get(agent_id, set())
            # If claimed secret is a true private secret but agent has not discovered it
            for sname, sval in self.mask_engine.private_secrets.items():
                if str(sval) == str(claimed_secret) and sname not in known:
                    self.groundedness_violations += 1
                    return False  # Telepathic/Omniscient action breach!

        return True

    def step_action(
        self,
        agent_id: str,
        action_type: str,
        target_entity: str,
        params: Dict[str, Any],
        is_arm1_uncoordinated: bool = False,
    ) -> Tuple[bool, str, Optional[CausalNode]]:
        """Executes a discrete action proposal with admission filtering and state mutation.
        
        Returns:
            Tuple[success_boolean, status_message, causal_node]
        """
        # 1. Groundedness check (M10)
        if not self.verify_action_groundedness(agent_id, action_type, target_entity, params):
            return False, "REJECTED_GROUNDEDNESS_VIOLATION", None

        # 2. Concurrency lease check (Arm 1 bypasses arbiter -> triggers race collision)
        if not is_arm1_uncoordinated:
            held = self.arbiter.get_held_resources(agent_id)
            if action_type in ("ACT", "UNLOCK", "ISOLATE", "ACTIVATE") and target_entity not in held:
                return False, f"REJECTED_UNAUTHORIZED_NO_LEASE:{target_entity}", None

        # 3. Check target existence
        if target_entity not in self.entities:
            return False, f"REJECTED_NONEXISTENT_ENTITY:{target_entity}", None

        entity = self.entities[target_entity]
        delta: Dict[str, Any] = {}
        mutation_ok = True

        # 4. Domain mutation logic
        if action_type == "INSPECT":
            # Reveals secret or clue if entity holds one
            for sname in self.mask_engine.private_secrets:
                if sname in entity:
                    self.mask_engine.grant_secret(agent_id, sname)
                    delta["revealed_secret"] = sname

        elif action_type in ("ACT", "UNLOCK", "ISOLATE", "ACTIVATE"):
            # Update entity state
            target_prop = params.get("property", "state")
            target_val = params.get("value", "OPERATIONAL")
            delta[target_prop] = target_val

            # Physical conservation check (M4)
            if isinstance(target_val, (int, float)):
                try:
                    self.invariant_guard.check_value(target_prop, float(target_val))
                except Exception:
                    self.physical_breaches += 1
                    mutation_ok = False

            if mutation_ok:
                entity[target_prop] = target_val

        if not mutation_ok:
            return False, "REJECTED_INVARIANT_BREACH", None

        # 5. Causal DAG logging and Vector Clock increment
        self.agent_clocks[agent_id].increment(agent_id)
        parent_ids: List[str] = []
        if agent_id in self.agent_heads:
            parent_ids.append(self.agent_heads[agent_id])
        if target_entity in self.last_resource_events:
            parent_ids.append(self.last_resource_events[target_entity])

        node = self.causal_dag.add_event(
            actor=agent_id,
            action_name=action_type,
            target_entity=target_entity,
            state_delta=delta,
            parent_ids=parent_ids,
            tick=self.current_tick,
        )

        self.agent_heads[agent_id] = node.event_id
        self.last_resource_events[target_entity] = node.event_id

        return True, "COMMITTED", node

    def advance_tick(self) -> int:
        """Advances simulation by one discrete tick and cleans up expired leases."""
        self.current_tick += 1
        self.arbiter.tick_cleanup(self.current_tick)
        return self.current_tick
