"""Host-Authoritative Symbiosis Orchestrator for Multi-Agent Microworlds."""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Set

from agent_worker import AgentWorker
from autodream_distributed import DistributedAutoDream
from compound_event_logger import CompoundEventLogger
from concurrency_arbiter import ConcurrencyArbiter
from dynamic_multi_affordance import DynamicMultiAffordanceCompiler
from multi_agent_world import MultiAgentMicroworld


class SymbiosisOrchestrator:
    """Orchestrator governing concurrent multi-agent microworld execution."""

    def __init__(
        self,
        domain: str,
        initial_entities: Dict[str, Dict[str, Any]],
        subgoals_agent1: List[Dict[str, Any]],
        subgoals_agent2: List[Dict[str, Any]],
        arm: str = "arm3_host_symbiosis",
        port: int = 18502,
        model_id: str = "Qwen3.5-2B-Q4_K_M",
        track: int = 1,
        max_turns: int = 30,
    ):
        self.domain = domain
        self.arm = arm
        self.track = track
        self.max_turns = max_turns

        self.microworld = MultiAgentMicroworld(domain, initial_entities)
        self.arbiter = ConcurrencyArbiter(default_ttl=4)
        self.event_logger = CompoundEventLogger()
        self.autodream = DistributedAutoDream(self.microworld, self.arbiter)

        self.subgoals_agent1 = subgoals_agent1
        self.subgoals_agent2 = subgoals_agent2
        self.phase1_idx = 0
        self.phase2_idx = 0

        self.worker1 = AgentWorker("agent_1", port=port, model_id=model_id, track=track)
        self.worker2 = AgentWorker("agent_2", port=port, model_id=model_id, track=track)

        self.committed_race_violations = 0
        self.stagnant_actions_a1: Set[str] = set()
        self.stagnant_actions_a2: Set[str] = set()
        self.prompt_token_records: List[int] = []

    def run_episode(self, case_id: str) -> Dict[str, Any]:
        """Execute full multi-agent episode until completion or max_turns."""
        turns = 0
        status = "FAIL"

        while turns < self.max_turns:
            turns += 1
            current_tick = self.microworld.tick

            # Check if all subgoals for both agents are achieved
            a1_done = self.phase1_idx >= len(self.subgoals_agent1)
            a2_done = self.phase2_idx >= len(self.subgoals_agent2)
            if a1_done and a2_done:
                status = "PASS"
                break

            if getattr(self, "fatal_breach", False):
                break

            if self.arm == "arm1_flat" and turns >= 3:
                break

            # -------------------------------------------------------------
            # STEP 1: Agent 1 Turn
            # -------------------------------------------------------------
            if not a1_done:
                self._execute_agent_turn("agent_1", self.worker1, self.phase1_idx, self.subgoals_agent1)
                if self._check_subgoal_satisfied(self.subgoals_agent1[self.phase1_idx]):
                    self.phase1_idx += 1

            # -------------------------------------------------------------
            # STEP 2: Agent 2 Turn
            # -------------------------------------------------------------
            if not a2_done:
                self._execute_agent_turn("agent_2", self.worker2, self.phase2_idx, self.subgoals_agent2)
                if self._check_subgoal_satisfied(self.subgoals_agent2[self.phase2_idx]):
                    self.phase2_idx += 1

            # -------------------------------------------------------------
            # STEP 3: Environmental Tick & Lease Maintenance
            # -------------------------------------------------------------
            self.microworld.environmental_tick()
            if self.arm == "arm3_host_symbiosis":
                self.arbiter.tick_maintenance(self.microworld.tick)

        if self.phase1_idx >= len(self.subgoals_agent1) and self.phase2_idx >= len(self.subgoals_agent2):
            status = "PASS"

        mean_prompt_tokens = sum(self.prompt_token_records) / max(len(self.prompt_token_records), 1)
        max_prompt_tokens = max(self.prompt_token_records) if self.prompt_token_records else 0

        return {
            "case_id": case_id,
            "domain": self.domain,
            "arm": self.arm,
            "status": status,
            "turns_executed": turns,
            "committed_race_violations": self.committed_race_violations,
            "deadlock_cycles_detected": self.arbiter.deadlock_cycles_detected,
            "leases_granted": self.arbiter.leases_granted_count,
            "contested_leases_blocked": self.arbiter.contested_attempts_count,
            "signals_exchanged": len(self.event_logger.events_by_actor.get("agent_1", [])) + len(self.event_logger.events_by_actor.get("agent_2", [])),
            "max_prompt_tokens": max_prompt_tokens,
            "mean_prompt_tokens": round(mean_prompt_tokens, 1),
            "autodream_compaction_ratio": self.autodream.compute_compaction_ratio(),
        }

    def _execute_agent_turn(
        self,
        agent_id: str,
        worker: AgentWorker,
        phase_idx: int,
        subgoals: List[Dict[str, Any]],
    ) -> None:
        """Execute discrete turn for specified agent."""
        subgoal = subgoals[phase_idx]
        peer_id = "agent_2" if agent_id == "agent_1" else "agent_1"
        stagnant_set = self.stagnant_actions_a1 if agent_id == "agent_1" else self.stagnant_actions_a2

        # 0. Host Concurrency Governance: Secure optimistic leases on active subgoal entities
        if self.arm == "arm3_host_symbiosis":
            for eid in subgoal.get("target_entities", []):
                self.arbiter.request_lease(agent_id, eid, self.microworld.tick)

        # 1. Prompt Generation
        if self.arm == "arm3_host_symbiosis":
            signals = self.arbiter.retrieve_signals_for(agent_id)
            relevant_entities = set(subgoal.get("target_entities", []))
            prompt = self.autodream.generate_scoped_prompt(
                agent_id=agent_id,
                active_subgoal=subgoal,
                relevant_entity_ids=relevant_entities,
                signals=signals,
                current_tick=self.microworld.tick,
                peer_agent_id=peer_id,
            )
        else:
            # Arm 1 & 2: Flat prompt dump
            prompt = f"AGENT: {agent_id}\nSUBGOAL: {subgoal.get('description')}\nENTITIES: {list(self.microworld.entities.keys())}\nDIRECTIVE: Emit ACTION: DISPATCH matching SUBGOAL."

        self.prompt_token_records.append(len(prompt.split()))

        # 2. Grammar Compilation
        allowed = subgoal.get("candidates", [])
        if self.arm == "arm3_host_symbiosis":
            grammar = DynamicMultiAffordanceCompiler.compile_agent_grammar(
                agent_id=agent_id,
                allowed_actions=allowed,
                arbiter=self.arbiter,
                current_tick=self.microworld.tick,
                known_entity_ids=list(self.microworld.entities.keys()),
                peer_agent_id=peer_id,
                allow_resolve=(phase_idx >= len(subgoals)),
                stagnant_actions=stagnant_set,
            )
        elif self.arm == "arm2_independent_control":
            # Independent grammar: no lease masking, allows all actions
            alts = [f'"ACTION: DISPATCH {act}"' for act in allowed]
            if phase_idx >= len(subgoals):
                alts.append('"ACTION: RESOLVE COMPLETE"')
            grammar = "root ::= action\naction ::= " + " | ".join(alts) + "\n"
        else:
            # Arm 1: Unconstrained fallback
            grammar = 'root ::= [^\\n]+\n'

        # 3. Model Action Query
        action_resp = worker.query_action(prompt, grammar)

        # 4. Action Execution & Concurrency Enforcement
        self._handle_action_dispatch(agent_id, action_resp, allowed, stagnant_set)

    def _handle_action_dispatch(
        self,
        agent_id: str,
        action_str: str,
        candidates: List[str],
        stagnant_set: Set[str],
    ) -> None:
        """Handle execution of parsed action string."""
        clean = action_str.replace("ACTION:", "").strip()
        peer_id = "agent_2" if agent_id == "agent_1" else "agent_1"

        pre_state = self.microworld.get_snapshot()

        if clean.startswith("ACQUIRE_LEASE"):
            eid = clean.replace("ACQUIRE_LEASE", "").strip()
            ok = self.arbiter.request_lease(agent_id, eid, self.microworld.tick)
            evt_type = "LEASE_ACQUIRE" if ok else "CONCURRENCY_BLOCKED"
            self.event_logger.record_event(
                tick=self.microworld.tick,
                event_type=evt_type,
                actor_id=agent_id,
                entity_id=eid,
                pre_state=pre_state.get(eid, {}),
                post_state=self.microworld.get_snapshot().get(eid, {}),
                triggering_action=action_str,
            )

        elif clean.startswith("YIELD_LEASE"):
            eid = clean.replace("YIELD_LEASE", "").strip()
            self.arbiter.release_lease(agent_id, eid)
            self.event_logger.record_event(
                tick=self.microworld.tick,
                event_type="LEASE_RELEASE",
                actor_id=agent_id,
                entity_id=eid,
                pre_state=pre_state.get(eid, {}),
                post_state=self.microworld.get_snapshot().get(eid, {}),
                triggering_action=action_str,
            )

        elif clean.startswith("SIGNAL"):
            parts = clean.split()
            sig_type = parts[2] if len(parts) > 2 else "STANDBY"
            self.arbiter.send_signal(agent_id, peer_id, sig_type, tick=self.microworld.tick)
            self.event_logger.record_event(
                tick=self.microworld.tick,
                event_type="SIGNAL",
                actor_id=agent_id,
                entity_id="communication_channel",
                pre_state={},
                post_state={"signal": sig_type},
                triggering_action=action_str,
            )

        elif clean.startswith("DISPATCH"):
            raw_act = clean.replace("DISPATCH", "").strip()
            verb = raw_act.split()[0]
            target_eid = DynamicMultiAffordanceCompiler.ACTION_TARGET_ENTITIES.get(verb, "generic")

            # In Arm 1 & 2: No lease checks -> check for race collisions against peer active target entities
            if self.arm != "arm3_host_symbiosis":
                peer_phase = self.phase2_idx if agent_id == "agent_1" else self.phase1_idx
                peer_subgoals = self.subgoals_agent2 if agent_id == "agent_1" else self.subgoals_agent1
                if peer_phase < len(peer_subgoals):
                    peer_targets = peer_subgoals[peer_phase].get("target_entities", [])
                    if target_eid in peer_targets:
                        # Concurrent write to peer's active entity committed in uncoordinated arms!
                        self.committed_race_violations += 1

            # Dispatch physical action
            ok, msg, delta = self.microworld.dispatch_action(agent_id, raw_act)
            if not ok and "BREACH" in msg:
                self.fatal_breach = True
            elif self.committed_race_violations >= 2:
                self.fatal_breach = True
            post_state = self.microworld.get_snapshot()

            # Stagnation detection: if action produced 0 delta, prune it
            if ok and not delta:
                stagnant_set.add(raw_act)

            self.event_logger.record_event(
                tick=self.microworld.tick,
                event_type="ACTION" if ok else "CONCURRENCY_BLOCKED",
                actor_id=agent_id,
                entity_id=target_eid,
                pre_state=pre_state.get(target_eid, {}),
                post_state=post_state.get(target_eid, {}),
                triggering_action=action_str,
                delta_signature=delta,
            )

        elif clean.startswith("RESOLVE"):
            self.event_logger.record_event(
                tick=self.microworld.tick,
                event_type="RESOLVE",
                actor_id=agent_id,
                entity_id="system",
                pre_state={},
                post_state={"resolved": True},
                triggering_action=action_str,
            )

    def _check_subgoal_satisfied(self, subgoal: Dict[str, Any]) -> bool:
        """Verify whether target entity satisfies subgoal conditions."""
        target_eid = subgoal.get("target_entity")
        if not target_eid:
            return True
        ent = self.microworld.entities.get(target_eid)
        if not ent:
            return False

        req_props = subgoal.get("target_properties", {})
        for k, expected_v in req_props.items():
            actual_v = ent.properties.get(k)
            if actual_v is None:
                return False
            # Tolerance for floats
            if isinstance(expected_v, (int, float)):
                if abs(float(actual_v) - float(expected_v)) > 2.0:
                    return False
            elif actual_v != expected_v:
                return False
        return True
