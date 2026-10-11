"""Isolated Counterfactual Sandbox for Stage 3.

Evaluates hypothetical candidate branches without mutating primary microworld state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from causal_synthesis_engine import CausalRule, CausalSynthesisEngine


@dataclass
class SandboxEvaluation:
    action: str
    is_viable: bool
    breach_reason: Optional[str] = None
    post_properties: Dict[str, Dict[str, Any]] = None
    triggered_rule: Optional[CausalRule] = None


class CounterfactualSandbox:
    """Non-destructive projection sandbox evaluating hypothetical candidate branches."""

    def __init__(self, causal_engine: CausalSynthesisEngine):
        self.causal_engine = causal_engine

    def evaluate_hypothetical_action(self, world_engine: Any, action_str: str) -> SandboxEvaluation:
        """Run hypothetical candidate branch in sandbox and check causal & physical viability."""
        # 1. Proactive causal rule check on pre-state
        rule = self.causal_engine.evaluate_action_causal_risk(action_str, world_engine.entities)
        if rule:
            return SandboxEvaluation(
                action=action_str,
                is_viable=False,
                breach_reason=f"CAUSAL_TRAP_ANTICIPATED: {rule.trap_consequence}",
                post_properties={eid: e.properties for eid, e in world_engine.entities.items()},
                triggered_rule=rule,
            )

        # 2. Non-destructive physical simulator step
        ok, err_msg, post_props = world_engine.simulate_counterfactual_step(action_str)
        if not ok:
            return SandboxEvaluation(
                action=action_str,
                is_viable=False,
                breach_reason=err_msg or "SIMULATION_INVARIANT_BREACH",
                post_properties=post_props,
                triggered_rule=None,
            )

        return SandboxEvaluation(
            action=action_str,
            is_viable=True,
            breach_reason=None,
            post_properties=post_props,
            triggered_rule=None,
        )
