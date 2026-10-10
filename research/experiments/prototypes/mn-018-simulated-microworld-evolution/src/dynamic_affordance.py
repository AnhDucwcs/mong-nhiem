"""Dynamic GBNF Affordance Compiler for Hierarchical Phase Gates with Active Pruning.

Dynamically compiles Context-Free GBNF Grammars parameterizing allowed actions
strictly to the active sub-goal G_k, preventing Horizon Jumping and Goal Divergence
at the engine logit level, while pruning redundant RECALL affordances to eliminate loops.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set

from hierarchical_planner import SubGoal


class DynamicAffordanceCompiler:
    """Compiles GBNF grammar definitions enforcing active sub-goal affordances."""

    @staticmethod
    def compile_grammar(
        allowed_actions: List[str],
        known_entity_ids: List[str],
        allow_resolve: bool = False,
        allow_recall: bool = True,
        negative_actions: Optional[List[str]] = None,
    ) -> str:
        """Compile a strict GBNF grammar for the current turn.
        
        Args:
            allowed_actions: List of action templates (e.g. ['adjust_valve v1 20', 'divert_power grid 50']).
            known_entity_ids: List of entity IDs valid for ACTION: RECALL.
            allow_resolve: If True, affords ACTION: RESOLVE.
            allow_recall: If True, affords ACTION: RECALL.
            negative_actions: Optional list of actions banned by Memento/rollbacks.
            
        Returns:
            Valid GBNF grammar string.
        """
        branches: List[str] = []
        neg_set = set(negative_actions or [])

        # Action dispatch branches
        for act in sorted(set(allowed_actions)):
            if act in neg_set:
                continue
            safe_act = act.replace('"', '\\"')
            branches.append(f'"ACTION: DISPATCH {safe_act}"')

        # Recall branches (with active entity pruning)
        if allow_recall and known_entity_ids:
            for eid in sorted(set(known_entity_ids)):
                recall_act = f"RECALL {eid}"
                if recall_act in neg_set:
                    continue
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
        negative_actions: Optional[List[str]] = None,
        working_entity_versions: Optional[Dict[str, int]] = None,
        current_entity_versions: Optional[Dict[str, int]] = None,
    ) -> str:
        """Convenience method to compile GBNF strictly for an active sub-goal with RECALL pruning."""
        if all_completed:
            return DynamicAffordanceCompiler.compile_grammar(
                allowed_actions=[],
                known_entity_ids=[],
                allow_resolve=True,
                allow_recall=False,
                negative_actions=negative_actions,
            )

        if subgoal is None:
            return DynamicAffordanceCompiler.compile_grammar(
                allowed_actions=["inspect_environment"],
                known_entity_ids=known_entity_ids,
                allow_resolve=False,
                allow_recall=True,
                negative_actions=negative_actions,
            )

        # Host affordance pruning:
        # If an entity is already in working memory with its latest version, prune its RECALL affordance
        candidate_recalls = list(known_entity_ids)
        if working_entity_versions and current_entity_versions:
            pruned_recalls: List[str] = []
            for eid in candidate_recalls:
                w_ver = working_entity_versions.get(eid)
                c_ver = current_entity_versions.get(eid)
                # Keep RECALL only if unobserved (w_ver is None) or stale (w_ver < c_ver)
                if w_ver is None or (c_ver is not None and w_ver < c_ver):
                    pruned_recalls.append(eid)
            # If all sub-goal actions are available and some entities are fresh, use pruned list
            candidate_recalls = pruned_recalls

        return DynamicAffordanceCompiler.compile_grammar(
            allowed_actions=subgoal.allowed_actions,
            known_entity_ids=candidate_recalls,
            allow_resolve=False,
            allow_recall=True,
            negative_actions=negative_actions,
        )

    @staticmethod
    def compile_global_grammar(
        all_actions: List[str],
        known_entity_ids: List[str],
        allow_resolve: bool = True,
        negative_actions: Optional[List[str]] = None,
    ) -> str:
        """Compile unconstrained global grammar for Arm 1 and Arm 2 baselines."""
        return DynamicAffordanceCompiler.compile_grammar(
            allowed_actions=all_actions,
            known_entity_ids=known_entity_ids,
            allow_resolve=allow_resolve,
            allow_recall=True,
            negative_actions=negative_actions,
        )
