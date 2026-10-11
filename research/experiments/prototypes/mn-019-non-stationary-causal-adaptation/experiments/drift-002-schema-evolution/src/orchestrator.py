"""Dual-Engine Cognitive Host Orchestrator for Stage 2.

Coordinates real-time microworld execution, schema evolution monitoring, dynamic
GBNF affordance expansion/pruning, relational AutoDream memory, and Memento rollback.
"""
from __future__ import annotations

import copy
import time
from typing import Any, Dict, List, Optional, Tuple

from autodream_engine import AutoDreamEngine
from discrepancy_monitor import DiscrepancyMonitor
from dynamic_affordance import DynamicAffordanceCompiler
from hierarchical_planner import HierarchicalPlanner, SubGoal
from memento_stack import MementoStack
from microworld_engine import SimulatedMicroworld, WorldEntity
from schema_evolution_engine import SchemaEvolutionRule


class DualEngineOrchestrator:
    """Cognitive Orchestrator governing SLM execution under dynamic schema evolution."""

    def __init__(
        self,
        domain: str,
        initial_entities: Dict[str, Any],
        subgoals: List[SubGoal],
        schema_rules: Optional[List[SchemaEvolutionRule]] = None,
        arm: str = "arm3_dynamic_schema_host",
        max_turns: int = 30,
    ) -> None:
        self.domain = domain
        self.arm = arm
        self.max_turns = max_turns
        self.current_turn: int = 0

        # Sub-components
        self.world = SimulatedMicroworld(
            domain=domain,
            initial_entities=initial_entities,
            schema_rules=schema_rules,
        )
        self.planner = HierarchicalPlanner(subgoals)
        self.monitor = DiscrepancyMonitor()
        self.autodream = AutoDreamEngine(initial_entities=initial_entities)
        self.memento = MementoStack()

        # Telemetry & metrics
        self.banned_actions: List[str] = []
        self.executed_actions: List[str] = []
        self.committed_schema_violations: int = 0
        self.committed_conservation_breaches: int = 0
        self.intercepted_traps: int = 0
        self.turn_latencies: List[float] = []
        self.prompt_token_counts: List[int] = []

        # Store initial entity keys for Arm 2 static baseline
        self.initial_entity_ids = list(initial_entities.keys())

    def get_forward_prompt_and_grammar(self) -> Tuple[str, str]:
        """Compile prompt and GBNF grammar according to experimental arm."""
        active_sg = self.planner.current_subgoal
        subgoal_desc = active_sg.description if active_sg else "All sub-goals satisfied."
        candidate_actions = active_sg.candidate_actions if active_sg else []

        active_eids = {eid for eid, ent in self.world.entities.items() if ent.is_active}

        # 1. Grammar compilation
        neg_actions = list(set(self.banned_actions or []))
        if self.arm == "arm1_flat":
            # Flat: unconstrained grammar
            grammar = None
        elif self.arm == "arm2_static_schema_control":
            # Static: fixed to t=0 initial entities, blind to emergent ones, unaware of retirement
            grammar = DynamicAffordanceCompiler.compile_grammar(
                allowed_actions=candidate_actions,
                known_entity_ids=self.initial_entity_ids,
                allow_resolve=self.planner.is_all_completed(),
                allow_recall=False,
                negative_actions=neg_actions,
                discrepancy_monitor=None,
                active_entities=set(self.initial_entity_ids),  # Fixed static set
            )
        else:
            # Arm 3: Dynamic Schema Evolution Host
            grammar = DynamicAffordanceCompiler.compile_grammar(
                allowed_actions=candidate_actions,
                known_entity_ids=list(self.world.entities.keys()),
                allow_resolve=self.planner.is_all_completed(),
                allow_recall=False,
                negative_actions=neg_actions,
                discrepancy_monitor=self.monitor,
                active_entities=active_eids,  # Dynamic active set
            )

        # 2. Prompt construction
        memory_block = self.autodream.render_memory_block(max_cards=6)
        schema_alerts = self.monitor.render_active_prompt_cards(max_cards=3) if self.arm == "arm3_dynamic_schema_host" else ""

        banned_str = f"\nBANNED ACTIONS (Memento Masked): {self.banned_actions}" if (self.banned_actions and self.arm == "arm3_dynamic_schema_host") else ""
        alert_str = f"\n{schema_alerts}" if schema_alerts else ""

        prompt = (
            f"=== DOMAIN: {self.domain} | TURN {self.current_turn + 1} | ACTIVE SUB-GOAL: {subgoal_desc} ===\n"
            f"MEMORY:\n{memory_block}\n"
            f"{alert_str}"
            f"{banned_str}\n"
            f"INSTRUCTION: Select the optimal valid protocol action to achieve the active sub-goal."
        )

        tokens = int(len(prompt.split()) * 1.3)
        self.prompt_token_counts.append(tokens)
        return prompt, grammar

    def execute_turn(self, action_emission: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Process agent action emission with Host invariant gating and Memento rollback."""
        start_time = time.perf_counter()
        self.current_turn += 1

        active_sg_id = self.planner.current_subgoal.subgoal_id if self.planner.current_subgoal else None

        # Check for mission resolution
        if "ACTION: RESOLVE COMPLETE" in action_emission:
            latency = (time.perf_counter() - start_time) * 1000.0
            self.turn_latencies.append(latency)
            if self.planner.is_all_completed():
                return True, "RESOLVED_SUCCESSFULLY", {
                    "type": "resolve",
                    "action": "ACTION: RESOLVE COMPLETE",
                    "active_subgoal": active_sg_id,
                }
            else:
                return False, "PREMATURE_RESOLUTION_FAILURE", {
                    "type": "error",
                    "action": "ACTION: RESOLVE COMPLETE",
                    "active_subgoal": active_sg_id,
                }

        # Parse action payload
        raw_action = action_emission.replace("ACTION: DISPATCH ", "").strip()
        if action_emission.startswith("ACTION: RECALL "):
            eid = action_emission.replace("ACTION: RECALL ", "").strip()
            latency = (time.perf_counter() - start_time) * 1000.0
            self.turn_latencies.append(latency)
            card = self.autodream.fact_cards.get(eid, f"[UNKNOWN ENTITY {eid}]")
            return True, f"RECALLED: {card}", {
                "type": "recall",
                "entity": eid,
                "active_subgoal": active_sg_id,
            }

        # Check for Memento push in Arm 3
        if self.arm == "arm3_dynamic_schema_host":
            self.memento.push(
                tick=self.world.current_tick,
                entities=self.world.entities,
                active_alerts=self.monitor.active_alerts,
            )

        # Execute physical and schema transition in Microworld
        is_ok, err_msg, new_state = self.world.execute_transition(raw_action)

        # Ingest turn into AutoDream
        self.autodream.ingest_turn(
            turn_num=self.current_turn,
            action=raw_action,
            world_state=new_state,
        )

        # Handle violations / failures
        if not is_ok:
            is_schema_err = err_msg and "SCHEMA_VIOLATION" in err_msg
            if is_schema_err:
                self.committed_schema_violations += 1
            else:
                self.committed_conservation_breaches += 1

            self.intercepted_traps += 1

            # Rollback in Arm 3
            if self.arm == "arm3_dynamic_schema_host":
                checkpoint = self.memento.pop()
                if checkpoint:
                    self.world.entities = copy.deepcopy(checkpoint.entities)
                self.banned_actions.append(raw_action)

            latency = (time.perf_counter() - start_time) * 1000.0
            self.turn_latencies.append(latency)
            return False, f"BREACH: {err_msg}", {
                "type": "breach",
                "action": raw_action,
                "active_subgoal": active_sg_id,
            }

        # Advance hierarchical planner progress
        self.executed_actions.append(raw_action)
        advanced, completed_subgoal_id = self.planner.update_progress(self.world.entities)

        # Detect stagnant action (zero state delta and no subgoal advance)
        if not advanced:
            checkpoint = self.memento.peek()
            if checkpoint:
                has_delta = any(
                    checkpoint.entities[k].properties != self.world.entities[k].properties
                    for k in self.world.entities if k in checkpoint.entities
                )
                if not has_delta:
                    self.banned_actions.append(raw_action)

        # Check if newly fired schema events occurred
        fired_schema_events = self.world.schema_engine.active_schema_alerts
        self.monitor.ingest_schema_events(fired_schema_events)

        # Refresh AutoDream Fact Cards with active entities
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
        """Finalize episode and compile headline metrics."""
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
            and self.committed_schema_violations == 0
            and self.committed_conservation_breaches == 0
        )

        return {
            "is_success": is_success,
            "turns_executed": self.current_turn,
            "subgoals_completed": sum(1 for g in self.planner.subgoals if g.is_completed),
            "total_subgoals": len(self.planner.subgoals),
            "committed_schema_violations": self.committed_schema_violations,
            "committed_conservation_breaches": self.committed_conservation_breaches,
            "intercepted_traps": self.intercepted_traps,
            "compaction_ratio": compaction,
            "max_prompt_tokens": max_prompt,
            "mean_prompt_tokens": round(mean_prompt, 1),
            "mean_latency_ms": round(mean_latency, 1),
            "emerged_entities": list(self.world.schema_engine.emerged_entity_ids),
            "retired_entities": list(self.world.schema_engine.retired_entity_ids),
        }
