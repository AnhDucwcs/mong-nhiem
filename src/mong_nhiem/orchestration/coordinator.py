"""Unified Cognitive Orchestrator for Dual-Layer Dynamic Affordance Steering.

Coordinates:
- Layer 1: Prompt attention prior injection (<= 20 tokens).
- Layer 2: Dynamic runtime Context-Free Grammar (GBNF) logit masking.
- Host Memento state checkpointing and context rewind.
- Deterministic Phase Gate goal verification.
- Defensive circuit breaker loop termination.
100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .affordance import BaseAffordanceProvider
from .circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from .grammar import DynamicGBNFCompiler
from .memento import MementoStack
from .phase_gate import PhaseGate
from .protocol import (
    ActionType,
    AffordanceSpec,
    OrchestratorResult,
    ToolAction,
    TurnRecord,
    format_action,
    format_affordance_prior,
    parse_action,
)
from .rewind import ContextRewindManager


DEFAULT_SYSTEM_PROTOCOL_PROMPT = """You are an autonomous agent executing deterministic state actions.
Output exactly ONE action per turn following this format:
ACTION: READ <target>
ACTION: INSPECT <target>
ACTION: DISPATCH <tool_name> <payload>
ACTION: RESOLVE <answer>"""


class CognitiveOrchestrator:
    """Orchestrates multi-turn cognitive loops with dynamic affordance steering."""

    def __init__(
        self,
        model_fn: Callable[[str, Optional[str]], Tuple[str, float]],
        affordance_provider: BaseAffordanceProvider,
        state_executor_fn: Callable[[ToolAction, Dict[str, Any]], Tuple[bool, str]],
        state_summarizer_fn: Optional[Callable[[Dict[str, Any]], str]] = None,
        token_counter_fn: Optional[Callable[[str], int]] = None,
        max_turns: int = 7,
        max_budget: int = 512,
        system_prompt: str = DEFAULT_SYSTEM_PROTOCOL_PROMPT,
        enable_dynamic_grammar: bool = True,
        enable_attention_prior: bool = True,
    ) -> None:
        self.model_fn = model_fn
        self.affordance_provider = affordance_provider
        self.state_executor_fn = state_executor_fn
        self.state_summarizer_fn = state_summarizer_fn or (lambda env: str(env))
        self.token_counter_fn = token_counter_fn or (lambda s: len(s) // 4)
        self.max_turns = max_turns
        self.max_budget = max_budget
        self.system_prompt = system_prompt
        self.enable_dynamic_grammar = enable_dynamic_grammar
        self.enable_attention_prior = enable_attention_prior
        self.phase_gate = PhaseGate()

    def run(
        self,
        query: str,
        initial_env: Dict[str, Any],
        target_predicate: Optional[Dict[str, Any]] = None,
    ) -> OrchestratorResult:
        """Execute full autonomous multi-turn cognitive session."""
        current_env = copy.deepcopy(initial_env)
        stack = MementoStack(max_depth=5)
        context_mgr = ContextRewindManager(max_budget=self.max_budget)
        circuit_breaker = CircuitBreaker(max_turns=self.max_turns)

        # Baseline snapshot S_0
        stack.push(turn_index=0, state=current_env, action_key="INITIAL_STATE")

        turns: List[TurnRecord] = []
        latest_observation = "None"
        rollback_count = 0
        all_under_budget = True
        total_latency_ms = 0.0
        rejected_actions: Set[str] = set()
        executed_actions: Set[str] = set()

        for turn_idx in range(1, self.max_turns + 1):
            state_summary = self.state_summarizer_fn(current_env)

            # Compute active state affordances
            affordances = self.affordance_provider.get_affordances(
                env=current_env,
                query=query,
                rejected_actions=rejected_actions,
                executed_actions=executed_actions,
                target_predicate=target_predicate,
                turn_index=turn_idx,
            )

            # Layer 1: Prompt Attention Prior
            if self.enable_attention_prior:
                affordance_line = format_affordance_prior(affordances)
                if latest_observation == "None":
                    observation_with_affordance = affordance_line
                else:
                    observation_with_affordance = f"{latest_observation}\n{affordance_line}"
            else:
                observation_with_affordance = latest_observation

            # Layer 2: Dynamic Context-Free Grammar (GBNF)
            if self.enable_dynamic_grammar:
                grammar_to_use = DynamicGBNFCompiler.compile(affordances)
            else:
                grammar_to_use = None

            prompt = context_mgr.build_turn_prompt(
                system_prompt=self.system_prompt,
                task_query=query,
                state_summary=state_summary,
                latest_observation=observation_with_affordance,
            )
            prompt_tokens = self.token_counter_fn(prompt)
            if prompt_tokens > self.max_budget:
                all_under_budget = False

            # Model inference pass
            raw_response, latency_ms = self.model_fn(prompt, grammar_to_use)
            total_latency_ms += latency_ms

            action = parse_action(raw_response)
            cb_status = circuit_breaker.record_action(action.action_key)

            if cb_status == CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED:
                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation="CIRCUIT_BREAKER: CYCLE_DETECTED",
                    is_rollback=False,
                    latency_ms=latency_ms,
                    used_grammar=bool(grammar_to_use),
                    compiled_gbnf=grammar_to_use,
                ))
                return OrchestratorResult(
                    status="DEADLOCK_CYCLE_DETECTED",
                    answer="",
                    total_turns=turn_idx,
                    rollback_count=rollback_count,
                    turns=turns,
                    all_under_budget=all_under_budget,
                    total_latency_ms=total_latency_ms,
                    final_environment=current_env,
                )

            # Check RESOLVE via Phase Gate
            if action.action_type == ActionType.RESOLVE:
                is_valid, msg = self.phase_gate.intercept_resolve(current_env, target_predicate, action.payload)
                if not is_valid:
                    # Premature resolution rejection
                    rollback_count += 1
                    rejected_actions.add(action.action_key)
                    turns.append(TurnRecord(
                        turn_index=turn_idx,
                        prompt=prompt,
                        prompt_tokens=prompt_tokens,
                        raw_response=raw_response,
                        action=action,
                        observation=msg,
                        is_rollback=True,
                        latency_ms=latency_ms,
                        used_grammar=bool(grammar_to_use),
                        compiled_gbnf=grammar_to_use,
                    ))
                    latest_observation = f"ROLLBACK_COMMITTED: {msg}"
                    continue

                # Goal satisfied and verified
                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation="TASK_RESOLVED",
                    is_rollback=False,
                    latency_ms=latency_ms,
                    used_grammar=bool(grammar_to_use),
                    compiled_gbnf=grammar_to_use,
                ))
                return OrchestratorResult(
                    status="SUCCESS",
                    answer=action.payload,
                    total_turns=turn_idx,
                    rollback_count=rollback_count,
                    turns=turns,
                    all_under_budget=all_under_budget,
                    total_latency_ms=total_latency_ms,
                    final_environment=current_env,
                )

            # Checkpoint pre-action state
            stack.push(turn_index=turn_idx, state=current_env, action_key=action.action_key)

            # Execute tool mutation against environment
            success, obs = self.state_executor_fn(action, current_env)

            if success:
                executed_actions.add(action.action_key)
                latest_observation = obs
                context_mgr.record_success(format_action(action), obs)
                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation=obs,
                    is_rollback=False,
                    latency_ms=latency_ms,
                    used_grammar=bool(grammar_to_use),
                    compiled_gbnf=grammar_to_use,
                ))
            else:
                # Execution failure: Host Backtracking Rollback
                rollback_count += 1
                rejected_actions.add(action.action_key)
                circuit_breaker.record_action(action.action_key, is_rejected=True)

                # Pop failed state and restore previous valid memento
                stack.pop()
                prev_memento = stack.peek()
                if prev_memento:
                    current_env = copy.deepcopy(prev_memento.state)

                context_mgr.rewind_last()
                negative_directive = (
                    f"ROLLBACK_COMMITTED: Restored turn {prev_memento.turn_index if prev_memento else 0}. "
                    f"REJECTED: {action.action_key} ({obs}). Do NOT repeat this action. Choose an alternative step."
                )
                latest_observation = negative_directive

                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation=negative_directive,
                    is_rollback=True,
                    latency_ms=latency_ms,
                    used_grammar=bool(grammar_to_use),
                    compiled_gbnf=grammar_to_use,
                ))

        # Max turns reached
        return OrchestratorResult(
            status="MAX_TURNS_EXCEEDED",
            answer="",
            total_turns=self.max_turns,
            rollback_count=rollback_count,
            turns=turns,
            all_under_budget=all_under_budget,
            total_latency_ms=total_latency_ms,
            final_environment=current_env,
        )
