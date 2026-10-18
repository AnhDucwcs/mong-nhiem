"""Goal-Conditioned Top-K Affordance Ranker.

Enforces O(1) constant-space working memory (<= 200 tokens) by ranking candidate
affordances, pulling prerequisite actions via dependency boosts, and masking deceptive decoy actions.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple


class GoalConditionedAffordanceRanker:
    """Ranks and bounds affordances to a constant Top-K working set."""

    def __init__(
        self,
        top_k: int = 4,
        dependency_boost: float = 25.0,
        default_score: float = 10.0,
    ) -> None:
        self.top_k = top_k
        self.dependency_boost = dependency_boost
        self.default_score = default_score

    def rank_affordances(
        self,
        candidates: List[str],
        unfulfilled_preconditions: Optional[Set[str]] = None,
        enabling_map: Optional[Dict[str, str]] = None,
        confirmed_decoys: Optional[Set[str]] = None,
        priority_verbs: Optional[List[str]] = None,
    ) -> List[str]:
        """Ranks candidate affordances and returns the Top-K subset.

        Args:
            candidates: Full list of valid candidate actions.
            unfulfilled_preconditions: Set of prerequisite keys currently not satisfied.
            enabling_map: Mapping of enabling_action -> prerequisite_key satisfied by it.
            confirmed_decoys: Set of target entities identified as unrecoverable/decoys.
            priority_verbs: List of verb prefixes to prioritize in order.

        Returns:
            Deterministic list of at most top_k ranked actions.
        """
        if not candidates:
            return []

        unmet = unfulfilled_preconditions or set()
        enablers = enabling_map or {}
        decoys = confirmed_decoys or set()
        prio_verbs = priority_verbs or []

        scored_candidates: List[Tuple[float, str]] = []

        for cand in candidates:
            clean_cand = cand.replace("ACTION:", "").strip()
            score = self.default_score

            # 1. Dependency Pulling: Boost enabling actions for unfulfilled preconditions
            if clean_cand in enablers:
                target_precond = enablers[clean_cand]
                if target_precond in unmet:
                    score += self.dependency_boost

            # 2. Priority Verbs Boost
            for idx, verb in enumerate(prio_verbs):
                if clean_cand.startswith(verb):
                    # Higher rank for earlier verbs in priority list
                    score += max(5.0, 20.0 - (idx * 3.0))
                    break

            # 3. Decoy Masking: Demote actions targeting confirmed decoys
            for decoy in decoys:
                if decoy in clean_cand:
                    score -= 50.0
                    break

            # Use negative candidate string for deterministic lexicographic tie-breaking
            scored_candidates.append((score, clean_cand, cand))

        # Sort descending by score, ascending by clean action text
        scored_candidates.sort(key=lambda x: (x[0], -len(x[1]), x[1]), reverse=True)

        return [item[2] for item in scored_candidates[: self.top_k]]
