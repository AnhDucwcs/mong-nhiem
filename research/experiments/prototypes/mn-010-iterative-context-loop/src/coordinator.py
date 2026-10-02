"""Iterative Context Working Set Coordinator for MN-010.

Coordinates host-managed turn execution, packaging bounded working sets (<= 512 tokens),
and enforcing circuit breaker boundaries.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from mong_nhiem.context import ContextPacker, sanitize_chat_tokens

from circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from protocol import ActionType, AgentAction, format_action, parse_action


@dataclass
class TurnRecord:
    turn_index: int
    prompt: str
    prompt_tokens: int
    raw_response: str
    action: AgentAction
    latency_ms: float
    retrieved_content: Optional[str] = None


@dataclass
class CoordinatorResult:
    status: str
    answer: str
    total_turns: int
    turns: List[TurnRecord] = field(default_factory=list)
    visited_targets: List[str] = field(default_factory=list)
    all_under_budget: bool = True
    total_latency_ms: float = 0.0


SYSTEM_PROTOCOL_PROMPT = (
    "You are an iterative context resolution agent. Follow this protocol strictly:\n"
    "- To fetch additional entity, function, or table details, output exactly:\n"
    "  ACTION: FETCH <target>\n"
    "- When you have sufficient facts to answer the question, output exactly:\n"
    "  ACTION: RESOLVE <final_answer>\n"
    "Output only the ACTION directive without redundant conversational filler."
)


class IterativeCoordinator:
    """Manages iterative context retrieval, working set packing, and circuit breakers."""

    def __init__(
        self,
        retriever_fn: Callable[[str], Optional[str]],
        model_fn: Callable[[str], str],
        token_counter: Optional[Callable[[str], int]] = None,
        max_turns: int = 3,
        max_budget: int = 512,
    ) -> None:
        self.retriever_fn = retriever_fn
        self.model_fn = model_fn
        self.max_turns = max_turns
        self.max_budget = max_budget
        self.packer = ContextPacker(max_budget=max_budget, tokenizer_func=token_counter)
        self.circuit_breaker = CircuitBreaker(max_turns=max_turns)

    def _build_turn_prompt(self, working_set: str, query: str) -> str:
        safe_ws = sanitize_chat_tokens(working_set)
        safe_query = sanitize_chat_tokens(query)
        return (
            f"{SYSTEM_PROTOCOL_PROMPT}\n\n"
            f"=== CURRENT WORKING SET ===\n"
            f"{safe_ws}\n\n"
            f"=== QUERY ===\n"
            f"{safe_query}\n\n"
            f"Directive:"
        )

    def run(self, query: str, initial_context: str = "") -> CoordinatorResult:
        """Run iterative working set loop to answer the query."""
        self.circuit_breaker.reset()
        t0_total = time.perf_counter()
        
        chunks: List[str] = []
        if initial_context.strip():
            chunks.append(initial_context.strip())

        turn_records: List[TurnRecord] = []
        all_under_budget = True

        for turn_idx in range(1, self.max_turns + 1):
            t0_turn = time.perf_counter()

            # Pack current chunks into working set
            packed_ws = self.packer.pack(chunks, query=query)
            prompt = self._build_turn_prompt(packed_ws, query)
            prompt_tokens = self.packer.count_tokens(prompt)
            if prompt_tokens > self.max_budget:
                all_under_budget = False

            # Invoke model
            response_text = self.model_fn(prompt)
            action = parse_action(response_text)

            turn_ms = (time.perf_counter() - t0_turn) * 1000

            # Validate action through circuit breaker
            valid, cb_status, trip_reason = self.circuit_breaker.validate_action(action)
            if not valid:
                self.circuit_breaker.trip(cb_status, trip_reason or "Validation failed")
                turn_records.append(
                    TurnRecord(
                        turn_index=turn_idx,
                        prompt=prompt,
                        prompt_tokens=prompt_tokens,
                        raw_response=response_text,
                        action=action,
                        latency_ms=round(turn_ms, 2),
                    )
                )
                return CoordinatorResult(
                    status=cb_status.value,
                    answer="",
                    total_turns=turn_idx,
                    turns=turn_records,
                    visited_targets=list(self.circuit_breaker.visited_targets),
                    all_under_budget=all_under_budget,
                    total_latency_ms=round((time.perf_counter() - t0_total) * 1000, 2),
                )

            # Record step in circuit breaker
            self.circuit_breaker.record_step(action)

            # Process valid action
            if action.action_type == ActionType.RESOLVE:
                turn_records.append(
                    TurnRecord(
                        turn_index=turn_idx,
                        prompt=prompt,
                        prompt_tokens=prompt_tokens,
                        raw_response=response_text,
                        action=action,
                        latency_ms=round(turn_ms, 2),
                    )
                )
                return CoordinatorResult(
                    status="RESOLVED",
                    answer=action.argument,
                    total_turns=turn_idx,
                    turns=turn_records,
                    visited_targets=list(self.circuit_breaker.visited_targets),
                    all_under_budget=all_under_budget,
                    total_latency_ms=round((time.perf_counter() - t0_total) * 1000, 2),
                )

            elif action.action_type == ActionType.FETCH:
                target = action.argument
                fetched_text = self.retriever_fn(target)
                if fetched_text:
                    chunks.append(f"[{target}]\n{fetched_text}")
                else:
                    chunks.append(f"[{target}]\nTarget not found in corpus.")

                turn_records.append(
                    TurnRecord(
                        turn_index=turn_idx,
                        prompt=prompt,
                        prompt_tokens=prompt_tokens,
                        raw_response=response_text,
                        action=action,
                        latency_ms=round(turn_ms, 2),
                        retrieved_content=fetched_text,
                    )
                )
            else:
                # Malformed action
                turn_records.append(
                    TurnRecord(
                        turn_index=turn_idx,
                        prompt=prompt,
                        prompt_tokens=prompt_tokens,
                        raw_response=response_text,
                        action=action,
                        latency_ms=round(turn_ms, 2),
                    )
                )
                return CoordinatorResult(
                    status="MALFORMED_ACTION",
                    answer="",
                    total_turns=turn_idx,
                    turns=turn_records,
                    visited_targets=list(self.circuit_breaker.visited_targets),
                    all_under_budget=all_under_budget,
                    total_latency_ms=round((time.perf_counter() - t0_total) * 1000, 2),
                )

        # Loop exhausted without RESOLVE
        return CoordinatorResult(
            status="MAX_TURNS_EXCEEDED",
            answer="",
            total_turns=self.max_turns,
            turns=turn_records,
            visited_targets=list(self.circuit_breaker.visited_targets),
            all_under_budget=all_under_budget,
            total_latency_ms=round((time.perf_counter() - t0_total) * 1000, 2),
        )
