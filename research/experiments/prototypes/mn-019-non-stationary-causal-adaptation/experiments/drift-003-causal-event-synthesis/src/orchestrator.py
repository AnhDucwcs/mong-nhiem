"""Dual-Engine Cognitive Host Orchestrator with Proactive Causal Synthesis for Stage 3."""
from __future__ import annotations

import copy
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from autodream_engine import AutoDreamEngine
from causal_event_logger import CausalEventLog
from causal_synthesis_engine import CausalSynthesisEngine
from counterfactual_sandbox import CounterfactualSandbox
from discrepancy_monitor import DiscrepancyMonitor
from dynamic_affordance import DynamicAffordanceCompiler
from hierarchical_planner import HierarchicalPlanner, SubGoal
from memento_stack import MementoStack
from microworld_engine import SimulatedMicroworld
from proactive_affordance_gate import ProactiveAffordanceGate
from schema_evolution_engine import SchemaEvolutionRule


class DualEngineOrchestrator:
    """Coordinates cognitive host execution, proactive causal gating, and memory consolidation."""

    def __init__(
        self,
        domain: str,
        initial_entities: Dict[str, Any],
        subgoals: List[SubGoal],
        schema_rules: Optional[List[SchemaEvolutionRule]] = None,
        arm: str = "arm3_counterfactual_causal_host",
        max_turns: int = 30,
    ) -> None:
        self.domain = domain
        self.arm = arm
        self.max_turns = max_turns
        self.current_turn: int = 0

        self.event_logger = CausalEventLog()
        self.world = SimulatedMicroworld(
            domain=domain,
            initial_entities=initial_entities,
            schema_rules=schema_rules,
            event_logger=self.event_logger,
        )
        self.planner = HierarchicalPlanner(subgoals)
        self.memento = MementoStack()
        self.monitor = DiscrepancyMonitor()
        self.autodream = AutoDreamEngine(initial_entities=initial_entities)

        # Causal and sandbox engines
        self.causal_engine = CausalSynthesisEngine(domain=domain)
        self.sandbox = CounterfactualSandbox(causal_engine=self.causal_engine)
        self.proactive_gate = ProactiveAffordanceGate(sandbox=self.sandbox)

        # Metrics tracking
        self.banned_actions: List[str] = []
        self.executed_actions: List[str] = []
        self.committed_violations: int = 0
        self.proactive_bypasses: int = 0
        self.reactive_traps_hit: int = 0
        self.turn_latencies: List[float] = []
        self.prompt_token_counts: List[int] = []

    def get_active_viable_actions(self) -> Tuple[List[str], Set[str]]:
        """Returns (viable_actions, proactive_pruned_set) for the active sub-goal."""
        curr_sg = self.planner.current_subgoal
        if not curr_sg:
            return [], set()

        candidates = list(curr_sg.candidate_actions)
        if self.arm == "arm3_counterfactual_causal_host":
            viable, pruned_map, causal_cards = self.proactive_gate.filter_viable_actions(self.world, candidates)
            for card in causal_cards:
                self.autodream.add_causal_rule_card(card.split()[1], card)
            self.proactive_bypasses = self.proactive_gate.proactive_bypasses_count
            return viable, set(pruned_map.keys())

        return candidates, set()

    def get_active_grammar(self) -> Optional[str]:
        """Compile GBNF grammar for the current turn."""
        if self.arm == "arm1_flat":
            return None

        curr_sg = self.planner.current_subgoal
        allowed = list(curr_sg.candidate_actions) if curr_sg else []
        proactive_pruned: Set[str] = set()

        if self.arm == "arm3_counterfactual_causal_host":
            allowed, proactive_pruned = self.get_active_viable_actions()

        active_eids = {eid for eid, ent in self.world.entities.items() if ent.is_active}

        neg_actions = list(set(self.banned_actions + self.executed_actions))
        return DynamicAffordanceCompiler.compile_grammar(
            allowed_actions=allowed,
            known_entity_ids=list(self.world.entities.keys()),
            allow_resolve=self.planner.is_all_completed(),
            allow_recall=False,
            negative_actions=neg_actions,
            discrepancy_monitor=self.monitor,
            active_entities=active_eids,
            proactive_pruned_actions=proactive_pruned,
        )

    def render_prompt(self) -> str:
        """Render compact forward prompt bounded by 512 tokens."""
        curr_sg = self.planner.current_subgoal
        sg_text = (
            f"SUBGOAL {curr_sg.subgoal_id}: {curr_sg.description} "
            f"TARGET {curr_sg.target_entity}.{curr_sg.target_property} {curr_sg.operator} {curr_sg.target_value}"
            if curr_sg
            else "ALL SUBGOALS COMPLETED - EMIT 'ACTION: RESOLVE COMPLETE'"
        )

        memory_block = self.autodream.render_memory_block(max_cards=4)
        alerts_block = self.monitor.render_active_prompt_cards(max_cards=2)
        alerts_section = f"\nALERTS:\n{alerts_block}" if alerts_block else ""

        prompt = (
            f"<|im_start|>system\n"
            f"DOMAIN: {self.domain} TICK: {self.world.current_tick}\n"
            f"ACTIVE {sg_text}\n"
            f"DECLARATIVE MEMORY:\n{memory_block}"
            f"{alerts_section}\n"
            f"Instruction: Output exactly one action in format 'ACTION: DISPATCH <command>' or 'ACTION: RESOLVE COMPLETE'.<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        tokens = AutoDreamEngine.estimate_tokens(prompt)
        self.prompt_token_counts.append(tokens)
        return prompt

    def execute_turn(self, action_emission: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute a single cognitive turn."""
        start_time = time.perf_counter()
        self.current_turn += 1

        active_sg = self.planner.current_subgoal
        active_sg_id = active_sg.subgoal_id if active_sg else "NONE"

        # Check for task resolution
        if "ACTION: RESOLVE COMPLETE" in action_emission:
            latency = (time.perf_counter() - start_time) * 1000.0
            self.turn_latencies.append(latency)
            if self.planner.is_all_completed():
                return True, "RESOLVED_SUCCESSFULLY", {"type": "resolution", "completed": True}
            else:
                self.committed_violations += 1
                return False, "PREMATURE_RESOLUTION_INCOMPLETE", {"type": "resolution", "completed": False}

        # Parse action command
        match = re.search(r"ACTION:\s*DISPATCH\s+(.+)", action_emission.strip())
        raw_action = match.group(1).strip() if match else action_emission.strip()

        # Ingest into AutoDream raw history
        causal_evs = self.world.event_logger.events[-2:] if hasattr(self.world, "event_logger") else None
        self.autodream.ingest_turn(
            turn_num=self.current_turn,
            action=raw_action,
            world_state={eid: copy.deepcopy(e.properties) for eid, e in self.world.entities.items() if e.is_active},
            causal_events=causal_evs,
        )

        # Snapshot for Memento rollback in Arm 2 and Arm 3
        if self.arm in ("arm2_reactive_control", "arm3_counterfactual_causal_host"):
            self.memento.push(self.world.current_tick, self.world.entities, self.monitor.active_alerts)

        # In Arm 3, proactive gate verifies action again
        if self.arm == "arm3_counterfactual_causal_host":
            eval_res = self.sandbox.evaluate_hypothetical_action(self.world, raw_action)
            if not eval_res.is_viable:
                self.proactive_bypasses += 1
                self.banned_actions.append(raw_action)
                latency = (time.perf_counter() - start_time) * 1000.0
                self.turn_latencies.append(latency)
                return False, f"PROACTIVELY_PREEMPTED: {eval_res.breach_reason}", {
                    "type": "proactive_preempt",
                    "action": raw_action,
                    "active_subgoal": active_sg_id,
                }

        # Apply action transition in microworld
        is_ok, err_msg, post_state = self.world.execute_transition(raw_action)

        if not is_ok:
            self.reactive_traps_hit += 1
            if self.arm == "arm1_flat":
                self.committed_violations += 1
            elif self.arm == "arm2_reactive_control":
                # Reactive control hits trap, must roll back
                cp = self.memento.pop()
                if cp:
                    self.world.entities = copy.deepcopy(cp.entities)
                self.banned_actions.append(raw_action)
            elif self.arm == "arm3_counterfactual_causal_host":
                cp = self.memento.pop()
                if cp:
                    self.world.entities = copy.deepcopy(cp.entities)
                self.banned_actions.append(raw_action)

            latency = (time.perf_counter() - start_time) * 1000.0
            self.turn_latencies.append(latency)
            return False, f"BREACH: {err_msg}", {
                "type": "breach",
                "action": raw_action,
                "active_subgoal": active_sg_id,
            }

        # Progress hierarchical planner
        self.executed_actions.append(raw_action)
        advanced, completed_subgoal_id = self.planner.update_progress(self.world.entities)

        # Ingest schema alerts
        fired_schema = self.world.schema_engine.active_schema_alerts
        self.monitor.ingest_schema_events(fired_schema)

        # Update Fact Cards
        for eid, ent in self.world.entities.items():
            if ent.is_active:
                self.autodream.update_fact_card(eid, ent)

        latency = (time.perf_counter() - start_time) * 1000.0
        self.turn_latencies.append(latency)

        status_msg = f"ADVANCED_TO_{completed_subgoal_id}" if advanced else "ACTION_COMMITTED"
        return True, status_msg, {
            "type": "advance",
            "action": raw_action,
            "subgoal": completed_subgoal_id,
            "active_subgoal": active_sg_id,
        }

    def finalize(self) -> Dict[str, Any]:
        """Compile headline metrics and episode summary."""
        self.autodream.finalize(self.world.entities)
        compaction = self.autodream.get_compaction_ratio()

        mean_latency = (
            sum(self.turn_latencies) / float(len(self.turn_latencies))
            if self.turn_latencies else 0.0
        )
        max_prompt = max(self.prompt_token_counts) if self.prompt_token_counts else 0
        mean_prompt = (
            sum(self.prompt_token_counts) / float(len(self.prompt_token_counts))
            if self.prompt_token_counts else 0.0
        )

        is_success = (
            self.planner.is_all_completed()
            and self.committed_violations == 0
        )

        return {
            "is_success": is_success,
            "turns_executed": self.current_turn,
            "subgoals_completed": sum(1 for g in self.planner.subgoals if g.is_completed),
            "total_subgoals": len(self.planner.subgoals),
            "committed_violations": self.committed_violations,
            "proactive_bypasses": self.proactive_bypasses,
            "reactive_traps_hit": self.reactive_traps_hit,
            "compaction_ratio": compaction,
            "max_prompt_tokens": max_prompt,
            "mean_prompt_tokens": round(mean_prompt, 1),
            "mean_latency_ms": round(mean_latency, 2),
        }
