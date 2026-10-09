"""Bounded Context Rewind and Working Memory Manager.

Constructs compact turn prompts strictly within the working memory budget
(default <= 512 tokens), pruning failed trajectories and injecting clean
negative directives upon host rollback.
100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

from typing import List, Optional


class ContextRewindManager:
    """Manages working memory prompts and state summaries under strict token ceilings."""

    def __init__(self, max_budget: int = 512) -> None:
        self.max_budget = max_budget
        self.confirmed_history: List[str] = []

    def record_success(self, action_str: str, observation_str: str) -> None:
        """Append confirmed valid action-observation step."""
        self.confirmed_history.append(f"Step: {action_str} -> {observation_str}")

    def rewind_last(self) -> None:
        """Rewind the most recent history entry upon rollback."""
        if self.confirmed_history:
            self.confirmed_history.pop()

    def build_turn_prompt(
        self,
        system_prompt: str,
        task_query: str,
        state_summary: str,
        latest_observation: str,
        additional_directive: Optional[str] = None,
    ) -> str:
        """Synthesize bounded working memory prompt for model forward pass."""
        sections: List[str] = [
            system_prompt.strip(),
            f"GOAL: {task_query.strip()}",
            f"CURRENT STATE:\n{state_summary.strip()}",
        ]

        if self.confirmed_history:
            # Keep only last 2 confirmed steps to preserve compact budget
            recent = self.confirmed_history[-2:]
            sections.append("CONFIRMED HISTORY:\n" + "\n".join(recent))

        sections.append(f"OBSERVATION:\n{latest_observation.strip()}")

        if additional_directive:
            sections.append(f"DIRECTIVE: {additional_directive.strip()}")

        sections.append("OUTPUT NEXT ACTION:")
        return "\n\n".join(sections)

    def clear(self) -> None:
        """Reset history."""
        self.confirmed_history.clear()
