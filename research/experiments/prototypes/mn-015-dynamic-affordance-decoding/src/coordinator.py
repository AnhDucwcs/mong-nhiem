"""Integrated Host Coordinator for MN-015: Dual-Layer Affordance Steering.

Orchestrates multi-turn task execution with Memento state checkpointing,
context rewinding, negative action directives, Phase Gate validation,
and Dual-Layer Affordance Steering:
- Layer 1: Prompt Attention Prior (compact active affordance listing <= 20 tokens)
- Layer 2: Dynamic Engine Logit Masking (per-turn compiled GBNF grammar)

Comparative experimental arms:
- Arm 1: Static GBNF grammar baseline (MN-014 standard)
- Arm 2: Full Dual-Layer Affordance Steering (MN-015 proposed)
"""
from __future__ import annotations

import copy
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from affordance_engine import AffordanceEngine
from circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from context_rewind import ContextRewindManager
from dynamic_gbnf import STATIC_FALLBACK_GBNF, compile_dynamic_gbnf
from memento_stack import MementoStack
from phase_gate import PhaseGateInterceptor
from protocol import (
    ActionType,
    Affordances,
    ToolAction,
    format_action,
    format_affordance_prior,
    format_negative_directive,
    parse_action,
)

SYSTEM_PROTOCOL_PROMPT = (
    "You are a stateful tool execution agent. Follow protocol strictly:\n"
    "Rule 1: If an action was REJECTED or uncommitted, choose an available alternative from affordances. NEVER resolve before committing.\n"
    "Rule 2: ONLY after mutation succeeds, RESOLVE the final value.\n\n"
    "Example 1 (Turn 1):\n"
    "Task: Transfer 50 from src to dst.\n"
    "Available Affordances: [DISPATCH transfer src,dst,50]\n"
    "Directive:\n"
    "ACTION: DISPATCH transfer src,dst,50\n\n"
    "Example 2 (Turn 2 rollback):\n"
    "Latest Observation: ROLLBACK_COMMITTED: Restored turn 1. REJECTED: DISPATCH:transfer:src,dst,50\n"
    "Available Affordances: [DISPATCH transfer backup,dst,50]\n"
    "Directive:\n"
    "ACTION: DISPATCH transfer backup,dst,50\n\n"
    "Example 3 (Resolve):\n"
    "Latest Observation: TRANSFER_COMMITTED balance_dst=500\n"
    "Available Affordances: [RESOLVE dst:500]\n"
    "Directive:\n"
    "ACTION: RESOLVE dst:500"
)


@dataclass
class TurnRecord:
    turn_index: int
    prompt: str
    prompt_tokens: int
    raw_response: str
    action: ToolAction
    observation: str
    is_rollback: bool
    latency_ms: float
    used_grammar: bool
    compiled_gbnf: Optional[str] = None


@dataclass
class CoordinatorResult:
    status: str  # "SUCCESS", "PREMATURE_RESOLVE", "MAX_TURNS_EXHAUSTED", "DEADLOCK_CYCLE_DETECTED"
    answer: str
    total_turns: int
    rollback_count: int
    turns: List[TurnRecord]
    all_under_budget: bool
    total_latency_ms: float
    final_environment: Dict[str, Any]


