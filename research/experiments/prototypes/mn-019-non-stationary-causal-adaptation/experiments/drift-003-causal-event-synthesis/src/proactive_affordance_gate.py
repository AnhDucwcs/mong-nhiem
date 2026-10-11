"""Proactive Affordance Gating Engine for Stage 3.

Filters out candidate actions that trigger latent causal traps or invariant breaches.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from counterfactual_sandbox import CounterfactualSandbox


class ProactiveAffordanceGate:
    """Proactively evaluates candidate actions and prunes latent traps from GBNF grammar."""

    def __init__(self, sandbox: CounterfactualSandbox):
        self.sandbox = sandbox
        self.proactive_bypasses_count: int = 0
        self.intercepted_traps_history: List[Dict[str, Any]] = []

    def filter_viable_actions(
        self,
        world_engine: Any,
        candidate_actions: List[str],
    ) -> Tuple[List[str], Dict[str, str], List[str]]:
        """Evaluates candidate actions, returning (viable_actions, pruned_map, causal_cards)."""
        viable: List[str] = []
        pruned: Dict[str, str] = {}
        cards: List[str] = []

        for act in candidate_actions:
            eval_res = self.sandbox.evaluate_hypothetical_action(world_engine, act)
            if eval_res.is_viable:
                viable.append(act)
            else:
                pruned[act] = eval_res.breach_reason or "UNVIABLE"
                self.proactive_bypasses_count += 1
                self.intercepted_traps_history.append({
                    "action": act,
                    "reason": eval_res.breach_reason,
                    "rule_id": eval_res.triggered_rule.rule_id if eval_res.triggered_rule else None,
                })
                if eval_res.triggered_rule:
                    cards.append(eval_res.triggered_rule.to_card_string())

        return viable, pruned, cards
