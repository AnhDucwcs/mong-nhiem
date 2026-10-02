"""Iterative Context Working Set Coordinator for Mộng Nhiễm.

Interleaves bounded model forward passes (<= 512 tokens per turn) with host-side
context extraction, enforcing action grammar parsing and circuit breaker safety bounds.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Set

from mong_nhiem.context.packer import ContextPacker, sanitize_chat_tokens


class ActionType(str, Enum):
    """Supported agent actions in the iterative loop protocol."""
    FETCH = "FETCH"
    RESOLVE = "RESOLVE"
    INVALID = "INVALID"


@dataclass(frozen=True)
class AgentAction:
    """Parsed action emitted by the reasoning model."""
    action_type: ActionType
    argument: str
    raw: str


_ACTION_REGEX = re.compile(
    r"ACTION:\s*(FETCH|RESOLVE)(?:[:\s]\s*)([^\r\n]+)",
    re.IGNORECASE,
)
_THINK_TAG_REGEX = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def parse_action(text: str) -> AgentAction:
    """Parse model generation into a validated AgentAction directive."""
    if not text or not text.strip():
        return AgentAction(action_type=ActionType.INVALID, argument="", raw=text)

    cleaned = _THINK_TAG_REGEX.sub("", text).strip()
    matches = list(_ACTION_REGEX.finditer(cleaned))
    if not matches:
        return AgentAction(action_type=ActionType.INVALID, argument="", raw=text)

    # Use the last action directive emitted in the response
    last_match = matches[-1]
    verb = last_match.group(1).upper()
    arg = last_match.group(2).strip()

    if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
        arg = arg[1:-1].strip()

    action_type = ActionType.FETCH if verb == "FETCH" else ActionType.RESOLVE
    return AgentAction(
        action_type=action_type,
        argument=arg,
        raw=last_match.group(0),
    )


def format_action(action_type: ActionType, argument: str) -> str:
    """Format an action directive string."""
    if action_type == ActionType.INVALID:
        raise ValueError("Cannot format INVALID action type")
    return f"ACTION: {action_type.value} {argument.strip()}"


class CircuitBreakerStatus(str, Enum):
    """Termination status codes for the circuit breaker."""
    OK = "OK"
    TRIPPED_MAX_TURNS = "TRIPPED_MAX_TURNS"
    TRIPPED_CYCLE_DETECTED = "TRIPPED_CYCLE_DETECTED"
    TRIPPED_EMPTY_TARGET = "TRIPPED_EMPTY_TARGET"


@dataclass
class CircuitBreaker:
    """Enforces turn ceiling and prevents circular retrieval loops."""
    max_turns: int = 3
    turn_count: int = 0
    visited_targets: Set[str] = field(default_factory=set)
    is_tripped: bool = False
    trip_reason: str | None = None

    def validate_action(self, action: AgentAction) -> tuple[bool, CircuitBreakerStatus, str | None]:
        """Validate whether an action can be executed without violating safety bounds."""
        if self.is_tripped:
            return False, CircuitBreakerStatus.TRIPPED_MAX_TURNS, self.trip_reason

        if self.turn_count >= self.max_turns:
            reason = f"Max turns ceiling reached ({self.max_turns})"
            return False, CircuitBreakerStatus.TRIPPED_MAX_TURNS, reason

        if action.action_type == ActionType.FETCH:
            normalized_target = action.argument.strip().lower()
            if not normalized_target:
                reason = "FETCH directive contains empty target identifier"
                return False, CircuitBreakerStatus.TRIPPED_EMPTY_TARGET, reason
            if normalized_target in self.visited_targets:
                reason = f"Cycle detected: target '{action.argument}' has already been fetched"
                return False, CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED, reason

        return True, CircuitBreakerStatus.OK, None

    def record_step(self, action: AgentAction) -> None:
        """Record an executed step and update tracking state."""
        self.turn_count += 1
        if action.action_type == ActionType.FETCH:
            self.visited_targets.add(action.argument.strip().lower())

    def trip(self, status: CircuitBreakerStatus, reason: str) -> None:
        """Manually trip the circuit breaker."""
        self.is_tripped = True
        self.trip_reason = reason

    def reset(self) -> None:
        """Reset internal state for a fresh execution run."""
        self.turn_count = 0
        self.visited_targets.clear()
        self.is_tripped = False
        self.trip_reason = None


@dataclass
class TurnRecord:
    """Telemetry record for a single turn in the iterative loop."""
    turn_index: int
    prompt: str
    prompt_tokens: int
    raw_response: str
    action: AgentAction
    latency_ms: float
    retrieved_content: Optional[str] = None


@dataclass
class CoordinatorResult:
    """Final result emitted by the IterativeCoordinator."""
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
    """Coordinates host-managed iterative context extraction and turn dispatch."""

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

        return CoordinatorResult(
            status="MAX_TURNS_EXCEEDED",
            answer="",
            total_turns=self.max_turns,
            turns=turn_records,
            visited_targets=list(self.circuit_breaker.visited_targets),
            all_under_budget=all_under_budget,
            total_latency_ms=round((time.perf_counter() - t0_total) * 1000, 2),
        )
