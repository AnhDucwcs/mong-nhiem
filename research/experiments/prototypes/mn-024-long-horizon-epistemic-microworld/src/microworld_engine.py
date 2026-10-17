"""Host-Authoritative Long-Horizon Microworld Engine for MN-024.

Integrates:
- ConservationInvariantGuard: Pre-condition admission filtering.
- MultiResourceArbiter: Distributed TTL mutual exclusion leases.
- CausalEventDAG: Topological event history and provenance tracking.
- EnvironmentalEntropyEngine: Passive continuous thermodynamic/electrical decay.
- EpistemicMaskEngine: Subjective visibility projection and M10 groundedness checks.
"""

from __future__ import annotations

import copy
import sys
import os
from typing import Any, Dict, List, Optional, Set, Tuple

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(repo_root, "src"))

from mong_nhiem.core.invariants import ConservationInvariantGuard, InvariantViolationError
from mong_nhiem.core.vector_clock import VectorClock
from mong_nhiem.knowledge.causal_dag import CausalEventDAG, CausalNode
from mong_nhiem.orchestration.arbiter import MultiResourceArbiter
from entropy_engine import EnvironmentalEntropyEngine
from epistemic_mask import EpistemicMaskEngine


class LongHorizonMicroworldEngine:
    """Authoritative host environment executing multi-agent physical operations over extended horizons."""

    def __init__(
        self,
        domain_name: str,
        initial_entities: Dict[str, Dict[str, Any]],
        agent_ids: List[str],
        mask_engine: EpistemicMaskEngine,
        entropy_engine: Optional[EnvironmentalEntropyEngine] = None,
        max_ticks: int = 60,
    ) -> None:
        self.domain_name = domain_name
        self.entities = copy.deepcopy(initial_entities)
        self.agent_ids = agent_ids
        self.mask_engine = mask_engine
        self.entropy_engine = entropy_engine
        self.max_ticks = max_ticks
        self.current_tick = 0

        # Subsystems
        self.arbiter = MultiResourceArbiter(default_ttl=6)
        self.causal_dag = CausalEventDAG()
        self.vector_clock = VectorClock({aid: 0 for aid in agent_ids})

        # Telemetry & Auditing
        self.physical_breaches = 0
        self.race_collisions = 0
        self.groundedness_violations = 0
        self.total_actions_evaluated = 0
        self.mitigated_entities_this_tick: Set[str] = set()
        self.completed_hops: Set[int] = set()

    def advance_tick(self) -> Tuple[bool, List[str]]:
        """Advances simulation by 1 discrete tick, expiring leases and applying entropy decay."""
        self.arbiter.tick_cleanup(self.current_tick)

        breaches: List[str] = []
        if self.entropy_engine is not None:
            safe, tick_breaches = self.entropy_engine.apply_tick_decay(
                self.entities, self.mitigated_entities_this_tick
            )
            if not safe:
                self.physical_breaches += len(tick_breaches)
                breaches.extend(tick_breaches)

        self.mitigated_entities_this_tick.clear()
        self.current_tick += 1
        return len(breaches) == 0, breaches

    def verify_action_groundedness(
        self,
        agent_id: str,
        action_type: str,
        target_entity: str,
        params: Dict[str, Any],
    ) -> bool:
        """Verifies Clause M10: Agent acts solely on facts/secrets it has legitimately observed."""
        self.total_actions_evaluated += 1

        claimed_secret = params.get("secret_key") or params.get("passcode")
        if claimed_secret:
            known = self.mask_engine.known_secrets.get(agent_id, set())
            for sname, sval in self.mask_engine.private_secrets.items():
                if str(sval) == str(claimed_secret) and sname not in known:
                    self.groundedness_violations += 1
                    return False

        return True

    def step_action(
        self,
        agent_id: str,
        action_type: str,
        target_entity: str,
        params: Dict[str, Any],
        is_arm1_uncoordinated: bool = False,
    ) -> Tuple[bool, str, Optional[CausalNode]]:
        """Executes an action proposal with groundedness check, lease arbitration, and mutation."""
        # 1. Groundedness verification (M10)
        if not self.verify_action_groundedness(agent_id, action_type, target_entity, params):
            return False, "REJECTED_GROUNDEDNESS_VIOLATION", None

        # 2. Concurrency lease verification (M5)
        if not is_arm1_uncoordinated:
            held = self.arbiter.get_held_resources(agent_id)
            if action_type in ("ACT", "ISOLATE", "COUPLE", "ENGAGE", "MAINTAIN") and target_entity not in held:
                return False, f"REJECTED_UNAUTHORIZED_NO_LEASE:{target_entity}", None

        # 3. Target verification
        if target_entity not in self.entities:
            return False, f"REJECTED_NONEXISTENT_ENTITY:{target_entity}", None

        entity = self.entities[target_entity]
        delta: Dict[str, Any] = {}

        # 4. Action semantics
        if action_type == "INSPECT":
            self.mask_engine.grant_visibility(agent_id, target_entity)
            for secret_key, secret_val in self.mask_engine.private_secrets.items():
                if secret_key in entity:
                    self.mask_engine.grant_secret(agent_id, secret_key)
            self.completed_hops.add(1)
            delta = {"inspected": True}

        elif action_type == "MAINTAIN":
            # Active mitigation of entropy decay
            self.mitigated_entities_this_tick.add(target_entity)
            # Reset entity property to nominal baseline
            if "temperature" in entity:
                entity["temperature"] = 25.0
            if "pressure" in entity:
                entity["pressure"] = 101.3
            if "frequency" in entity:
                entity["frequency"] = 50.0
            delta = {"maintained": True}

        elif action_type == "ISOLATE":
            # Hop 2 in cascade
            entity["state"] = "ISOLATED"
            self.completed_hops.add(2)
            delta = {"state": "ISOLATED"}

        elif action_type == "COUPLE":
            # Hop 3 in cascade
            entity["state"] = "COUPLED"
            self.completed_hops.add(3)
            delta = {"state": "COUPLED"}

        elif action_type in ("ACT", "ENGAGE"):
            # Hop 4 in cascade: conditioned on secret
            required_secret_key = list(self.mask_engine.private_secrets.keys())[0]
            required_secret_val = self.mask_engine.private_secrets[required_secret_key]
            claimed = params.get("secret_key") or params.get("passcode")
            if str(claimed) == str(required_secret_val):
                entity["state"] = "UNLOCKED"
                self.completed_hops.add(4)
                delta = {"state": "UNLOCKED"}
            else:
                return False, "REJECTED_INVALID_CREDENTIAL", None

        # 5. Record Causal DAG node
        self.vector_clock.increment(agent_id)
        node = self.causal_dag.add_event(
            actor=agent_id,
            action_name=action_type,
            target_entity=target_entity,
            state_delta=delta,
            tick=self.current_tick,
        )

        return True, "COMMITTED", node

    def get_subjective_state(self, agent_id: str) -> Dict[str, Dict[str, Any]]:
        """Returns observation view for agent."""
        return self.mask_engine.project_subjective_view(agent_id, self.entities)

    def get_valid_affordances(self, agent_id: str, held_leases: Set[str]) -> List[str]:
        """Synthesizes valid affordances for agent."""
        affs: List[str] = []
        visible = self.mask_engine.agent_visibility.get(agent_id, set())

        for ent_name in visible:
            if ent_name in self.entities:
                if ent_name not in held_leases:
                    affs.append(f"ACTION: LEASE {ent_name}")
                else:
                    affs.append(f"ACTION: MAINTAIN {ent_name}")
                    affs.append(f"ACTION: ISOLATE {ent_name}")
                    affs.append(f"ACTION: COUPLE {ent_name}")
                    affs.append(f"ACTION: ENGAGE {ent_name}")
                    affs.append(f"ACTION: RELEASE {ent_name}")

        affs.append("ACTION: WAIT")
        return affs
