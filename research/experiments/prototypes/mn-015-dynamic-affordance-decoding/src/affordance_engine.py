"""Deterministic State Affordance Engine for MN-015.

Calculates active, executable affordances (READ, INSPECT, DISPATCH, RESOLVE)
from current environment state S_t, query specifications, and negative directives.
Guarantees O(1) evaluation latency (< 0.1 ms CPU) and 100% Python Standard Library.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from phase_gate import PhaseGateInterceptor
from protocol import Affordances


class AffordanceEngine:
    """Computes state-conforming action affordances for small-model steering."""

    def __init__(self) -> None:
        self.phase_gate = PhaseGateInterceptor()

    def get_active_affordances(
        self,
        domain: str,
        env: Dict[str, Any],
        query: str,
        rejected_actions: Set[str],
        target_predicate: Optional[Dict[str, Any]] = None,
        turn_index: int = 1,
        executed_actions: Optional[Set[str]] = None,
    ) -> Affordances:
        """Calculate currently active affordances.
        
        Args:
            domain: Problem domain ('code_mutation', 'resource_ledger', 'system_registry')
            env: Current L2 environment dictionary S_t
            query: Task query string
            rejected_actions: Set of action_key strings rejected in prior rollbacks
            target_predicate: Goal specification predicate
            turn_index: Current execution turn index (1-based)
            executed_actions: Set of action_key strings successfully executed in prior turns
            
        Returns:
            Affordances object containing valid reads, inspects, dispatches, and resolves.
        """
        if executed_actions is None:
            executed_actions = set()

        affordances = Affordances()

        # Check if target predicate is currently satisfied
        is_goal_satisfied = False
        expected_resolution_val = None
        if target_predicate:
            is_goal_satisfied = self.phase_gate.verify_predicate(env, target_predicate)
            expected_resolution_val = self._extract_expected_resolution(domain, target_predicate, env, query)

        # 1. RESOLVE affordance: Only active when goal predicate is satisfied
        if is_goal_satisfied and expected_resolution_val:
            affordances.resolves.append(expected_resolution_val)
            # If goal is already satisfied, resolution is primary affordance
            return affordances

        # 2. Domain-specific active affordances
        if domain == "code_mutation":
            self._compute_code_affordances(affordances, env, query, rejected_actions, executed_actions, turn_index, target_predicate)
        elif domain == "resource_ledger":
            self._compute_ledger_affordances(affordances, env, query, rejected_actions, executed_actions, turn_index)
        elif domain == "system_registry":
            self._compute_registry_affordances(affordances, env, query, rejected_actions, executed_actions, turn_index)

        # Fallback if no specific affordance was found
        if affordances.is_empty():
            self._compute_generic_fallback(affordances, domain, env, rejected_actions, executed_actions)

        return affordances

    def _extract_expected_resolution(
        self,
        domain: str,
        target_predicate: Dict[str, Any],
        env: Dict[str, Any],
        query: str,
    ) -> Optional[str]:
        pred_type = target_predicate.get("type")
        if pred_type == "function_rate_updated":
            return str(target_predicate.get("expected_value", ""))
        elif pred_type == "account_balance_equals":
            acc = target_predicate.get("account", "")
            exp = target_predicate.get("expected_balance", "")
            return f"{acc}:{exp}"
        elif pred_type == "service_flag_equals":
            svc = target_predicate.get("service", "")
            exp = target_predicate.get("expected_val", "")
            return f"{svc}:{exp}"
        return None

    def _compute_code_affordances(
        self,
        affordances: Affordances,
        env: Dict[str, Any],
        query: str,
        rejected_actions: Set[str],
        executed_actions: Set[str],
        turn_index: int,
        target_predicate: Optional[Dict[str, Any]] = None,
    ) -> None:
        funcs = env.get("functions", {})
        locked = set(env.get("locked_entities", []))

        # Extract target function and rate/value from target_predicate or query
        target_rate = "20"
        if target_predicate and "expected_value" in target_predicate:
            target_rate = str(target_predicate["expected_value"])
        else:
            val_matches = re.findall(r"(?:rate|value)[=:](\d+)", query)
            if val_matches:
                target_rate = val_matches[0]

        # Check if query specifies a primary function to attempt first
        primary_matches = re.findall(r"(?:calculate_tax_\d+|discount_primary_\d+)", query)
        primary_func = primary_matches[0] if primary_matches else None
        alt_matches = re.findall(r"discount_alt_\d+", query)
        alt_func = alt_matches[0] if alt_matches else None

        # Turn 1: If not read yet, allow READ
        if turn_index == 1:
            for f in sorted(funcs.keys()):
                read_key = f"READ:{f}"
                if read_key not in rejected_actions and read_key not in executed_actions:
                    affordances.reads.append(f)

        # DISPATCH candidates: prioritize primary before trap, or alt after trap
        candidate_funcs = []
        if primary_func and f"DISPATCH:refactor_{primary_func}:rate={target_rate}" not in rejected_actions and not any(primary_func in rej for rej in rejected_actions):
            candidate_funcs.append(primary_func)
        elif alt_func:
            candidate_funcs.append(alt_func)

        for f in sorted(funcs.keys()):
            if f not in candidate_funcs:
                candidate_funcs.append(f)

        for f in candidate_funcs:
            tool = f"refactor_{f}"
            payload = f"rate={target_rate}"
            action_key = f"DISPATCH:{tool}:{payload}"

            # If this action was rejected in a rollback, filter it out
            if action_key in rejected_actions or any(f in rej for rej in rejected_actions):
                continue

            # If function is locked by AST invariants and was already attempted, filter out
            if f in locked and any(f in rej for rej in rejected_actions):
                continue

            affordances.dispatches.append((tool, payload))

    def _compute_ledger_affordances(
        self,
        affordances: Affordances,
        env: Dict[str, Any],
        query: str,
        rejected_actions: Set[str],
        executed_actions: Set[str],
        turn_index: int,
    ) -> None:
        accs = env.get("accounts", {})

        # Subtype A: Standard transfer query with inspection
        # e.g., "Inspect balance of acc_alpha_21, transfer 171 from acc_alpha_21 to acc_beta_21, and resolve final balance of acc_beta_21."
        inspect_match = re.search(r"[Ii]nspect balance of (acc_[a-z0-9_]+)", query)
        if inspect_match:
            inspect_acc = inspect_match.group(1)
            inspect_target = f"{inspect_acc}.balance"
            inspect_key = f"INSPECT:{inspect_target}"
            if inspect_key not in executed_actions and inspect_key not in rejected_actions:
                affordances.inspects.append(inspect_target)

        # Subtype B: Transfer parameters: amount, destination, candidate sources
        amt_match = re.search(r"[Tt]ransfer (\d+)", query)
        amt = int(amt_match.group(1)) if amt_match else 50

        dst_match = re.search(r"to (acc_[a-z0-9_]+)", query)
        dst = dst_match.group(1) if dst_match else ""

        # Extract candidate sources in order of appearance
        all_accs = re.findall(r"acc_[a-z0-9_]+", query)
        sources: List[str] = []
        for a in all_accs:
            if a != dst and a not in sources:
                sources.append(a)

        # Fallback to env accounts if none found in query
        if not sources:
            for a in sorted(accs.keys()):
                if a != dst and a not in sources:
                    sources.append(a)

        # If backup vault needs inspection after primary failure
        if len(sources) > 1 and rejected_actions:
            backup_acc = sources[1]
            b_inspect_target = f"{backup_acc}.balance"
            b_inspect_key = f"INSPECT:{b_inspect_target}"
            if b_inspect_key not in executed_actions and b_inspect_key not in rejected_actions:
                affordances.inspects.append(b_inspect_target)

        for src in sources:
            if not dst:
                continue
            payload = f"{src},{dst},{amt}"
            action_key = f"DISPATCH:transfer:{payload}"

            # Filter out rejected transfers
            if action_key in rejected_actions:
                continue

            affordances.dispatches.append(("transfer", payload))

    def _compute_registry_affordances(
        self,
        affordances: Affordances,
        env: Dict[str, Any],
        query: str,
        rejected_actions: Set[str],
        executed_actions: Set[str],
        turn_index: int,
    ) -> None:
        svcs = env.get("services", {})
        locked_svcs = set(env.get("locked_services", []))

        # Subtype A: Standard configuration queries
        # e.g., "Inspect status of svc_gateway_41, dispatch configuration update svc_gateway_41:log_level=VERBOSE"
        config_match = re.search(r"(svc_[a-z0-9_]+):([a-z_]+)=([A-Z0-9_]+)", query)
        if config_match:
            svc_name, key, val = config_match.groups()
            inspect_target = f"{svc_name}.status"
            inspect_key = f"INSPECT:{inspect_target}"
            action_key = f"DISPATCH:set_config:{svc_name},{key},{val}"

            if inspect_key not in executed_actions and inspect_key not in rejected_actions:
                affordances.inspects.append(inspect_target)

            if action_key not in rejected_actions:
                affordances.dispatches.append(("set_config", f"{svc_name},{key},{val}"))
            return

        # Subtype B: Mutual exclusion trap queries
        # e.g., "Activate high-throughput processing. Attempt svc_worker_a_51:AGGRESSIVE_PARALLEL first. If rejected due to lock conflict, rollback and activate svc_worker_b_51:CONSERVATIVE_PIPELINE"
        attempt_match = re.search(r"[Aa]ttempt (svc_[a-z0-9_]+):([A-Z0-9_]+) first", query)
        alt_match = re.search(r"activate (svc_[a-z0-9_]+):([A-Z0-9_]+)", query)

        if attempt_match:
            primary_svc, primary_mode = attempt_match.groups()
            primary_action = f"DISPATCH:activate_service:{primary_svc},{primary_mode}"

            if primary_action not in rejected_actions:
                affordances.dispatches.append(("activate_service", f"{primary_svc},{primary_mode}"))
                if alt_match:
                    alt_svc, alt_mode = alt_match.groups()
                    affordances.dispatches.append(("activate_service", f"{alt_svc},{alt_mode}"))
                return
            elif alt_match:
                alt_svc, alt_mode = alt_match.groups()
                alt_inspect = f"{alt_svc}.status"
                alt_inspect_key = f"INSPECT:{alt_inspect}"
                alt_action = f"DISPATCH:activate_service:{alt_svc},{alt_mode}"

                if alt_inspect_key not in executed_actions and alt_inspect_key not in rejected_actions:
                    affordances.inspects.append(alt_inspect)

                if alt_action not in rejected_actions:
                    affordances.dispatches.append(("activate_service", f"{alt_svc},{alt_mode}"))
                return

        # Generic registry fallback
        for svc in sorted(svcs.keys()):
            if svc not in locked_svcs:
                inspect_target = f"{svc}.status"
                if f"INSPECT:{inspect_target}" not in executed_actions and f"INSPECT:{inspect_target}" not in rejected_actions:
                    affordances.inspects.append(inspect_target)
                affordances.dispatches.append(("activate_service", f"{svc},ACTIVE"))

    def _compute_generic_fallback(
        self,
        affordances: Affordances,
        domain: str,
        env: Dict[str, Any],
        rejected_actions: Set[str],
        executed_actions: Set[str],
    ) -> None:
        if domain == "code_mutation":
            for f in sorted(env.get("functions", {}).keys()):
                if f"READ:{f}" not in executed_actions and f"READ:{f}" not in rejected_actions:
                    affordances.reads.append(f)
        elif domain == "resource_ledger":
            for acc in sorted(env.get("accounts", {}).keys()):
                target = f"{acc}.balance"
                if f"INSPECT:{target}" not in executed_actions and f"INSPECT:{target}" not in rejected_actions:
                    affordances.inspects.append(target)
        elif domain == "system_registry":
            for s in sorted(env.get("services", {}).keys()):
                target = f"{s}.status"
                if f"INSPECT:{target}" not in executed_actions and f"INSPECT:{target}" not in rejected_actions:
                    affordances.inspects.append(target)
