"""Host-Directed Backtracking & Working Set Coordinator for MN-013.

Supports 4 experimental arms:
- Arm 1: Forward-Only Baseline (no rollback, no rewind)
- Arm 2: Naive History Accumulation (errors appended to prompt context)
- Arm 3: Context Rewind Only (state rolled back, context rewound, NO negative mask)
- Arm 4: Full MN-013 (Memento rollback + Context rewind + Negative mask + Phase gate)
"""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from context_rewind import ContextRewindManager
from memento_stack import MementoStack
from phase_gate import PhaseGateInterceptor
from protocol import ActionType, ToolAction, format_action, format_negative_directive, parse_action


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


@dataclass
class CoordinatorResult:
    status: str
    answer: str
    total_turns: int
    rollback_count: int
    turns: List[TurnRecord] = field(default_factory=list)
    all_under_budget: bool = True
    total_latency_ms: float = 0.0
    final_environment: Dict[str, Any] = field(default_factory=dict)


SYSTEM_PROTOCOL_PROMPT = (
    "You are a stateful tool execution agent. Follow protocol strictly:\n"
    "Rule 1: If Observation is None, or if an action was REJECTED, DISPATCH or READ the required tool action. NEVER resolve before committing.\n"
    "Rule 2: ONLY after MUTATION_SUCCESS, TRANSFER_COMMITTED, or SERVICE_ACTIVATED, RESOLVE the final value.\n\n"
    "Example 1 (Turn 1 start):\n"
    "Task: Transfer 50 from demo_src to demo_dst and resolve balance of demo_dst.\n"
    "Recent History: None\n"
    "Latest Observation: None\n"
    "Directive: ACTION: DISPATCH transfer demo_src,demo_dst,50\n\n"
    "Example 2 (Turn 2 recovery after rejection):\n"
    "Task: Transfer 200 to demo_dst. Try demo_primary first, else backup demo_secondary.\n"
    "Recent History: None\n"
    "Latest Observation: ROLLBACK_COMMITTED: Restored turn 1. REJECTED: DISPATCH:transfer:demo_primary,demo_dst,200 (INSUFFICIENT_FUNDS). Do NOT repeat this action. Choose an alternative step.\n"
    "Constraint: REJECTED: DISPATCH:transfer:demo_primary,demo_dst,200. Do NOT use demo_primary.\n"
    "Directive: ACTION: DISPATCH transfer demo_secondary,demo_dst,200\n\n"
    "Example 3 (Final turn resolve):\n"
    "Task: Transfer 200 to demo_dst.\n"
    "Recent History: ACTION: DISPATCH transfer demo_secondary,demo_dst,200 -> TRANSFER_COMMITTED balance_demo_dst=500\n"
    "Latest Observation: TRANSFER_COMMITTED balance_demo_dst=500\n"
    "Directive: ACTION: RESOLVE demo_dst:500"
)


