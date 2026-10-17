"""Host Authoritative Microworld Engine for Milestone MN-025."""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from src.isomorphism_engine import DOMAIN_BINDINGS, FunctionalRole, IsomorphismEngine
from src.conflict_engine import CausalBeliefState, ConflictEngine
from src.stochastic_engine import StochasticEngine


@dataclass
class ResourceLease:
    resource_id: str
    holder: str
    acquired_tick: int
    ttl: int


class MicroworldEngine:
    """Authoritative Host Microworld governing physical state, 3-tier fact cards, and invariants."""

    def __init__(self, stage: int, domain_id: str, max_ticks: int = 40, is_regime_shift_scenario: bool = False):
        self.stage = stage
        self.domain_id = domain_id
        self.max_ticks = max_ticks
        self.is_regime_shift_scenario = is_regime_shift_scenario
        self.current_tick = 0
        self.is_resolved = False
        self.is_failed = False
        self.failure_reason: Optional[str] = None

        # Physical state
        self.world_state: Dict[str, Any] = {
            "core_temp": 280.0,
            "cabin_pressure": 101.3,
            "co2_ppm": 450.0,
            "grid_frequency": 50.0,
            "status": "INITIALIZING",
        }

        # Sub-engines
        self.stochastic = StochasticEngine()
        self.active_leases: Dict[str, ResourceLease] = {}
        self.tier1_anchors: List[str] = []
        self.tier2_frontier: List[str] = []
        self.tier3_negative_masks: Set[str] = set()

        # Epistemic Belief States for Stage 2
        self.belief_state_a = CausalBeliefState(agent_id="agent_alpha")
        self.belief_state_b = CausalBeliefState(agent_id="agent_beta")

        # Telemetry & Audit
        self.action_history: List[Dict[str, Any]] = []
        self.physical_breach_count = 0
        self.concurrency_collision_count = 0
        self.negative_transfer_breach_count = 0
        self.demotion_count = 0
        self.current_hop = 1  # 1: INSPECT, 2: ISOLATE/SEAL, 3: ENGAGE, 4: STABILIZE, 5: RESOLVE

        self._initialize_domain()

    def _initialize_domain(self) -> None:
        """Sets up domain-specific initial states and Tier 1 anchors."""
        binding = DOMAIN_BINDINGS.get(self.domain_id)
        if binding:
            if self.stage == 1:
                # Stage 1: Inject Topological Schema Card into Tier 1
                card = IsomorphismEngine.render_topological_schema_card(self.domain_id)
                self.tier1_anchors.append(card)
            elif self.stage == 2:
                # Stage 2: Initialize asymmetric beliefs
                self.belief_state_a.inferred_edges.add(("sensor_telemetry", "INDICATES", "HIGH_RISK_SHUTDOWN"))
                self.belief_state_b.inferred_edges.add(("sensor_telemetry", "INDICATES", "TRANSIENT_MAINTAIN_LOAD"))
                self.tier1_anchors.append("[CONSENSUS_POLICY: DIALECTIC_QUORUM_REQUIRED]")
            elif self.stage == 3:
                # Stage 3: Initial anchor subject to regime-shift demotion (Trap 3.2)
                self.tier1_anchors.append("[ANCHOR: aux_pump STABILIZES overheat [CONF: 1.0]]")

    def acquire_lease(self, resource_id: str, agent_id: str, ttl: int = 3) -> bool:
        """Optimistic resource lease acquisition under MultiResourceArbiter."""
        if resource_id in self.active_leases:
            lease = self.active_leases[resource_id]
            if lease.holder != agent_id and (self.current_tick - lease.acquired_tick) < lease.ttl:
                self.concurrency_collision_count += 1
                return False
        self.active_leases[resource_id] = ResourceLease(resource_id, agent_id, self.current_tick, ttl)
        return True

    def release_lease(self, resource_id: str, agent_id: str) -> None:
        """Releases resource lease."""
        if resource_id in self.active_leases and self.active_leases[resource_id].holder == agent_id:
            del self.active_leases[resource_id]

    def render_fact_card(self, agent_id: str = "agent_primary", target_arm: int = 3) -> Tuple[str, int]:
        """Renders 3-Tier Fact Card working prompt strictly bounded by <= 512 tokens."""
        if target_arm == 1:
            # Arm 1: Flat monolithic prompt without tiers
            lines = [f"System World State (Tick {self.current_tick}):"]
            for k, v in sorted(self.world_state.items()):
                lines.append(f"  {k}: {v}")
            lines.append("Actions:")
            for a in self.get_valid_affordances(target_arm=1):
                lines.append(f"  {a}")
            rendered = "\n".join(lines)
            tokens = max(len(rendered.split()), int(len(rendered) / 3.6))
            return rendered, tokens

        lines = [
            f"[AGENT: {agent_id}] [TICK: {self.current_tick}] [DOMAIN: {self.domain_id}]",
            "=== TIER 1: INVARIANT ANCHORS ===",
        ]
        for a in self.tier1_anchors:
            lines.append(f"  {a}")

        lines.append("=== TIER 2: CAUSAL FRONTIER ===")
        if not self.tier2_frontier:
            lines.append("  [FRONTIER: ALL_SYSTEMS_MONITORED]")
        else:
            for f in self.tier2_frontier[-4:]:
                lines.append(f"  {f}")

        lines.append("=== TIER 3: VALID AFFORDANCES ===")
        for aff in self.get_valid_affordances(target_arm=target_arm):
            lines.append(f"  {aff}")

        rendered = "\n".join(lines)
        tokens = max(len(rendered.split()), int(len(rendered) / 3.6))
        return rendered, tokens

    def get_valid_affordances(self, target_arm: int = 3) -> List[str]:
        """Returns dynamic valid actions menu filtered by Negative Masking and dynamic entities."""
        binding = DOMAIN_BINDINGS.get(self.domain_id)
        actions = []

        if target_arm == 1:
            # Arm 1: Flat monolithic list of all actions
            if binding:
                for role, act in binding.valid_actions.items():
                    ent = binding.role_to_entity[role]
                    actions.append(f"ACTION: {act} {ent}")
            if self.stage == 1:
                actions.append("ACTION: VENT pressure_relief")
            elif self.stage == 2:
                actions.append("ACTION: DEFER_MAINTENANCE filter")
            elif self.stage == 3:
                actions.append("ACTION: CYCLE_VALVE main_feed")
            actions.append("ACTION: WAIT")
            actions.append("ACTION: RESOLVE")
            return actions

        # Arm 2 & 3: Phased Affordance Gating
        if self.stage == 1 and binding:
            if self.current_hop == 1:
                s_ent = binding.role_to_entity[FunctionalRole.SENSOR]
                s_act = binding.valid_actions[FunctionalRole.SENSOR]
                actions.append(f"ACTION: {s_act} {s_ent}")
                actions.append("ACTION: VENT pressure_relief")  # Trap 1.1 temptation
                actions.append("ACTION: THROTTLE_UNREGULATED valve")  # Trap 1.3 temptation
            elif self.current_hop == 2:
                i_ent = binding.role_to_entity[FunctionalRole.ISOLATOR]
                i_act = binding.valid_actions[FunctionalRole.ISOLATOR]
                actions.append(f"ACTION: {i_act} {i_ent}")
            elif self.current_hop == 3:
                a_ent = binding.role_to_entity[FunctionalRole.ACTUATOR]
                a_act = binding.valid_actions[FunctionalRole.ACTUATOR]
                actions.append(f"ACTION: {a_act} {a_ent}")
            elif self.current_hop == 4:
                st_ent = binding.role_to_entity[FunctionalRole.STABILIZER]
                st_act = binding.valid_actions[FunctionalRole.STABILIZER]
                actions.append(f"ACTION: {st_act} {st_ent}")
            elif self.current_hop >= 5:
                actions.append("ACTION: RESOLVE")

        elif self.stage == 2:
            if self.current_hop == 1:
                actions.append("ACTION: CROSS_INSPECT telemetry")
                actions.append("ACTION: DEFER_MAINTENANCE filter")  # Trap 2.4 temptation
            elif self.current_hop >= 2:
                actions.append("ACTION: RESOLVE")

        elif self.stage == 3:
            if self.current_hop == 1:
                for ent_id in self.stochastic.dynamic_entities:
                    sig = self.stochastic.get_typed_affordance_signature(ent_id)
                    actions.append(sig)
                actions.append("ACTION: CYCLE_VALVE main_feed")  # Trap 3.4 temptation
            elif self.current_hop == 2:
                if binding:
                    st_ent = binding.role_to_entity[FunctionalRole.STABILIZER]
                    actions.append(f"ACTION: STABILIZE {st_ent}")
            elif self.current_hop >= 3:
                actions.append("ACTION: RESOLVE")

        # Filter against negative masks
        filtered_actions = [a for a in actions if a not in self.tier3_negative_masks]
        if "ACTION: RESOLVE" not in filtered_actions:
            filtered_actions.append("ACTION: WAIT")
        return filtered_actions

    def step(self, action_str: str, agent_id: str = "agent_primary") -> Tuple[bool, Optional[str]]:
        """Advances simulation by 1 discrete tick and verifies safety invariants."""
        self.current_tick += 1

        cleaned = action_str.strip()
        if cleaned.startswith("- "):
            cleaned = cleaned[2:].strip()
        elif cleaned.startswith("* "):
            cleaned = cleaned[2:].strip()
        if cleaned.startswith("ACTION:"):
            cleaned = cleaned[7:].strip()

        action_parts = cleaned.split()
        verb = action_parts[0] if action_parts else "WAIT"
        target = action_parts[1] if len(action_parts) > 1 else ""

        self.action_history.append({
            "tick": self.current_tick,
            "agent_id": agent_id,
            "action": action_str,
            "verb": verb,
            "target": target,
        })

        # 1. Immediate Negative Transfer Check (Stage 1)
        is_valid_transfer, neg_reason = IsomorphismEngine.validate_action(self.domain_id, verb, target)
        if not is_valid_transfer:
            self.negative_transfer_breach_count += 1
            self.tier3_negative_masks.add(action_str)
            self.tier2_frontier.append(f"[BLOCKED] {neg_reason}")
            return False, neg_reason

        # 2. Stage 3: Regime Shift & Non-Monotonic Anchor Demotion Check (Trap 3.2)
        should_shift = (self.is_regime_shift_scenario and self.current_tick == 2) or (self.current_tick == 15)
        if self.stage == 3 and should_shift and self.stochastic.active_regime == "NOMINAL":
            shift = self.stochastic.trigger_regime_shift("SUPERHEATED")
            # Demote from Tier 1 immediately
            self.tier1_anchors = [a for a in self.tier1_anchors if "aux_pump STABILIZES" not in a]
            self.tier2_frontier.append(shift["tombstone"])
            self.tier3_negative_masks.add("ACTION: ENGAGE aux_pump")
            self.demotion_count += 1
            self.current_hop = 1  # Reset to re-engage with dynamic backup

        # 3. Latent Time-Bomb Check (Traps 1.3, 1.4, 2.3, 2.4, 3.3, 3.4)
        active_actions = [h["action"] for h in self.action_history[-3:]]
        latent_breach, latent_reason = self.stochastic.update_latent_degradation(
            self.current_tick, active_actions, current_load=75.0
        )
        if latent_breach:
            self.physical_breach_count += 1
            self.is_failed = True
            self.failure_reason = latent_reason
            return False, latent_reason

        # 4. Standard Causal Progression & Resolution
        if verb == "RESOLVE":
            # Check if all invariant criteria met
            if self.physical_breach_count == 0 and not self.is_failed:
                self.is_resolved = True
                self.world_state["status"] = "RESOLVED"
                return True, "TASK_SUCCESSFULLY_RESOLVED"
            else:
                return False, "CANNOT_RESOLVE_WHILE_IN_BREACH"

        # Apply state effect and advance causal hop
        if verb == "INSPECT":
            self.current_hop = max(self.current_hop, 2)
            self.tier2_frontier.append(f"[INSPECTED: {target}. Anomaly confirmed]")
        elif verb in ("ISOLATE", "SEAL"):
            self.current_hop = max(self.current_hop, 3)
            self.tier2_frontier.append(f"[CAUSAL_PROGRESS: {target} ISOLATED]")
            self.world_state["core_temp"] -= 15.0
            self.world_state["co2_ppm"] -= 50.0
        elif verb == "CROSS_INSPECT":
            self.current_hop = max(self.current_hop, 2)
            self.tier2_frontier.append("[TELEMETRY_RECONCILED: Objective data confirmed]")
        elif verb == "ENGAGE":
            if self.stage == 1:
                self.current_hop = max(self.current_hop, 4)
            elif self.stage == 3:
                self.current_hop = max(self.current_hop, 2)
            self.tier2_frontier.append(f"[CAUSAL_PROGRESS: {target} ENGAGED]")
            self.world_state["core_temp"] = 275.0
            self.world_state["co2_ppm"] = 420.0
        elif verb == "STABILIZE":
            if self.stage == 1:
                self.current_hop = max(self.current_hop, 5)
            elif self.stage == 3:
                self.current_hop = max(self.current_hop, 3)
            self.tier2_frontier.append(f"[CAUSAL_PROGRESS: {target} STABILIZED]")
            self.world_state["core_temp"] = 270.0
            self.world_state["co2_ppm"] = 400.0

        return True, "ACTION_EXECUTED"
