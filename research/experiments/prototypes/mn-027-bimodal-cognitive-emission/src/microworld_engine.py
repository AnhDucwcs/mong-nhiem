"""Unified Real-Time Bimodal Microworld Engine.

Integrates Dual-Clock timing, Continuous State decay, Declarative Schema,
Semantic Invariants, and Human Supervisory preemption into a single runtime.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from mong_nhiem.core.semantic_gate import SemanticInvariantGate, SemanticPrecondition
from mong_nhiem.knowledge.abductive_tracer import AbductiveCausalTracer
from mong_nhiem.orchestration.preemption_gate import ActionClass, PreemptiveInterruptGate

from bimodal_protocol import BimodalEmission, BimodalParser, CommClass
from continuous_state import ContinuousStateEngine
from human_preemption import HumanSupervisoryBridge
from schema_loader import CompiledWorldSchema, DeclarativeSchemaLoader
from temporal_bridge import ClockMode, TemporalBridge


class BimodalMicroworldEngine:
    """Integrated real-time runtime engine for MN-027 benchmark and deployment."""

    def __init__(
        self,
        schema: Optional[CompiledWorldSchema] = None,
        clock_mode: ClockMode = ClockMode.SIMULATED,
    ) -> None:
        self.temporal_bridge = TemporalBridge(mode=clock_mode)
        self.continuous_state = ContinuousStateEngine()
        self.human_bridge = HumanSupervisoryBridge()
        self.semantic_gate = SemanticInvariantGate()

        # Dynamic world state dict
        self.world_state: Dict[str, Any] = {
            "mode": "OPERATIONAL",
            "sensors": {},
            "valves": {},
            "tasks": {},
            "pet": {},
        }

        # Apply schema if supplied
        if schema:
            self._apply_schema(schema)

    def _apply_schema(self, schema: CompiledWorldSchema) -> None:
        """Configures runtime structures from compiled declarative schema."""
        for ent in schema.entities:
            self.world_state[ent.name] = dict(ent.initial_properties)

        for trait in schema.continuous_traits:
            self.continuous_state.register_variable(
                name=trait.name,
                initial_value=trait.initial_value,
                min_val=trait.min_val,
                max_val=trait.max_val,
                rate_per_unit=trait.rate_per_sec,
                is_decay=trait.is_decay,
            )

        for inv in schema.invariants:
            self.continuous_state.register_trigger(
                variable_name=inv.target_metric,
                threshold=inv.threshold,
                comparison=inv.comparator,
                trigger_action=inv.trigger_action,
            )

        for prec in schema.preconditions:
            self.semantic_gate.register_precondition(
                SemanticPrecondition(
                    action_verb=prec.action_verb,
                    required_states=prec.required_states,
                    prohibited_states=prec.prohibited_states,
                )
            )

    def load_case_scenario(self, case: Dict[str, Any]) -> None:
        """Initializes microworld state from a benchmark test scenario."""
        init = case.get("initial_state", {})
        self.world_state = {
            "mode": init.get("mode", "OPERATIONAL"),
            "sensors": json.loads(json.dumps(init.get("sensors", {}))),
            "valves": json.loads(json.dumps(init.get("valves", {}))),
            "tasks": json.loads(json.dumps(init.get("tasks", {}))),
            "pet": json.loads(json.dumps(init.get("pet", {}))),
        }

        # If scenario starts in standby
        if self.world_state["mode"] == "SUPERVISED_STANDBY":
            self.human_bridge.enter_standby(case.get("stimulus", "Sensor Blackout"))

        # Initialize continuous variables for companion domain
        if "pet" in init and init["pet"]:
            p = init["pet"]
            self.continuous_state.register_variable(
                "energy", float(p.get("energy", 80.0)), 0.0, 100.0, rate_per_unit=1.0, is_decay=True
            )
            self.continuous_state.register_variable(
                "hunger", float(p.get("hunger", 20.0)), 0.0, 100.0, rate_per_unit=1.0, is_decay=False
            )
            self.continuous_state.register_trigger(
                "energy", 15.0, "<=", "TRIGGER_REST_ALERT"
            )
            self.continuous_state.register_trigger(
                "hunger", 80.0, ">=", "TRIGGER_HUNGER_ALERT"
            )

    def advance_time(self, delta_time: float) -> List[str]:
        """Steps continuous time, advancing clock and firing threshold triggers."""
        if self.temporal_bridge.mode == ClockMode.SIMULATED:
            self.temporal_bridge.step_simulated(int(delta_time))
        else:
            self.temporal_bridge.measure_real_time_tick()

        fired = self.continuous_state.step_time(delta_time)
        return fired

    def format_working_prompt(self, case: Dict[str, Any], include_bimodal_instructions: bool = True) -> str:
        """Constructs a compact context-scaffolded prompt strictly bounded <= 512 tokens."""
        domain = case.get("domain", "general")
        stimulus = case.get("stimulus", "")

        state_lines = [f"[MODE: {self.world_state['mode']}]"]

        if self.human_bridge.in_standby:
            state_lines.append(f"[STANDBY_REASON: {self.human_bridge.standby_reason}]")
            state_lines.append("[PHASE: SOLICIT_HUMAN]")
        elif domain == "companion":
            traits_card = self.continuous_state.format_fact_card()
            state_lines.append(traits_card)
            state_lines.append("[PHASE: OPERATIONAL_EXPRESS]")
        else:
            state_lines.append("[PHASE: OPERATIONAL_BROADCAST]")

        if self.world_state.get("sensors"):
            s_str = " ".join(f"{k}:{v.get('status','ONLINE')}({v.get('value',0)})" for k, v in self.world_state["sensors"].items())
            state_lines.append(f"[SENSORS {s_str}]")

        if self.world_state.get("tasks"):
            t_str = " ".join(f"{k}:{v.get('status','PENDING')}" for k, v in self.world_state["tasks"].items())
            state_lines.append(f"[TASKS {t_str}]")

        context_str = "\n".join(state_lines)

        instructions = ""
        if include_bimodal_instructions:
            instructions = (
                "\nRespond in strict Bimodal Cognitive Emission format:\n"
                "ACTION: <VERB> [PARAMS]\n"
                "COMMUNICATE [<INFORM|QUERY|EXPRESS>]: \"<MESSAGE>\"\n"
            )

        prompt = f"""<|im_start|>system
