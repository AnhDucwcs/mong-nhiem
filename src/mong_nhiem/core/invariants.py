"""Host-authoritative physical conservation law and invariant validation primitives."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple


class InvariantViolationError(ValueError):
    """Raised when an operation or proposed state violates registered system invariants."""

    pass


class ConservationInvariantGuard:
    """Validates physical and domain invariants prior to authoritative host state commit."""

    def __init__(
        self,
        default_non_negative_keys: Optional[List[str]] = None,
    ):
        self.non_negative_keys: set[str] = set(
            default_non_negative_keys
            or [
                "mass",
                "energy",
                "charge",
                "power",
                "inventory",
                "volume",
                "pressure",
                "coolant",
                "battery",
                "soc",
                "stored_energy",
                "oxygen",
            ]
        )
        self.rules: Dict[str, Callable[[Dict[str, Any], Optional[Dict[str, Any]]], Tuple[bool, Optional[str]]]] = {}

    def register_rule(
        self,
        name: str,
        validator_fn: Callable[[Dict[str, Any], Optional[Dict[str, Any]]], Tuple[bool, Optional[str]]],
    ) -> None:
        """Registers a named invariant validation function.
        
        Args:
            name: Unique rule name.
            validator_fn: Callable taking (state, context) and returning (is_valid, failure_reason).
        """
        self.rules[name] = validator_fn

    def check_non_negativity(self, state: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Recursively checks that registered physical keys are not strictly negative (< 0)."""
        stack: List[Tuple[str, Any]] = [("", state)]
        while stack:
            path, current = stack.pop()
            if isinstance(current, dict):
                for k, v in current.items():
                    sub_path = f"{path}.{k}" if path else k
                    if k in self.non_negative_keys and isinstance(v, (int, float)):
                        if v < 0.0:
                            return False, f"INVARIANT_BREACH: Property '{sub_path}' has negative value: {v}"
                    if isinstance(v, (dict, list)):
                        stack.append((sub_path, v))
            elif isinstance(current, list):
                for idx, item in enumerate(current):
                    stack.append((f"{path}[{idx}]", item))
        return True, None

    def validate(
        self,
        state: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Validates all registered invariants against state and optional context.
        
        Returns:
            (is_valid, Optional[failure_reason])
        """
        valid_nn, err_nn = self.check_non_negativity(state)
        if not valid_nn:
            return False, err_nn

        for rule_name, rule_fn in self.rules.items():
            try:
                passed, reason = rule_fn(state, context)
                if not passed:
                    return False, f"INVARIANT_BREACH [{rule_name}]: {reason or 'Condition not satisfied'}"
            except Exception as exc:
                return False, f"INVARIANT_EVAL_ERROR [{rule_name}]: {str(exc)}"

        return True, None

    def enforce(
        self,
        state: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Enforces invariants, raising InvariantViolationError if any rule is breached."""
        passed, reason = self.validate(state, context)
        if not passed:
            raise InvariantViolationError(reason)
