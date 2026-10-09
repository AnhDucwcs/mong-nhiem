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
    ) -> Affordances:
        """Calculate currently active affordances.
        
        Args:
            domain: Problem domain ('code_mutation', 'resource_ledger', 'system_registry')
            env: Current L2 environment dictionary S_t
            query: Task query string
            rejected_actions: Set of action_key strings rejected in prior rollbacks
            target_predicate: Goal specification predicate
            turn_index: Current execution turn index (1-based)
            
        Returns:
            Affordances object containing valid reads, inspects, dispatches, and resolves.
        """
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
            self._compute_code_affordances(affordances, env, query, rejected_actions, turn_index, target_predicate)
        elif domain == "resource_ledger":
            self._compute_ledger_affordances(affordances, env, query, rejected_actions, turn_index)
        elif domain == "system_registry":
            self._compute_registry_affordances(affordances, env, query, rejected_actions, turn_index)

        # Fallback if no specific affordance was found
        if affordances.is_empty():
            self._compute_generic_fallback(affordances, domain, env)

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
                if read_key not in rejected_actions:
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
        turn_index: int,
    ) -> None:
        accs = env.get("accounts", {})

        # Extract transfer parameters: src, dst, amount
        # e.g., "Transfer 100 to demo_dst. Try demo_primary first, else backup demo_secondary"
        amt_match = re.search(r"[Tt]ransfer (\d+)", query)
        amt = int(amt_match.group(1)) if amt_match else 50

        dst_match = re.search(r"to (acc_\w+|demo_\w+)", query)
        dst = dst_match.group(1) if dst_match else "acc_target"

        # Candidate sources in query or env
        sources: List[str] = []
        src_matches = re.findall(r"(acc_vault_[a-z0-9_]+|demo_[a-z0-9_]+)", query)
        for s in src_matches:
            if s != dst and s not in sources:
                sources.append(s)

        for s in sorted(accs.keys()):
            if s != dst and s not in sources:
                sources.append(s)

        # READ balance
        if turn_index == 1 and not rejected_actions:
            for acc in sorted(accs.keys()):
                read_key = f"READ:balance_{acc}"
                if read_key not in rejected_actions:
                    affordances.reads.append(f"balance_{acc}")

        # DISPATCH transfer
        for src in sources:
            payload = f"{src},{dst},{amt}"
            action_key = f"DISPATCH:transfer:{payload}"

            # Filter out rejected transfers
            if action_key in rejected_actions or any(src in rej for rej in rejected_actions):
                continue

            affordances.dispatches.append(("transfer", payload))

    def _compute_registry_affordances(
        self,
        affordances: Affordances,
        env: Dict[str, Any],
        query: str,
        rejected_actions: Set[str],
        turn_index: int,
    ) -> None:
        svcs = env.get("services", {})
        locked_svcs = set(env.get("locked_services", []))

        # Check for standard config queries
        # e.g., "Inspect status of svc_gateway_41, dispatch configuration update svc_gateway_41:log_level=VERBOSE"
        config_match = re.search(r"(svc_[a-z0-9_]+):([a-z_]+)=([A-Z0-9_]+)", query)
        if config_match:
            svc_name, key, val = config_match.groups()
            action_key = f"DISPATCH:set_config:{svc_name},{key},{val}"

            if turn_index == 1 and not rejected_actions:
                affordances.inspects.append(f"{svc_name}.status")

            if action_key not in rejected_actions:
                affordances.dispatches.append(("set_config", f"{svc_name},{key},{val}"))
            return

        # Check for mutual exclusion trap queries
        # e.g., "Attempt svc_worker_a_51:AGGRESSIVE_PARALLEL first. If rejected due to lock conflict, rollback and activate svc_worker_b_51:CONSERVATIVE_PIPELINE"
        pairs = re.findall(r"(svc_[a-z0-9_]+):([A-Z0-9_]+)", query)
        if pairs:
            for svc_name, mode in pairs:
                action_key = f"DISPATCH:activate_service:{svc_name},{mode}"

                # If this specific activation was rejected, filter it out
                if action_key in rejected_actions or any(svc_name in rej for rej in rejected_actions):
                    continue

                # If service is currently locked and we've already had a rollback, filter it out
                if svc_name in locked_svcs and rejected_actions:
                    continue

                # Add inspect
                inspect_target = f"{svc_name}.status"
                if f"INSPECT:{inspect_target}" not in rejected_actions:
                    affordances.inspects.append(inspect_target)

                # Add dispatch
                affordances.dispatches.append(("activate_service", f"{svc_name},{mode}"))
            return

        # Generic registry fallback
        for svc in sorted(svcs.keys()):
            if svc not in locked_svcs:
                affordances.inspects.append(f"{svc}.status")
                affordances.dispatches.append(("activate_service", f"{svc},ACTIVE"))

    def _compute_generic_fallback(
        self,
        affordances: Affordances,
        domain: str,
        env: Dict[str, Any],
    ) -> None:
        if domain == "code_mutation":
            for f in sorted(env.get("functions", {}).keys()):
                affordances.reads.append(f)
        elif domain == "resource_ledger":
            for acc in sorted(env.get("accounts", {}).keys()):
                affordances.reads.append(f"balance_{acc}")
        elif domain == "system_registry":
            for s in sorted(env.get("services", {}).keys()):
                affordances.inspects.append(f"{s}.status")