You are Mộng Nhiễm Cognitive Operator. Reason over the current state and emit valid bimodal actions.{instructions}<|im_end|>
<|im_start|>user
Context:
{context_str}
Stimulus: {stimulus}
<|im_end|>
<|im_start|>assistant
"""
        return prompt

    def execute_emission(
        self,
        emission: BimodalEmission,
        action_epoch: Optional[int] = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Validates and applies a bimodal emission to the microworld state.

        Returns:
            Tuple of (success: bool, status_message: str, telemetry: Dict[str, Any]).
        """
        if not emission.valid:
            return False, f"Syntax Error: {emission.parse_error}", {"breach": False}

        if action_epoch is None:
            action_epoch = self.human_bridge.preemption_gate.world_epoch

        # 1. Determine action class
        act_class = ActionClass.MUTATION
        if emission.action_verb.startswith("LOG_") or emission.action_verb.startswith("SEND_"):
            act_class = ActionClass.READ_ONLY
        elif "SUPERVISED_STANDBY" in emission.action_verb or "SCRAM" in emission.action_verb:
            act_class = ActionClass.FAILSAFE

        # 2. Preemption & Epoch check
        valid_epoch, epoch_err = self.human_bridge.validate_action_against_human_epoch(
            action=emission.full_action_str,
            action_epoch=action_epoch,
        )
        if not valid_epoch:
            return False, f"Preemption Rejection: {epoch_err}", {"dropped": True, "breach": False}

        # 3. Semantic invariant check
        valid_sem, sem_err = self.semantic_gate.validate_action(
            emission.action_verb,
            self.world_state,
        )
        if not valid_sem:
            return False, f"Semantic Breach Intercepted: {sem_err}", {"breach": True}

        # 4. State mutation
        if emission.comm_class == CommClass.QUERY or "STANDBY" in emission.action_verb:
            self.human_bridge.enter_standby(emission.comm_message)
            self.world_state["mode"] = "SUPERVISED_STANDBY"
        elif emission.action_verb.startswith("COMPLETE_TASK"):
            t_id = emission.action_params.get("id", "T1")
            if "tasks" in self.world_state and t_id in self.world_state["tasks"]:
                self.world_state["tasks"][t_id]["status"] = "COMPLETED"

        telemetry = {
            "epoch": self.human_bridge.preemption_gate.world_epoch,
            "mode": self.world_state["mode"],
            "comm_class": emission.comm_class.value,
            "message": emission.comm_message,
            "standby": self.human_bridge.in_standby,
        }

        return True, "ACTION_EXECUTED", telemetry
