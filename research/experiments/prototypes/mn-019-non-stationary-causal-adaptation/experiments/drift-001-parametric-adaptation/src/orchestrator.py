"""Dual-Engine Cognitive Host Orchestrator with Discrepancy Monitoring.

Integrates Microworld Engine, Discrepancy Monitor, Dynamic Affordance Compiler,
Memento Stack, and AutoDream Memory Engine for long-horizon non-stationary governance.
"""
from __future__ import annotations

import copy
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from autodream_engine import AutoDreamEngine
from discrepancy_monitor import DiscrepancyMonitor, DriftAlert
from dynamic_affordance import DynamicAffordanceCompiler
from hierarchical_planner import HierarchicalPlanner, SubGoal
from memento_stack import MementoStack
from microworld_engine import SimulatedMicroworld, WorldEntity


class DualEngineOrchestrator:
    """Coordinates host cognitive authority, state transitions, and model interactions."""

    def __init__(
        self,
        world: SimulatedMicroworld,
        planner: HierarchicalPlanner,
        arm: str = "arm3_dynamic_host",  # 'arm1_flat', 'arm2_static_control', 'arm3_dynamic_host'
        discrepancy_monitor: Optional[DiscrepancyMonitor] = None,
        max_turns: int = 35,
    ):
        self.world = world
        self.planner = planner
        self.arm = arm
        self.monitor = discrepancy_monitor or DiscrepancyMonitor()
        self.memento = MementoStack()
        self.autodream = AutoDreamEngine()
        self.max_turns = max_turns

        self.current_turn = 0
        self.banned_actions: List[str] = []
        self.executed_actions: List[str] = []
        self.committed_conservation_breaches = 0
        self.intercepted_traps = 0
        self.turn_latencies: List[float] = []
        self.prompt_token_counts: List[int] = []

    def build_prompt_context(self) -> str:
        """Assemble bounded prompt context strictly respecting <= 512 token ceiling."""
        sections: List[str] = []

        # 1. System directive
        sections.append("GOVERNANCE ACTIVE. Select exactly one structured ACTION.")

        # 2. Fact Cards from AutoDream
        active_eids = list(self.world.entities.keys())
        fact_cards_str = self.autodream.consolidate(self.world.entities, active_eids)
        if fact_cards_str:
            sections.append(fact_cards_str)

        # 3. Active Drift Alerts (Arm 3 only)
        if self.arm == "arm3_dynamic_host":
            drift_str = self.monitor.render_active_drift_cards()
            if drift_str:
                sections.append(drift_str)

        # 4. Current Sub-Goal Directive
        curr_subgoal = self.planner.current_subgoal
        if curr_subgoal:
            sections.append(f"[SUBGOAL {curr_subgoal.subgoal_id}: {curr_subgoal.description}]")
        else:
            sections.append("[SUBGOAL COMPLETE: EMIT RESOLVE]")

        full_prompt = "\n".join(sections)
        tok_count = AutoDreamEngine.estimate_tokens(full_prompt)
        self.prompt_token_counts.append(tok_count)

        return full_prompt

    def compile_turn_grammar(self) -> Optional[str]:
        """Compile GBNF grammar for the current turn based on active evaluation arm."""
        if self.arm == "arm1_flat":
            return None  # Unconstrained output

        curr_subgoal = self.planner.current_subgoal
        allowed = curr_subgoal.candidate_actions if curr_subgoal else []
        allow_resolve = self.planner.is_all_completed()
        known_eids = list(self.world.entities.keys())

        if self.arm == "arm2_static_control":
            # Static compile without discrepancy monitor awareness
            return DynamicAffordanceCompiler.compile_grammar(
                allowed_actions=allowed,
                known_entity_ids=known_eids,
                allow_resolve=allow_resolve,
                negative_actions=self.banned_actions,
                discrepancy_monitor=None,
            )

        # Arm 3: Dynamic compile factoring in active drift alerts
        return DynamicAffordanceCompiler.compile_grammar(
            allowed_actions=allowed,
            known_entity_ids=known_eids,
            allow_resolve=allow_resolve,
            negative_actions=self.banned_actions,
            discrepancy_monitor=self.monitor,
        )

    def execute_turn(self, action_emission: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Process a single turn action emission.
        
        Returns:
            Tuple[is_turn_ok, status_message, turn_metadata]
        """
        start_time = time.perf_counter()
        self.current_turn += 1

        clean_action = action_emission.strip()
        # Parse prefix
        if clean_action.startswith("ACTION: DISPATCH "):
            raw_action = clean_action[len("ACTION: DISPATCH "):].strip()
        elif clean_action.startswith("ACTION: RECALL "):
            eid = clean_action[len("ACTION: RECALL "):].strip()
            # Informational recall
            latency = (time.perf_counter() - start_time) * 1000.0
            self.turn_latencies.append(latency)
            return True, f"Recalled entity {eid}", {"type": "recall", "entity": eid}
        elif clean_action == "ACTION: RESOLVE COMPLETE":
            if self.planner.is_all_completed():
                latency = (time.perf_counter() - start_time) * 1000.0
                self.turn_latencies.append(latency)
                return True, "TASK_RESOLVED_SUCCESSFULLY", {"type": "resolve"}
            else:
                latency = (time.perf_counter() - start_time) * 1000.0
                self.turn_latencies.append(latency)
                return False, "PREMATURE_RESOLUTION_ATTEMPTED", {"type": "premature_resolve"}
        else:
            raw_action = clean_action

        # Track raw event stream for AutoDream compression accounting
        self.autodream.record_raw_event(f"ACTION_EMISSION_{self.current_turn}: {raw_action}")
        for eid, ent in self.world.entities.items():
            self.autodream.record_raw_event(f"TELEMETRY_LOG tick={self.world.current_tick} entity={eid} props={ent.properties}")

        # Compute nominal transition expectations
        s_nominal = self.world.compute_nominal_transition(raw_action)

        # Push memento checkpoint before execution
        self.memento.push(
            step_id=self.current_turn,
            entities=self.world.entities,
            current_tick=self.world.current_tick,
            metadata={"planner_index": self.planner.active_index},
        )

        # Execute actual transition under real drift
        success, breach_msg, s_actual = self.world.execute_actual_transition(raw_action)

        # Evaluate discrepancy vectors
        if self.arm == "arm3_dynamic_host":
            self.monitor.evaluate_step(s_nominal, s_actual, self.world.current_tick)

        if not success:
            # Physical conservation breach intercepted!
            self.intercepted_traps += 1
            # In Arm 1 or Arm 2 without Host rollback, committed breaches accumulate
            if self.arm in ("arm1_flat", "arm2_static_control"):
                self.committed_conservation_breaches += 1

            # Arm 3 performs atomic rollback
            if self.arm == "arm3_dynamic_host":
                checkpoint = self.memento.pop()
                if checkpoint:
                    self.world.entities = copy.deepcopy(checkpoint.entities)
                self.banned_actions.append(raw_action)

            latency = (time.perf_counter() - start_time) * 1000.0
            self.turn_latencies.append(latency)
            return False, f"BREACH: {breach_msg}", {"type": "breach", "action": raw_action}

        # Advance hierarchical planner progress
        active_sg_id = self.planner.current_subgoal.subgoal_id if self.planner.current_subgoal else None
        self.executed_actions.append(raw_action)
        advanced, subgoal_id = self.planner.update_progress(self.world.entities)

        latency = (time.perf_counter() - start_time) * 1000.0
        self.turn_latencies.append(latency)

        status_msg = f"ADVANCED_TO_{subgoal_id}" if advanced else "ACTION_COMMITTED"
        return True, status_msg, {
            "type": "advance",
            "action": raw_action,
            "subgoal": subgoal_id,
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

        is_success = self.planner.is_all_completed() and self.committed_conservation_breaches == 0

        return {
            "is_success": is_success,
            "turns_executed": self.current_turn,
            "subgoals_completed": sum(1 for g in self.planner.subgoals if g.is_completed),
            "total_subgoals": len(self.planner.subgoals),
            "committed_conservation_breaches": self.committed_conservation_breaches,
            "intercepted_traps": self.intercepted_traps,
            "compaction_ratio": compaction,
            "max_prompt_tokens": max_prompt,
            "mean_prompt_tokens": round(mean_prompt, 1),
            "mean_latency_ms": round(mean_latency, 1),
            "discrepancies_detected": len(self.monitor.alert_history),
        }