class Coordinator:
    """Integrated Host Coordinator for MN-015."""

    def __init__(
        self,
        arm: int = 2,
        max_turns: int = 7,
        max_budget: int = 512,
        model_fn: Optional[Callable[[str, Optional[str]], Tuple[str, float]]] = None,
        token_counter_fn: Optional[Callable[[str], int]] = None,
    ):
        self.arm = arm
        self.max_turns = max_turns
        self.max_budget = max_budget
        self.model_fn = model_fn or (lambda p, g: ("ACTION: RESOLVE unknown", 10.0))
        self.token_counter_fn = token_counter_fn or (lambda s: len(s) // 4)
        self.phase_gate = PhaseGateInterceptor()
        self.affordance_engine = AffordanceEngine()

    def _summarize_state(self, env: Dict[str, Any], domain: str) -> str:
        """Create compact deterministic state summary for working context."""
        lines: List[str] = []
        if domain == "code_mutation":
            rates = env.get("rates", {})
            for fn in sorted(rates.keys()):
                lines.append(f"Function {fn}: rate={rates[fn]}")
        elif domain == "resource_ledger":
            accs = env.get("accounts", {})
            for acc in sorted(accs.keys()):
                lines.append(f"Account {acc}: balance {accs[acc]}")
        elif domain == "system_registry":
            svcs = env.get("services", {})
            for svc in sorted(svcs.keys()):
                mode = svcs[svc].get("mode", "STOPPED")
                lines.append(f"Service {svc}: mode={mode}")
        return "\n".join(lines) if lines else "Empty State"

    def _execute_tool(self, action: ToolAction, env: Dict[str, Any], domain: str) -> Tuple[bool, str]:
        """Execute action mutation or query against L2 environment state."""
        if action.action_type == ActionType.READ:
            funcs = env.get("functions", {})
            if action.target in funcs:
                return True, funcs[action.target].strip()
            return False, f"ENTITY_NOT_FOUND: {action.target}"

        elif action.action_type == ActionType.INSPECT:
            target = action.target
            entity, prop = target.split(".", 1) if "." in target else (target, "status")
            if domain == "resource_ledger":
                accs = env.get("accounts", {})
                if entity in accs:
                    return True, str(accs[entity])
                return False, f"ACCOUNT_NOT_FOUND: {entity}"
            elif domain == "system_registry":
                svcs = env.get("services", {})
                if entity in svcs:
                    svc = svcs[entity]
                    return True, str(svc.get(prop, svc.get("mode", "UNKNOWN")))
                return False, f"SERVICE_NOT_FOUND: {entity}"
            return True, f"INSPECT_OK: {target}"

        elif action.action_type == ActionType.DISPATCH:
            tool_name = action.target
            payload = action.payload

            if domain == "code_mutation":
                clean_tool = re.sub(r"^(?:refactor_|inspect:?|mutate:?)", "", tool_name).strip(":, ")
                locked = env.get("locked_entities", [])
                for lk in locked:
                    if lk in clean_tool or lk in payload:
                        return False, f"SYNTAX_INVARIANT_VIOLATION: {lk} has locked malformed AST."

                if "=" in payload:
                    val = payload.split("=")[-1].strip()
                    env.setdefault("rates", {})[clean_tool] = val
                    return True, f"MUTATION_SUCCESS {clean_tool} updated ({payload})"
                return True, f"MUTATION_SUCCESS {clean_tool} applied"

            elif domain == "resource_ledger":
                clean_payload = payload.replace(":", ",")
                parts = [p.strip() for p in clean_payload.split(",") if p.strip()]
                if len(parts) == 3:
                    src, dst, amt_str = parts
                    try:
                        amt = int(amt_str)
                    except ValueError:
                        return False, "INVALID_AMOUNT_FORMAT"

                    accs = env.setdefault("accounts", {})
                    if accs.get(src, 0) < amt:
                        return False, f"INSUFFICIENT_FUNDS: {src} balance {accs.get(src, 0)} < {amt}"

                    accs[src] -= amt
                    accs[dst] = accs.get(dst, 0) + amt
                    return True, f"TRANSFER_COMMITTED balance_{dst}={accs[dst]}"
                return False, "INVALID_TRANSFER_SYNTAX"

            elif domain == "system_registry":
                clean_payload = payload.replace(":", ",")
                parts = [p.strip() for p in clean_payload.split(",") if p.strip()]
                locked_svcs = env.get("locked_services", [])
                if len(parts) >= 2:
                    svc = parts[0]
                    if svc in locked_svcs:
                        return False, f"LOCKED_SERVICE_CONFLICT: {svc} is locked for modification."

                    svcs = env.setdefault("services", {})
                    if len(parts) == 3:
                        key, val = parts[1], parts[2]
                        svcs.setdefault(svc, {})[key] = val
                        return True, f"CONFIG_UPDATED {svc}.{key}={val}"
                    elif len(parts) == 2:
                        mode = parts[1]
                        svcs.setdefault(svc, {})["mode"] = mode
                        return True, f"SERVICE_ACTIVATED {svc}:{mode}"
                return False, "INVALID_REGISTRY_COMMAND"

        return False, f"UNHANDLED_ACTION: {action.action_type}"

    def run(
        self,
        query: str,
        initial_env: Dict[str, Any],
        domain: str = "resource_ledger",
        target_predicate: Optional[Dict[str, Any]] = None,
    ) -> CoordinatorResult:
        current_env = copy.deepcopy(initial_env)
        stack = MementoStack(max_depth=3)
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

        for turn_idx in range(1, self.max_turns + 1):
            state_summary = self._summarize_state(current_env, domain)

            # Compute active affordances
            affordances = self.affordance_engine.get_active_affordances(
                domain=domain,
                env=current_env,
                query=query,
                rejected_actions=rejected_actions,
                target_predicate=target_predicate,
                turn_index=turn_idx,
            )

            # Arm-dependent steering configuration
            if self.arm == 2:
                # Layer 1: Prompt Attention Prior
                affordance_line = format_affordance_prior(affordances)
                if latest_observation == "None":
                    observation_with_affordance = affordance_line
                else:
                    observation_with_affordance = f"{latest_observation}\n{affordance_line}"

                # Layer 2: Dynamic Engine Logit Masking
                grammar_to_use = compile_dynamic_gbnf(affordances)
                use_grammar = True
            else:
                # Arm 1: Static GBNF Baseline (no prompt prior, static grammar)
                observation_with_affordance = latest_observation
                grammar_to_use = STATIC_FALLBACK_GBNF
                use_grammar = True

            prompt = context_mgr.build_turn_prompt(
                system_prompt=SYSTEM_PROTOCOL_PROMPT,
                task_query=query,
                state_summary=state_summary,
                latest_observation=observation_with_affordance,
            )
            prompt_tokens = self.token_counter_fn(prompt)
            if prompt_tokens > self.max_budget:
                all_under_budget = False

            # Model inference
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
                    used_grammar=use_grammar,
                    compiled_gbnf=grammar_to_use,
                ))
                return CoordinatorResult(
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
                if target_predicate:
                    passed, reason = self.phase_gate.intercept_resolve(current_env, target_predicate, action.payload)
                    if not passed:
                        # Reject premature resolve
                        latest_observation = f"PREMATURE_RESOLVE_REJECTED: {reason}. Required conditions NOT met. Continue execution."
                        turns.append(TurnRecord(
                            turn_index=turn_idx,
                            prompt=prompt,
                            prompt_tokens=prompt_tokens,
                            raw_response=raw_response,
                            action=action,
                            observation=latest_observation,
                            is_rollback=False,
                            latency_ms=latency_ms,
                            used_grammar=use_grammar,
                            compiled_gbnf=grammar_to_use,
                        ))
                        continue

                # Valid resolution
                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation="TASK_RESOLVED",
                    is_rollback=False,
                    latency_ms=latency_ms,
                    used_grammar=use_grammar,
                    compiled_gbnf=grammar_to_use,
                ))
                return CoordinatorResult(
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

            # Execute tool mutation
            success, obs = self._execute_tool(action, current_env, domain)

            if success:
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
                    used_grammar=use_grammar,
                    compiled_gbnf=grammar_to_use,
                ))
            else:
                # Execution failure: Host Backtracking Rollback
                rollback_count += 1
                rejected_actions.add(action.action_key)
                circuit_breaker.record_action(action.action_key, is_rejected=True)

                # Pop failed state and restore previous valid memento
                if stack.depth > 1:
                    snapshot = stack.pop()
                else:
                    snapshot = stack.peek()

                if snapshot is not None:
                    current_env = copy.deepcopy(snapshot.state)
                restore_turn = snapshot.turn_index if snapshot else 0
                neg_dir = format_negative_directive(action.action_key, obs)
                context_mgr.rewind(neg_dir)
                latest_observation = f"ROLLBACK_COMMITTED: Restored turn {restore_turn}. {neg_dir}"

                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation=latest_observation,
                    is_rollback=True,
                    latency_ms=latency_ms,
                    used_grammar=use_grammar,
                    compiled_gbnf=grammar_to_use,
                ))

        return CoordinatorResult(
            status="MAX_TURNS_EXHAUSTED",
            answer="",
            total_turns=self.max_turns,
            rollback_count=rollback_count,
            turns=turns,
            all_under_budget=all_under_budget,
            total_latency_ms=total_latency_ms,
            final_environment=current_env,
        )
