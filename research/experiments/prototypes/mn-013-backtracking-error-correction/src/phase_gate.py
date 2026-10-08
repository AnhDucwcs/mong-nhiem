"""Phase Gate Interceptor for MN-013.

Prevents "Horizon Jumping" (Failure Mode 3 from MN-012) where small models (<4B)
prematurely emit 'ACTION: RESOLVE' before the environment state satisfies the goal predicate.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple
from protocol import ActionType, ToolAction


class PhaseGateInterceptor:
    """Validates state predicates before permitting ACTION: RESOLVE."""

    @staticmethod
    def validate_resolution(
        action: ToolAction,
        current_state: Dict[str, Any],
        target_predicate: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Verify whether current state satisfies target predicate.
        
        Returns:
            (True, "VALID") if satisfied.
            (False, <rejection_reason>) if premature.
        """
        if action.action_type != ActionType.RESOLVE:
            return True, "NOT_RESOLVE"

        if not target_predicate:
            return True, "NO_PREDICATE_DEFINED"

        pred_type = target_predicate.get("type")

        if pred_type == "function_rate_updated":
            target_func = target_predicate.get("target_func")
            expected_val = str(target_predicate.get("expected_value"))
            funcs = current_state.get("functions", {})
            func_def = funcs.get(target_func, "")
            # Check if updated value is present in function code or rates table
            rates = current_state.get("rates", {})
            if rates.get(target_func) == expected_val or f"rate = {expected_val}" in func_def or expected_val in func_def:
                return True, "PREDICATE_SATISFIED"
            return False, f"PREMATURE_RESOLVE: Function {target_func} has not been updated to expected rate {expected_val}."

        elif pred_type == "account_balance_equals":
            account = target_predicate.get("account")
            expected_balance = target_predicate.get("expected_balance")
            accounts = current_state.get("accounts", {})
            actual_balance = accounts.get(account)
            if actual_balance == expected_balance:
                return True, "PREDICATE_SATISFIED"
            return False, f"PREMATURE_RESOLVE: Account {account} balance is {actual_balance}, expected {expected_balance}."

        elif pred_type == "service_flag_equals":
            service = target_predicate.get("service")
            flag = target_predicate.get("flag")
            expected_val = target_predicate.get("expected_val")
            services = current_state.get("services", {})
            svc_data = services.get(service, {})
            actual_val = svc_data.get(flag)
            if actual_val == expected_val:
                return True, "PREDICATE_SATISFIED"
            return False, f"PREMATURE_RESOLVE: Service {service} flag {flag} is {actual_val}, expected {expected_val}."

        return True, "UNKNOWN_PREDICATE_PASS"
