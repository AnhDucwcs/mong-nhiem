"""Deterministic Phase Gate and Predicate Evaluator.

Guarantees causal termination integrity by verifying whether environment
state S_t satisfies the goal predicate before permitting the RESOLVE action.
100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple


class PhaseGate:
    """Evaluates predicate invariants and intercepts premature resolution."""

    def __init__(self) -> None:
        self._custom_evaluators: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], bool]] = {}

    def register_predicate_evaluator(
        self,
        pred_type: str,
        evaluator_fn: Callable[[Dict[str, Any], Dict[str, Any]], bool],
    ) -> None:
        """Register custom predicate evaluator for specialized environments."""
        self._custom_evaluators[pred_type] = evaluator_fn

    def verify_predicate(self, env: Dict[str, Any], predicate: Dict[str, Any]) -> bool:
        """Evaluate if environment state satisfies goal predicate."""
        if not predicate:
            return True

        pred_type = predicate.get("type", "")

        # Check custom evaluators first
        if pred_type in self._custom_evaluators:
            return self._custom_evaluators[pred_type](env, predicate)

        # Standard predicate evaluators
        if pred_type == "function_rate_updated":
            func = predicate.get("target_func", "")
            exp_val = str(predicate.get("expected_value", ""))
            rates = env.get("rates", {})
            return str(rates.get(func, "")) == exp_val

        elif pred_type == "account_balance_equals":
            acc = predicate.get("account", "")
            exp_bal = int(predicate.get("expected_balance", -1))
            accs = env.get("accounts", {})
            return int(accs.get(acc, -999)) == exp_bal

        elif pred_type == "service_flag_equals":
            svc = predicate.get("service", "")
            flag = predicate.get("flag", "mode")
            exp_val = predicate.get("expected_val", "")
            svcs = env.get("services", {})
            if svc in svcs:
                return str(svcs[svc].get(flag, "")) == str(exp_val)
            return False

        elif pred_type == "equals":
            key_path = predicate.get("key_path", [])
            expected = predicate.get("expected")
            curr = env
            for k in key_path:
                if isinstance(curr, dict) and k in curr:
                    curr = curr[k]
                else:
                    return False
            return curr == expected

        return False

    def intercept_resolve(
        self,
        env: Dict[str, Any],
        predicate: Optional[Dict[str, Any]],
        resolve_payload: str,
    ) -> Tuple[bool, str]:
        """Intercept and validate RESOLVE action against goal predicate.
        
        Returns:
            Tuple of (is_valid, observation_message)
        """
        if not predicate:
            return True, "RESOLVE_ACCEPTED"

        if not self.verify_predicate(env, predicate):
            return False, "PREMATURE_RESOLUTION_REJECTED: Goal predicate not yet satisfied."

        return True, "TASK_RESOLVED"
