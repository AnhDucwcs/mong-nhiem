"""MN-017 Cognitive Orchestrator coordinating Dynamic World Ticks, Hierarchical Planning, and Concurrency.

Supports 3 evaluation arms:
- Arm 1: Flat Baseline (global mission prompt, unconstrained GBNF, unassisted ticks)
- Arm 2: Static Plan Control (sequential sub-goals, unconstrained GBNF, unassisted ticks)
- Arm 3: Dual-Engine MN-017 (scoped sub-goal prompt, dynamic GBNF phase gates, Host Concurrency Guard)
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from concurrency_guard import ConcurrencyGuard
from dynamic_affordance_compiler import DynamicAffordanceCompiler
from hierarchical_planner import HierarchicalPlanner, MissionGraph, SubGoal
from world_engine import DynamicWorldEngine, WorldEntity


@dataclass
class TurnMetric:
    """Metrics recorded for an individual agent turn."""
    turn_idx: int
    world_tick: int
    prompt_tokens: int
    raw_action: str
    action_type: str
    action_target: str
    is_valid_format: bool
    is_stale_mutation: bool
    is_horizon_jumping: bool
    is_premature_resolution: bool
    phase_advanced: bool
    host_latency_ms: float
    model_latency_ms: float


@dataclass
class ExecutionResult:
    """End-to-end mission execution result."""
    case_id: str
    arm: str
    success: bool
    terminal_status: str
    total_turns: int
    final_world_tick: int
    stale_violations: int
    horizon_jumping_events: int
    premature_resolutions: int
    token_ceiling_violations: int
    max_prompt_tokens: int
    mean_prompt_tokens: float
    mean_turn_latency_ms: float
    stale_intercepted: int = 0
    turn_history: List[TurnMetric] = field(default_factory=list)


class MN017Orchestrator:
    """Host execution orchestrator for MN-017 benchmarks."""

    def __init__(
        self,
        engine: DynamicWorldEngine,
        mission: MissionGraph,
        arm: str = "arm3",
        ticks_per_turn: int = 1,
        max_turns: int = 35,
        token_counter: Optional[Callable[[str], int]] = None,
    ) -> None:
        self.engine = engine
        self.planner = HierarchicalPlanner(mission)
        self.guard = ConcurrencyGuard()
        self.arm = arm.lower()
        self.ticks_per_turn = ticks_per_turn
        self.max_turns = max_turns
        self.token_counter = token_counter or self._default_token_counter
        
        # Working memory buffer of entity fact cards (scoped to <= 4 cards)
        self.working_entities: Dict[str, str] = {}
        self.pending_delta_notices: List[str] = []

    @staticmethod
    def _default_token_counter(text: str) -> int:
        """Conservative token approximation (1 token ~= 4 chars or whitespace tokens)."""
        return max(1, int(len(text) / 3.8))

    def build_prompt(self, global_mission_desc: str) -> str:
        """Construct forward-pass context prompt according to active Arm."""
        sections: List[str] = []

        if self.arm == "arm1":
            # Flat Baseline: Global mission text dumped into prompt
            sections.append(f"[GLOBAL MISSION SPECIFICATION]\n{global_mission_desc}")
            sections.append(f"[CURRENT WORLD TICK: {self.engine.clock.current_tick}]")
        elif self.arm == "arm2":
            # Static Plan Control: Shows active sub-goal but no concurrency notices
            self.planner.update_plan(self.engine)
            scoped_plan = self.planner.render_scoped_prompt(self.engine)
            sections.append(scoped_plan)
        else:
            # Arm 3 (Dual-Engine MN-017): Scoped sub-goal + delta notices
            self.planner.update_plan(self.engine)
            scoped_plan = self.planner.render_scoped_prompt(self.engine)
            sections.append(scoped_plan)
            
            if self.pending_delta_notices:
                sections.append("[CONCURRENCY DELTA NOTICES]")
                for notice in self.pending_delta_notices[-2:]:  # Keep at most 2 freshest notices
                    sections.append(notice)
                self.pending_delta_notices.clear()

        # Append working set entity cards
        if self.working_entities:
            sections.append("[WORKING CONTEXT ENTITIES]")
            for card in self.working_entities.values():
                sections.append(card)

        # Instruction directive
        sections.append(
            "[INSTRUCTION: Output strictly one GBNF-conforming action (e.g. ACTION: DISPATCH <action>, ACTION: RECALL <id>, or ACTION: RESOLVE COMPLETE).]"
        )

        return "\n\n".join(sections)

    def get_gbnf_grammar(self, all_case_actions: List[str]) -> str:
        """Compile GBNF grammar matching current arm and plan state."""
        known_eids = list(self.engine.entities.keys())
        all_completed = self.planner.mission.is_mission_accomplished(self.engine)

        if self.arm in ("arm1", "arm2"):
            # Unconstrained global grammar
            return DynamicAffordanceCompiler.compile_global_grammar(
                all_actions=all_case_actions,
                known_entity_ids=known_eids,
                allow_resolve=True,
            )
        else:
            # Arm 3: Dynamic GBNF constrained strictly to active sub-goal
            self.planner.update_plan(self.engine)
            return DynamicAffordanceCompiler.compile_for_subgoal(
                subgoal=self.planner.active_subgoal,
                known_entity_ids=known_eids,
                all_completed=all_completed,
            )

    def parse_action(self, raw_response: str) -> Tuple[str, str]:
        """Parse structured action from model output."""
        clean = raw_response.strip().split("\n")[0].strip()
        m_dispatch = re.match(r"^ACTION:\s*DISPATCH\s+(.+)$", clean)
        if m_dispatch:
            return "DISPATCH", m_dispatch.group(1).strip()
        m_recall = re.match(r"^ACTION:\s*RECALL\s+(.+)$", clean)
        if m_recall:
            return "RECALL", m_recall.group(1).strip()
        m_resolve = re.match(r"^ACTION:\s*RESOLVE\s*(.*)$", clean)
        if m_resolve:
            return "RESOLVE", m_resolve.group(1).strip()
        return "UNKNOWN", clean

    def step(
        self,
        raw_response: str,
        action_executor: Callable[[str, str, DynamicWorldEngine], Tuple[bool, str]],
        model_latency_ms: float = 0.0,
    ) -> TurnMetric:
        """Process one turn: validate concurrency, execute action, advance world clock, update plan."""
        t_start = time.perf_counter()
        act_type, act_target = self.parse_action(raw_response)
        
        is_stale = False
        is_horizon_jumping = False
        is_premature_res = False
        
        # 1. Horizon Jumping & Premature Resolution Detection
        active_sg = self.planner.active_subgoal
        all_done = self.planner.mission.is_mission_accomplished(self.engine)
        
        if act_type == "RESOLVE":
            if not all_done:
                is_premature_res = True
        elif act_type == "DISPATCH":
            if active_sg and act_target not in active_sg.allowed_actions:
                is_horizon_jumping = True

        # 2. Concurrency Validation (For Arms with guard or tracking)
        target_entity_id = self._extract_target_entity(act_target)
        if target_entity_id:
            enforce_guard = (self.arm == "arm3")
            is_allowed, err_code, notice = self.guard.validate_action(
                entity_id=target_entity_id,
                engine=self.engine,
                enforce_guard=enforce_guard,
            )
            if not is_allowed:
                is_stale = True
                if notice:
                    self.pending_delta_notices.append(notice)
            elif err_code in ("STALE_OVERWRITE_PERMITTED", "MUTATE_EXPIRED_PERMITTED"):
                is_stale = True

        # 3. Action Execution
        if act_type == "RECALL":
            eid = act_target
            ent = self.engine.get_entity(eid)
            if ent:
                card = ent.render_fact_card()
                self.working_entities[eid] = card
                self.guard.record_observation(eid, ent.version, self.engine.clock.current_tick)
        elif act_type == "DISPATCH" and not (is_stale and self.arm == "arm3"):
            # Execute mutation via domain executor
            action_executor(act_type, act_target, self.engine)

        # 4. Advance Background World Ticks
        background_events = self.engine.step_ticks(self.ticks_per_turn)
        for bevent in background_events:
            if self.arm == "arm3":
                self.pending_delta_notices.append(f"[WORLD TICK EVENT: {bevent}]")

        # 5. Check Phase Advancement
        advanced, _ = self.planner.update_plan(self.engine)
        
        host_latency_ms = (time.perf_counter() - t_start) * 1000.0
        
        return TurnMetric(
            turn_idx=len(self.planner.mission.subgoals),
            world_tick=self.engine.clock.current_tick,
            prompt_tokens=0,  # Filled by runner
            raw_action=raw_response,
            action_type=act_type,
            action_target=act_target,
            is_valid_format=(act_type != "UNKNOWN"),
            is_stale_mutation=is_stale,
            is_horizon_jumping=is_horizon_jumping,
            is_premature_resolution=is_premature_res,
            phase_advanced=advanced,
            host_latency_ms=host_latency_ms,
            model_latency_ms=model_latency_ms,
        )

    @staticmethod
    def _extract_target_entity(act_target: str) -> Optional[str]:
        """Extract entity ID parameter from action string (e.g. 'lock_resource res_1' -> 'res_1')."""
        tokens = act_target.split()
        if len(tokens) >= 2:
            return tokens[1]
        return None