class BacktrackingCoordinator:
    def __init__(
        self,
        model_fn: Callable[[str], str],
        token_counter_fn: Optional[Callable[[str], int]] = None,
        max_turns: int = 7,
        max_budget: int = 512,
        arm: int = 4,
    ):
        self.model_fn = model_fn
        self.token_counter_fn = token_counter_fn or (lambda p: len(p) // 4)
        self.max_turns = max_turns
        self.max_budget = max_budget
        self.arm = arm

    def _summarize_state(self, env: Dict[str, Any], domain: str) -> str:
        """Create a compact L1 state summary string (<= 100 tokens)."""
        if domain == "code_mutation":
            funcs = env.get("functions", {})
            return ", ".join(f"{k}:present" for k in funcs.keys())
        elif domain == "resource_ledger":
            accs = env.get("accounts", {})
            return ", ".join(f"{k}={v}" for k, v in accs.items())
        elif domain == "system_registry":
            svcs = env.get("services", {})
            return ", ".join(f"{k}:{v.get('mode', v.get('status', ''))}" for k, v in svcs.items())
        return "env:initialized"

    def _execute_tool(
        self,
        action: ToolAction,
        env: Dict[str, Any],
        domain: str,
    ) -> tuple[bool, str]:
        """Execute action against environment.
        
        Returns:
            (success: bool, observation: str)
        """
        if action.action_type == ActionType.READ:
            funcs = env.get("functions", {})
            if action.target in funcs:
                return True, f"CODE_CONTENT: {funcs[action.target][:60]}..."
            return False, f"ENTITY_NOT_FOUND: {action.target}"

        elif action.action_type == ActionType.INSPECT:
            target = action.target
            if "." in target:
                entity, prop = target.split(".", 1)
            else:
                entity, prop = target, "status"

            if domain == "resource_ledger":
                accs = env.get("accounts", {})
                if entity in accs:
                    return True, str(accs[entity])
                return False, f"ACCOUNT_NOT_FOUND: {entity}"
            elif domain == "system_registry":
                svcs = env.get("services", {})
                if entity in svcs:
                    svc = svcs[entity]
                    return True, str(svc.get(prop, svc.get("status", "UNKNOWN")))
                return False, f"SERVICE_NOT_FOUND: {entity}"
            return True, f"INSPECT_OK: {target}"

        elif action.action_type == ActionType.DISPATCH:
            tool_name = action.target
            payload = action.payload

            if domain == "code_mutation":
                clean_tool = re.sub(r"^(?:refactor_|inspect:?|mutate:?)", "", tool_name).strip(":, ")
                # Check locked/syntax error trap
                locked = env.get("locked_entities", [])
                for lk in locked:
                    if lk in clean_tool or lk in payload:
                        return False, f"SYNTAX_INVARIANT_VIOLATION: {lk} has locked malformed AST."

                # Successful mutation
                if "=" in payload:
                    val = payload.split("=")[-1].strip()
                    env.setdefault("rates", {})[clean_tool] = val
                    return True, f"MUTATION_SUCCESS {clean_tool} updated ({payload})"
                return True, f"MUTATION_SUCCESS {clean_tool} applied"

            elif domain == "resource_ledger":
                # Format: transfer src,dst,amount (support comma or colon)
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
                # Format: set_config svc,key,val OR activate_service svc,mode (support comma or colon)
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

        # Push initial baseline state
        stack.push(turn_index=0, state=current_env, action_key="INITIAL_STATE")

        turns: List[TurnRecord] = []
        latest_observation = "None"
        rollback_count = 0
        all_under_budget = True
        total_latency_ms = 0.0

        for turn_idx in range(1, self.max_turns + 1):
            t_start = time.perf_counter()
            state_summary = self._summarize_state(current_env, domain)

            prompt = context_mgr.build_turn_prompt(
                system_prompt=SYSTEM_PROTOCOL_PROMPT,
                task_query=query,
                state_summary=state_summary,
                latest_observation=latest_observation,
                arm=self.arm,
            )
            prompt_tokens = self.token_counter_fn(prompt)
            if prompt_tokens > self.max_budget:
                all_under_budget = False

            # Model inference
            raw_response = self.model_fn(prompt)
            action = parse_action(raw_response)
            cb_status = circuit_breaker.record_action(action.action_key)

            if cb_status == CircuitBreakerStatus.TRIPPED_CYCLE_DETECTED:
                latency_ms = (time.perf_counter() - t_start) * 1000.0
                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation="CIRCUIT_BREAKER: CYCLE_DETECTED",
                    is_rollback=False,
                    latency_ms=latency_ms,
                ))
                return CoordinatorResult(
                    status="DEADLOCK_CYCLE_DETECTED",
                    answer="",
                    total_turns=turn_idx,
                    rollback_count=rollback_count,
                    turns=turns,
                    all_under_budget=all_under_budget,
                    total_latency_ms=total_latency_ms + latency_ms,
                    final_environment=current_env,
                )

            # Check RESOLVE via Phase Gate (Arm 4 only, Arms 1-3 skip phase gate)
            if action.action_type == ActionType.RESOLVE:
                if self.arm == 4 and target_predicate:
                    is_valid, reason = PhaseGateInterceptor.validate_resolution(
                        action=action,
                        current_state=current_env,
                        target_predicate=target_predicate,
                    )
                    if not is_valid:
                        # Intercepted premature resolve!
                        latest_observation = f"REJECTED: {reason}"
                        context_mgr.rewind_arm4(f"REJECTED: RESOLVE ({reason}). Continue task exploration.")
                        latency_ms = (time.perf_counter() - t_start) * 1000.0
                        turns.append(TurnRecord(
                            turn_index=turn_idx,
                            prompt=prompt,
                            prompt_tokens=prompt_tokens,
                            raw_response=raw_response,
                            action=action,
                            observation=latest_observation,
                            is_rollback=False,
                            latency_ms=latency_ms,
                        ))
                        total_latency_ms += latency_ms
                        continue

                # Valid resolution or Arms 1-3
                latency_ms = (time.perf_counter() - t_start) * 1000.0
                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation=f"RESOLVED: {action.payload}",
                    is_rollback=False,
                    latency_ms=latency_ms,
                ))
                return CoordinatorResult(
                    status="RESOLVED",
                    answer=action.payload,
                    total_turns=turn_idx,
                    rollback_count=rollback_count,
                    turns=turns,
                    all_under_budget=all_under_budget,
                    total_latency_ms=total_latency_ms + latency_ms,
                    final_environment=current_env,
                )

            # Handle Tool Execution
            if action.action_type in (ActionType.READ, ActionType.INSPECT, ActionType.DISPATCH):
                # Save snapshot before stateful dispatch in Arms 3 & 4
                if action.action_type == ActionType.DISPATCH and self.arm in (3, 4):
                    stack.push(turn_index=turn_idx, state=current_env, action_key=action.action_key)

                success, obs = self._execute_tool(action, current_env, domain)

                if success:
                    latest_observation = obs
                    context_mgr.record_success(format_action(action), obs)
                    is_rollback_turn = False
                else:
                    # Action rejected / trap hit!
                    circuit_breaker.record_action(action.action_key, is_rejected=True)
                    if self.arm == 1:
                        # Arm 1: Forward-only (no rollback, state remains or aborts)
                        latest_observation = f"ACTION_REJECTED: {obs}"
                        is_rollback_turn = False
                    elif self.arm == 2:
                        # Arm 2: Naive History (no rollback, appends error to context)
                        latest_observation = f"ACTION_REJECTED: {obs}"
                        context_mgr.record_failure_arm2(format_action(action), obs)
                        is_rollback_turn = False
                    elif self.arm == 3:
                        # Arm 3: Rollback state, rewind context, NO negative directive
                        snapshot = stack.pop()
                        current_env = copy.deepcopy(snapshot.state)
                        context_mgr.rewind_arm3()
                        latest_observation = f"ROLLBACK_COMMITTED: Restored turn {snapshot.turn_index}"
                        rollback_count += 1
                        is_rollback_turn = True
                    elif self.arm == 4:
                        # Arm 4: Full MN-013 (Rollback state + Rewind context + Negative directive)
                        snapshot = stack.pop()
                        current_env = copy.deepcopy(snapshot.state)
                        neg_dir = format_negative_directive(action.action_key, obs)
                        context_mgr.rewind_arm4(neg_dir)
                        latest_observation = f"ROLLBACK_COMMITTED: Restored turn {snapshot.turn_index}. {neg_dir}"
                        rollback_count += 1
                        is_rollback_turn = True

                latency_ms = (time.perf_counter() - t_start) * 1000.0
                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation=latest_observation,
                    is_rollback=is_rollback_turn,
                    latency_ms=latency_ms,
                ))
                total_latency_ms += latency_ms

            else:
                # Invalid action format
                latency_ms = (time.perf_counter() - t_start) * 1000.0
                turns.append(TurnRecord(
                    turn_index=turn_idx,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    raw_response=raw_response,
                    action=action,
                    observation="SYNTAX_ERROR: Invalid action format",
                    is_rollback=False,
                    latency_ms=latency_ms,
                ))
                total_latency_ms += latency_ms

        return CoordinatorResult(
            status="MAX_TURNS_EXCEEDED",
            answer="",
            total_turns=self.max_turns,
            rollback_count=rollback_count,
            turns=turns,
            all_under_budget=all_under_budget,
            total_latency_ms=total_latency_ms,
            final_environment=current_env,
        )
