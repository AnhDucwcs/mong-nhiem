"""Dynamic GBNF Affordance Compiler for Hierarchical Phase Gates.

Dynamically compiles Context-Free GBNF Grammars parameterizing allowed actions
strictly to the active sub-goal G_k, preventing Horizon Jumping and Goal Divergence
at the engine logit level.
"""
from __future__ import annotations

from typing import List, Optional, Set

from hierarchical_planner import SubGoal


class DynamicAffordanceCompiler:
    """Compiles GBNF grammar definitions enforcing active sub-goal affordances."""

    @staticmethod
    def compile_grammar(
        allowed_actions: List[str],
        known_entity_ids: List[str],
        allow_resolve: bool = False,
        allow_recall: bool = True,
    ) -> str:
        """Compile a strict GBNF grammar for the current turn.
        
        Args:
            allowed_actions: List of action templates (e.g. ['lock_resource res_1', 'renew_lease res_1']).
            known_entity_ids: List of entity IDs valid for ACTION: RECALL.
            allow_resolve: If True, affords ACTION: RESOLVE.
            allow_recall: If True, affords ACTION: RECALL.
            
        Returns:
            Valid GBNF grammar string.
        """
        branches: List[str] = []

        # Action dispatch branches
        for act in sorted(set(allowed_actions)):
            # Escape quotes
            safe_act = act.replace('"', '\\"')
            branches.append(f'"ACTION: DISPATCH {safe_act}"')

        # Recall branches
        if allow_recall and known_entity_ids:
            for eid in sorted(set(known_entity_ids)):
                safe_eid = eid.replace('"', '\\"')
                branches.append(f'"ACTION: RECALL {safe_eid}"')

        # Resolve branch
        if allow_resolve:
            branches.append('"ACTION: RESOLVE COMPLETE"')

        if not branches:
            branches.append('"ACTION: WAIT"')

        alternatives = " | ".join(branches)
        
        grammar = (
            f"root ::= action [\\n]?\n"
            f"action ::= {alternatives}\n"
        )
        return grammar

    @staticmethod
    def compile_for_subgoal(
        subgoal: Optional[SubGoal],
        known_entity_ids: List[str],
        all_completed: bool = False,
    ) -> str:
        """Convenience method to compile GBNF strictly for an active sub-goal."""
        if all_completed:
            return DynamicAffordanceCompiler.compile_grammar(
                allowed_actions=[],
                known_entity_ids=known_entity_ids,
                allow_resolve=True,
                allow_recall=False,
            )

        if subgoal is None:
            return DynamicAffordanceCompiler.compile_grammar(
                allowed_actions=["inspect_environment"],
                known_entity_ids=known_entity_ids,
                allow_resolve=False,
                allow_recall=True,
            )

        return DynamicAffordanceCompiler.compile_grammar(
            allowed_actions=subgoal.allowed_actions,
            known_entity_ids=known_entity_ids,
            allow_resolve=False,
            allow_recall=True,
        )

    @staticmethod
    def compile_global_grammar(
        all_actions: List[str],
        known_entity_ids: List[str],
        allow_resolve: bool = True,
    ) -> str:
        """Compile unconstrained global grammar for Arm 1 and Arm 2 baselines."""
        return DynamicAffordanceCompiler.compile_grammar(
            allowed_actions=all_actions,
            known_entity_ids=known_entity_ids,
            allow_resolve=allow_resolve,
            allow_recall=True,
        )
