"""MN-018 Full Cognitive Host Orchestrator.

Unifies all Mộng Nhiễm substrates into an integrated Dual-Engine Host:
- Physics simulation and Conservation Law Guard
- Hierarchical Mission DAG planning and symbolic phase gates
- Optimistic Concurrency Guard and Delta Notices
- Dynamic GBNF Affordance Compiler with active RECALL pruning
- Append-only SHA-256 Episodic Event Log
- Autonomous AutoDream Memory Consolidation
- Host Memento Rollback and Negative Action Steering
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from autodream_engine import AutoDreamEngine
from concurrency_guard import ConcurrencyGuard
from dynamic_affordance import DynamicAffordanceCompiler
from episodic_memory import EpisodicLog
from hierarchical_planner import HierarchicalPlanner, MissionGraph, SubGoal
from memento_stack import MementoStack
from microworld_engine import MicroworldEngine, WorldEntity


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
    is_conservation_breach: bool
    phase_advanced: bool
    host_latency_ms: float
    model_latency_ms: float


@dataclass
class ExecutionResult:
    """End-to-end mission execution result across long-horizon microworld run."""
    case_id: str
    arm: str
    success: bool
    terminal_status: str
    total_turns: int
    final_world_tick: int
    stale_violations: int
    horizon_jumping_events: int
    premature_resolutions: int
    conservation_breaches: int
    token_ceiling_violations: int
    max_prompt_tokens: int
    mean_prompt_tokens: float
    mean_turn_latency_ms: float
    stale_intercepted: int = 0
    autodream_cycles: int = 0
    compression_ratio: float = 0.0
    turn_history: List[TurnMetric] = field(default_factory=list)


class MN018Orchestrator:
    """Host execution orchestrator for MN-018 Dual-Engine cognitive benchmark."""

    def __init__(
        self,
        engine: MicroworldEngine,
        mission: MissionGraph,
        arm: str = "arm3",
        ticks_per_turn: int = 1,
        max_turns: int = 70,
        token_counter: Optional[Callable[[str], int]] = None,
    ) -> None:
        self.engine = engine
        self.mission = mission
        self.planner = HierarchicalPlanner(mission)
        self.guard = ConcurrencyGuard()
        self.episodic_log = EpisodicLog()
        self.autodream = AutoDreamEngine(event_threshold=15, token_threshold=400)
        self.memento = MementoStack(max_depth=10)
        self.arm = arm.lower()
        self.ticks_per_turn = ticks_per_turn
        self.max_turns = max_turns
        self.token_counter = token_counter or self._default_token_counter

        # Working context fact cards (scoped to <= 4 cards)
        self.working_entities: Dict[str, str] = {}
        self.working_entity_versions: Dict[str, int] = {}
        self.pending_delta_notices: List[str] = []
        self.turn_count: int = 0
        self.conservation_breaches_committed: int = 0

    @staticmethod
    def _default_token_counter(text: str) -> int:
        """Conservative token approximation (1 token ~= 4 chars)."""
        return max(1, int(len(text) / 3.8))

    def build_prompt(self, global_mission_desc: str) -> str:
        """Construct forward-pass context prompt according to active Arm."""
        sections: List[str] = []

        if self.arm == "arm1":
            # Flat Baseline: Global unguided mission text
            sections.append(f"[GLOBAL MISSION SPECIFICATION]\n{global_mission_desc}")
            sections.append(f"[CURRENT WORLD TICK: {self.engine.clock.current_tick}]")
            # Sliding raw event log (uncompressed)
            unconsolidated = self.episodic_log.events[-5:]
            if unconsolidated:
                sections.append("[RECENT EVENT LOG]")
                for e in unconsolidated:
                    sections.append(f"TICK {e.tick}: {e.entity_id} {e.action_name} -> {e.status}")

        elif self.arm == "arm2":
            # Static Plan Control: Shows active sub-goal but no concurrency or memory consolidation
            self.planner.update_plan(self.engine)
            scoped_plan = self.planner.render_scoped_prompt(self.engine)
            sections.append(scoped_plan)
            # Working set cards without pruning
            if self.working_entities:
                sections.append("[OBSERVED ENTITIES]")
                for card in self.working_entities.values():
                    sections.append(card)

        else:
            # Arm 3: Full Dual-Engine Cognitive Host Stack
            self.planner.update_plan(self.engine)
            scoped_plan = self.planner.render_scoped_prompt(self.engine)
            sections.append(scoped_plan)

            # 1. Negative action directives
            neg_directives = self.memento.render_negative_directives()
            if neg_directives:
                sections.append(neg_directives)

            # 2. Concurrency Delta Notices
            if self.pending_delta_notices:
                sections.append("[CONCURRENCY DELTA NOTICES]")
                for notice in self.pending_delta_notices[-2:]:
                    sections.append(notice)
                self.pending_delta_notices.clear()

            # 3. AutoDream Consolidated Declarative Memory (if any)
            decl_mem = self.autodream.render_declarative_context()
            if decl_mem:
                sections.append(decl_mem)

            # 4. Working memory entity cards (freshest observed entities)
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
        all_completed = self.mission.is_mission_accomplished(self.engine)
        negative_actions = self.memento.get_negative_actions()

        if self.arm in ("arm1", "arm2"):
            # Unconstrained global grammar
            return DynamicAffordanceCompiler.compile_global_grammar(
                all_actions=all_case_actions,
                known_entity_ids=known_eids,
                allow_resolve=True,
                negative_actions=None if self.arm == "arm1" else negative_actions,
            )
        else:
            # Arm 3: Dynamic GBNF constrained strictly to active sub-goal with RECALL pruning
            self.planner.update_plan(self.engine)
            current_entity_versions = {
                eid: ent.version for eid, ent in self.engine.entities.items()
            }
            return DynamicAffordanceCompiler.compile_for_subgoal(
                subgoal=self.planner.active_subgoal,
                known_entity_ids=known_eids,
                all_completed=all_completed,
                negative_actions=negative_actions,
                working_entity_versions=self.working_entity_versions,
                current_entity_versions=current_entity_versions,
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
        m_wait = re.match(r"^ACTION:\s*WAIT\s*(.*)$", clean)
        if m_wait:
            return "WAIT", ""
        return "UNKNOWN", clean

    def step(
        self,
        raw_response: str,
        action_executor: Callable[[str, str, MicroworldEngine], Tuple[bool, str]],
        model_latency_ms: float = 0.0,
    ) -> TurnMetric:
        """Process one discrete turn: concurrency check, execution, conservation check, tick, AutoDream."""
        t_start = time.perf_counter()
        self.turn_count += 1
        act_type, act_target = self.parse_action(raw_response)

        is_stale = False
        is_horizon_jumping = False
        is_premature_res = False
        is_conservation_breach = False

        # 1. Horizon Jumping & Premature Resolution Detection
        active_sg = self.planner.active_subgoal
        all_done = self.mission.is_mission_accomplished(self.engine)

        if act_type == "RESOLVE":
            if not all_done:
                is_premature_res = True
        elif act_type == "DISPATCH":
            if active_sg and act_target not in active_sg.allowed_actions:
                is_horizon_jumping = True

        # 2. Concurrency Validation
        target_entity_id = self._extract_target_entity(act_target)
        if target_entity_id and target_entity_id in self.engine.entities:
            enforce_guard = (self.arm == "arm3")
            is_allowed, err_code, notice = self.guard.validate_action(
                entity_id=target_entity_id,
                engine=self.engine,
                enforce_guard=enforce_guard,
            )
            if not is_allowed:
                if err_code in ("STALE_VERSION_INTERCEPTED", "ENTITY_EXPIRED"):
                    is_stale = True
                if notice:
                    self.pending_delta_notices.append(notice)
            elif err_code in ("STALE_OVERWRITE_PERMITTED", "MUTATE_EXPIRED_PERMITTED"):
                is_stale = True

        # 3. Action Execution & Conservation Guard
        if act_type == "RECALL":
            eid = act_target
            ent = self.engine.get_entity(eid)
            if ent:
                card = ent.render_fact_card()
                self.working_entities[eid] = card
                self.working_entity_versions[eid] = ent.version
                self.guard.record_observation(eid, ent.version, self.engine.clock.current_tick)
                self.episodic_log.append(
                    tick=self.engine.clock.current_tick,
                    entity_id=eid,
                    action_name="RECALL",
                    status="SUCCESS",
                    details={"version": ent.version},
                )
        elif act_type == "DISPATCH" and not (is_stale and self.arm == "arm3"):
            # In Arm 3: push Memento checkpoint prior to mutation
            if self.arm == "arm3":
                self.memento.push(self.engine, action_attempted=act_target)

            success, message = action_executor(act_type, act_target, self.engine)

            if "CONSERVATION_BREACH" in message or "INVARIANT_BREACH" in message:
                is_conservation_breach = True
                if self.arm == "arm3":
                    # Roll back immediately to restore physical integrity
                    self.memento.rollback_latest(self.engine, reason=message)
                    self.pending_delta_notices.append(f"[MEMENTO ROLLBACK: {message}]")
                else:
                    self.conservation_breaches_committed += 1

            # Log to episodic memory
            self.episodic_log.append(
                tick=self.engine.clock.current_tick,
                entity_id=target_entity_id or "system",
                action_name=act_target,
                status="SUCCESS" if success else "FAILED",
                details={"message": message, "breach": is_conservation_breach},
            )

        # 4. Advance Background World Ticks
        background_events = self.engine.step_ticks(self.ticks_per_turn)
        for bevent in background_events:
            self.episodic_log.append(
                tick=self.engine.clock.current_tick,
                entity_id="environment",
                action_name="TICK_MUTATION",
                status="INFO",
                details={"event": bevent},
            )
            if self.arm == "arm3":
                self.pending_delta_notices.append(f"[BACKGROUND DRIFT: {bevent}]")

        # 5. Autonomous AutoDream Consolidation Pass (Arm 3)
        if self.arm == "arm3":
            self.autodream.consolidate(self.episodic_log, self.engine)

        # 6. Check Phase Advancement
        advanced, _ = self.planner.update_plan(self.engine)

        host_latency_ms = (time.perf_counter() - t_start) * 1000.0

        return TurnMetric(
            turn_idx=self.turn_count,
            world_tick=self.engine.clock.current_tick,
            prompt_tokens=0,
            raw_action=raw_response,
            action_type=act_type,
            action_target=act_target,
            is_valid_format=(act_type != "UNKNOWN"),
            is_stale_mutation=is_stale,
            is_horizon_jumping=is_horizon_jumping,
            is_premature_resolution=is_premature_res,
            is_conservation_breach=is_conservation_breach,
            phase_advanced=advanced,
            host_latency_ms=host_latency_ms,
            model_latency_ms=model_latency_ms,
        )

    def _extract_target_entity(self, act_target: str) -> Optional[str]:
        """Extract entity ID parameter from action string matching registered entities."""
        tokens = act_target.split()
        for tok in tokens:
            if tok in self.engine.entities:
                return tok
        if len(tokens) >= 2:
            return tokens[1]
        return None
