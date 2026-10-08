"""Hierarchical Tool & Working Set Coordinator for MN-012.

Orchestrates multi-turn stateful tool execution:
- Packages bounded L1 working sets (<= 512 tokens) via ContextPacker.
- Synchronizes with HostStateStore (L2 persistent state on disk/RAM).
- Enforces CircuitBreaker bounds (max_turns <= 5, cycle detection).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from mong_nhiem.context import ContextPacker, sanitize_chat_tokens

from circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from memory_store import HostStateStore
from protocol import ActionType, ToolAction, format_action, parse_action


@dataclass
class TurnRecord:
    turn_index: int
    prompt: str
    prompt_tokens: int
    raw_response: str
    action: ToolAction
    observation: str
    latency_ms: float


@dataclass
class CoordinatorResult:
    status: str
    answer: str
    total_turns: int
    turns: List[TurnRecord] = field(default_factory=list)
    all_under_budget: bool = True
    total_latency_ms: float = 0.0
    l2_state_snapshot: Dict[str, Any] = field(default_factory=dict)


SYSTEM_PROTOCOL_PROMPT = (
    "You are a stateful tool execution agent. Follow this protocol strictly:\n"
    "- To read a function or document, output: ACTION: READ <target_id>\n"
    "- To inspect an entity property or balance, output: ACTION: INSPECT <entity_id>.<property>\n"
    "- To execute a state mutation, output: ACTION: DISPATCH <action_name> <payload>\n"
    "- When the objective is achieved, output: ACTION: RESOLVE <final_result>\n"
    "Output only the single ACTION directive without conversational filler."
)


class HierarchicalToolCoordinator:
    """Coordinates L1 working set packing and L2 state management across multi-turn tool loops."""

    def __init__(
        self,
        model_fn: Callable[[str], str],
        token_counter: Optional[Callable[[str], int]] = None,
        max_turns: int = 5,
        max_budget: int = 512,
    ) -> None:
        self.model_fn = model_fn
        self.max_turns = max_turns
        self.max_budget = max_budget
        self.packer = ContextPacker(max_budget=max_budget, tokenizer_func=token_counter)
        self.circuit_breaker = CircuitBreaker(max_turns=max_turns)

    def _build_turn_prompt(
        self,
        l2_summary: str,
        latest_observation: str,
        query: str,
        initial_context: str = "",
    ) -> str:
        safe_l2 = sanitize_chat_tokens(l2_summary)
        safe_obs = sanitize_chat_tokens(latest_observation)
        safe_query = sanitize_chat_tokens(query)
        safe_init = sanitize_chat_tokens(initial_context)

        chunks = []
        if safe_init:
            chunks.append(f"Context: {safe_init}")
        chunks.append(f"State Summary:\n{safe_l2}")
        if safe_obs:
            chunks.append(f"Latest Observation:\n{safe_obs}")

        packed_body = self.packer.pack(chunks, query=safe_query)

        return (
            f"{SYSTEM_PROTOCOL_PROMPT}\n\n"
            f"=== WORKING MEMORY (L1) ===\n"
            f"{packed_body}\n\n"
            f"=== CURRENT TASK ===\n"
            f"{safe_query}\n\n"
            f"Directive:"
        )

    def run(
        self,
        query: str,
        initial_env: Dict[str, Any],
        initial_context: str = "",
        audit_log_path: Optional[Path] = None,
    ) -> CoordinatorResult:
        """Execute multi-turn stateful tool loop."""
        self.circuit_breaker.reset()
        t0_total = time.perf_counter()

        store = HostStateStore(initial_env=initial_env, audit_log_path=audit_log_path)
        turn_records: List[TurnRecord] = []
        all_under_budget = True
        latest_obs = "None"
        resolved_answer = "UNKNOWN"

        for turn_idx in range(1, self.max_turns + 1):
            cb_status = self.circuit_breaker.check_turn()
            if cb_status != CircuitBreakerStatus.ACTIVE:
                break

            t0_turn = time.perf_counter()

            # Compile L1 working set
            l2_summary = store.format_l1_state_summary()
            prompt = self._build_turn_prompt(l2_summary, latest_obs, query, initial_context)
            prompt_tokens = self.packer.count_tokens(prompt)
            if prompt_tokens > self.max_budget:
                all_under_budget = False

            # Model inference
            raw_response = self.model_fn(prompt)
            turn_latency = (time.perf_counter() - t0_turn) * 1000

            # Action parsing
            action = parse_action(raw_response)

            # Tool execution against L2 store
            is_rejected = False
            if action.action_type == ActionType.READ:
                latest_obs = store.read(action.target)
            elif action.action_type == ActionType.INSPECT:
                latest_obs = store.inspect(action.target)
            elif action.action_type == ActionType.DISPATCH:
                latest_obs = store.dispatch(action.target, action.payload, turn=turn_idx)
                if "ACTION_REJECTED" in latest_obs:
                    is_rejected = True
            elif action.action_type == ActionType.RESOLVE:
                resolved_answer = action.payload.strip()
                latest_obs = f"RESOLVED: {resolved_answer}"
                turn_records.append(
                    TurnRecord(
                        turn_index=turn_idx,
                        prompt=prompt,
                        prompt_tokens=prompt_tokens,
                        raw_response=raw_response,
                        action=action,
                        observation=latest_obs,
                        latency_ms=turn_latency,
                    )
                )
                break
            else:
                # INVALID action
                latest_obs = "ACTION_REJECTED InvalidGrammar"
                is_rejected = True

            turn_records.append(
                TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation=latest_obs,
                    latency_ms=turn_latency,
                )
            )

            # Record in circuit breaker
            sig = f"{action.action_type.value}:{action.target}:{action.payload}"
            cb_status = self.circuit_breaker.record_action(sig, is_rejected=is_rejected)
            if cb_status != CircuitBreakerStatus.ACTIVE:
                break

        total_latency = (time.perf_counter() - t0_total) * 1000

        final_status = "RESOLVED" if resolved_answer != "UNKNOWN" else self.circuit_breaker.status.value

        return CoordinatorResult(
            status=final_status,
            answer=resolved_answer,
            total_turns=len(turn_records),
            turns=turn_records,
            all_under_budget=all_under_budget,
            total_latency_ms=total_latency,
            l2_state_snapshot=store.env,
        )
