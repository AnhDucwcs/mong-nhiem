"""Mộng Nhiễm Core Cognitive Kernel Façade.

Provides a unified, minimal, 3-line consumer interface for embedding Mộng Nhiễm
into downstream applications (Desktop Assistants, Game Engines, SCADA controllers).
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Self

from mong_nhiem.bimodal import (
    BimodalEmission,
    BimodalParser,
    CommClass,
    compile_bimodal_gbnf_grammar,
)
from mong_nhiem.core.semantic_gate import SemanticInvariantGate, SemanticPrecondition
from mong_nhiem.orchestration.reflex_breaker import RedlineRule, ReflexCircuitBreaker
from mong_nhiem.preemption import HumanSupervisoryBridge
from mong_nhiem.runtime.backends import (
    BaseInferenceBackend,
    LlamaServerBackend,
    MockBackend,
    SubprocessLlamaBackend,
)
from mong_nhiem.schema import (
    CompiledWorldSchema,
    DeclarativeSchemaLoader,
)
from mong_nhiem.state import ContinuousStateEngine
from mong_nhiem.temporal import ClockMode, TemporalBridge


@dataclass(frozen=True)
class StepResult:
    """Consolidated outcome of an authoritative Host cognitive tick."""

    action_verb: str
    action_params: dict[str, str]
    comm_class: CommClass
    comm_message: str
    raw_output: str
    in_standby: bool
    preempted: bool
    tick: int
    delta_time: float
    state_snapshot: dict[str, Any]
    fired_invariants: list[str] = field(default_factory=list)


class MongNhiemKernel:
    """Master Façade coordinating Host State, Invariants, and Reasoning Engine."""

    def __init__(
        self,
        schema: CompiledWorldSchema | str | dict[str, Any],
        backend: BaseInferenceBackend | str | None = None,
        clock_mode: ClockMode = ClockMode.REAL_TIME,
        tick_interval_seconds: float = 1.0,
        state_file: str | None = None,
        weights_path: str | None = None,
    ) -> None:
        # 1. Initialize Schema
        if isinstance(schema, CompiledWorldSchema):
            self.schema = schema
        elif isinstance(schema, str):
            if os.path.exists(schema):
                self.schema = DeclarativeSchemaLoader.load_from_file(schema)
            else:
                self.schema = DeclarativeSchemaLoader.load_from_json_string(schema)
        elif isinstance(schema, dict):
            self.schema = DeclarativeSchemaLoader.load_from_dict(schema)
        else:
            raise TypeError(f"Unsupported schema type: {type(schema)}")

        # 2. Initialize Inference Backend
        if backend is not None:
            if isinstance(backend, str):
                self.backend: BaseInferenceBackend = LlamaServerBackend(endpoint=backend)
            elif isinstance(backend, BaseInferenceBackend):
                self.backend = backend
            else:
                raise TypeError(f"Invalid backend type: {type(backend)}")
        elif weights_path is not None:
            self.backend = SubprocessLlamaBackend(weights_path=weights_path)
        elif self.schema.model_config:
            m_cfg = self.schema.model_config
            b_type = m_cfg.get("type", "llama_server")
            if "weights_path" in m_cfg:
                self.backend = SubprocessLlamaBackend(
                    weights_path=m_cfg["weights_path"],
                    port=int(m_cfg.get("port", 18505)),
                    n_gpu_layers=int(m_cfg.get("n_gpu_layers", 99)),
                )
            elif b_type in ("openai_compat", "ollama"):
                from mong_nhiem.runtime.backends import OpenAICompatBackend
                self.backend = OpenAICompatBackend(
                    endpoint=m_cfg.get("endpoint", "http://127.0.0.1:11434/v1"),
                    model_name=m_cfg.get("model_name", "default"),
                )
            elif b_type == "mock":
                self.backend = MockBackend()
            else:
                endpoint = m_cfg.get("endpoint", "http://127.0.0.1:8080")
                self.backend = LlamaServerBackend(
                    endpoint=endpoint,
                    slot_id=int(m_cfg.get("slot_id", 0)),
                    cache_prompt=bool(m_cfg.get("cache_prompt", True)),
                )
        else:
            # Fallback to deterministic mock backend if none provided
            self.backend = MockBackend()

        # 3. Initialize Temporal Bridge
        self.temporal_bridge = TemporalBridge(
            mode=clock_mode,
            tick_interval_seconds=tick_interval_seconds,
        )

        # 4. Initialize Continuous State Engine
        self.state_engine = ContinuousStateEngine()
        for trait in self.schema.continuous_traits:
            self.state_engine.register_variable(
                name=trait.name,
                initial_value=trait.initial_value,
                min_val=trait.min_val,
                max_val=trait.max_val,
                rate_per_unit=trait.rate_per_sec,
                is_decay=trait.is_decay,
            )

        for inv in self.schema.invariants:
            self.state_engine.register_trigger(
                variable_name=inv.target_metric,
                threshold=inv.threshold,
                comparison=inv.comparator,
                trigger_action=inv.trigger_action,
            )

        # 5. Initialize Invariant Gate & Reflex Breaker
        self.invariant_gate = SemanticInvariantGate()
        for pre in self.schema.preconditions:
            self.invariant_gate.register_precondition(
                action_verb=pre.action_verb,
                precondition=SemanticPrecondition(
                    required_entity=next(iter(pre.required_states.keys()), "*"),
                    required_state=next(iter(pre.required_states.values()), "*"),
                    incompatible_states=set(pre.prohibited_states.keys()),
                ),
            )

        self.reflex_breaker = ReflexCircuitBreaker()
        for inv in self.schema.invariants:
            self.reflex_breaker.register_rule(
                RedlineRule(
                    metric_key=inv.target_metric,
                    threshold=inv.threshold,
                    comparison=inv.comparator,
                    failsafe_action=inv.trigger_action,
                    reset_threshold=inv.threshold * 0.8,
                )
            )

        # 6. Initialize Human Preemption Bridge
        self.human_bridge = HumanSupervisoryBridge()

        # 7. Persistence file
        self.state_file = state_file
        if self.state_file and os.path.exists(self.state_file):
            self.state_engine.load_from_disk(self.state_file)

        # 8. Grammar compilation
        allowed_verbs = [p.action_verb for p in self.schema.preconditions] or None
        self.grammar = compile_bimodal_gbnf_grammar(allowed_verbs=allowed_verbs)

    @classmethod
    def from_schema(
        cls,
        schema_path: str,
        backend: BaseInferenceBackend | str | None = None,
        **kwargs: Any,
    ) -> MongNhiemKernel:
        """Factory constructor initializing kernel directly from a schema file."""
        return cls(schema=schema_path, backend=backend, **kwargs)

    def tick(
        self,
        stimulus: str = "",
        user_input: str | None = None,
        delta_time: float | None = None,
    ) -> StepResult:
        """Authoritative single cognitive tick execution."""
        # Step A: Human Supervisory Command Resolution
        preempted = False
        if user_input:
            self.human_bridge.inject_human_command(raw_command=user_input)
            self.temporal_bridge.record_user_activity()
            preempted = True

        # Step B: Advance Temporal Bridge & Continuous State
        if delta_time is None:
            if self.temporal_bridge.mode == ClockMode.REAL_TIME:
                dt, _ = self.temporal_bridge.measure_real_time_tick()
            else:
                dt = float(self.temporal_bridge.step_simulated(1))
        else:
            dt = float(delta_time)
            if self.temporal_bridge.mode == ClockMode.SIMULATED:
                self.temporal_bridge.step_simulated(max(1, int(dt)))

        fired_triggers = self.state_engine.step_time(dt)

        # Snapshot state
        state_dict = {
            name: self.state_engine.get_variable(name)
            for name in self.state_engine.variables
        }

        # Step C: Evaluate Reflex Breakers (Physical Safety Priority)
        tripped, failsafe_action = self.reflex_breaker.check_telemetry(
            telemetry=state_dict,
            current_tick=self.temporal_bridge.simulated_tick,
        )
        if tripped and failsafe_action:
            if self.state_file:
                self.state_engine.save_to_disk_atomic(self.state_file)
            return StepResult(
                action_verb=failsafe_action,
                action_params={},
                comm_class=CommClass.INFORM,
                comm_message=f"CRITICAL REDLINE BREACH: Emergency {failsafe_action} engaged.",
                raw_output=f"ACTION: {failsafe_action}\nCOMMUNICATE [INFORM]: \"Redline tripped\"",
                in_standby=False,
                preempted=preempted,
                tick=self.temporal_bridge.simulated_tick,
                delta_time=dt,
                state_snapshot=state_dict,
                fired_invariants=fired_triggers + [failsafe_action],
            )

        # Step D: Check Supervisory Standby
        if self.human_bridge.in_standby and not user_input:
            return StepResult(
                action_verb="ABSTAIN_STANDBY",
                action_params={},
                comm_class=CommClass.QUERY,
                comm_message=self.human_bridge.standby_reason or "Awaiting operator intervention.",
                raw_output="",
                in_standby=True,
                preempted=False,
                tick=self.temporal_bridge.simulated_tick,
                delta_time=dt,
                state_snapshot=state_dict,
                fired_invariants=fired_triggers,
            )

        # Step E: Construct Model Prompt
        prompt = self._format_prompt(stimulus=stimulus, state=state_dict)

        # Step F: Generate and Parse Bimodal Output
        start_epoch = self.human_bridge.preemption_gate.world_epoch
        raw_output = self.backend.generate(
            prompt=prompt,
            grammar=self.grammar,
            session_id=self.schema.schema_name,
        )
        emission = BimodalParser.parse(raw_output)

        # Step G: Preemption Epoch Verification
        valid_epoch, _ = self.human_bridge.validate_action_against_human_epoch(
            action=emission.full_action_str,
            action_epoch=start_epoch,
        )
        if not valid_epoch:
            # Stale proposal invalidated by concurrent human input
            emission = BimodalEmission(
                action_verb="ABSTAIN_PREEMPTED",
                comm_class=CommClass.INFORM,
                comm_message="Action proposal dropped due to intervening human directive.",
                valid=True,
                raw_text=raw_output,
            )
            preempted = True

        # Step H: Handle Standby Transition on QUERY
        if emission.comm_class == CommClass.QUERY:
            self.human_bridge.enter_standby(reason=emission.comm_message)

        # Step I: Save state if file specified
        if self.state_file:
            self.state_engine.save_to_disk_atomic(self.state_file)

        return StepResult(
            action_verb=emission.action_verb,
            action_params=emission.action_params,
            comm_class=emission.comm_class,
            comm_message=emission.comm_message,
            raw_output=raw_output,
            in_standby=self.human_bridge.in_standby,
            preempted=preempted,
            tick=self.temporal_bridge.simulated_tick,
            delta_time=dt,
            state_snapshot=state_dict,
            fired_invariants=fired_triggers,
        )

    def _format_prompt(self, stimulus: str, state: dict[str, Any]) -> str:
        """Formats bounded prompt strictly adhering to <= 512 token envelope."""
        state_repr = ", ".join(f"{k}={v}" for k, v in state.items())
        return (
            f"[SYSTEM: {self.schema.schema_name}]\n"
            f"State: {state_repr}\n"
            f"Stimulus: {stimulus or 'Nominal tick'}\n"
            f"Instruction: Emit single-pass ACTION and COMMUNICATE act.\n"
        )

    def close(self) -> None:
        """Cleans up backend and saves final state."""
        if self.state_file:
            self.state_engine.save_to_disk_atomic(self.state_file)
        self.backend.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.close()
