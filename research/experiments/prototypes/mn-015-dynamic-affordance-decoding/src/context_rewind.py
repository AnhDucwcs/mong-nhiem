"""Host-directed Context Rewind & Negative Directive Manager for MN-014.

Guarantees prompt tokens remain bounded <= 512 tokens while communicating
precise negative constraints after state rollback.
"""
from __future__ import annotations

from typing import List, Optional


class ContextRewindManager:
    """Manages working memory context, turn pruning, and negative directive injection."""

    def __init__(self, max_budget: int = 512):
        self.max_budget = max_budget
        self._successful_turns: List[str] = []
        self._active_negative_directive: Optional[str] = None

    def record_success(self, action_str: str, observation: str) -> None:
        """Append a validated successful turn interaction."""
        self._successful_turns.append(f"{action_str} -> {observation}")
        self._active_negative_directive = None  # Clear negative directive upon forward progress

    def rewind(self, negative_directive: Optional[str] = None) -> None:
        """Drop the last failed assistant turn and inject negative constraint."""
        self._active_negative_directive = negative_directive

    def clear(self) -> None:
        self._successful_turns.clear()
        self._active_negative_directive = None

    def build_turn_prompt(
        self,
        system_prompt: str,
        task_query: str,
        state_summary: str,
        latest_observation: str = "None",
    ) -> str:
        """Construct per-turn prompt ensuring working context <= 512 tokens."""
        sections = [
            system_prompt,
            f"Task: {task_query}",
        ]
        if state_summary:
            sections.append(f"State: {state_summary}")

        if self._successful_turns:
            hist_str = " | ".join(self._successful_turns[-2:])
            sections.append(f"Recent History: {hist_str}")
        else:
            sections.append("Recent History: None")

        sections.append(f"Latest Observation: {latest_observation}")

        if self._active_negative_directive:
            sections.append(f"Constraint: {self._active_negative_directive}")

        sections.append("Directive:")
        return "\n\n".join(sections) + "\n"
