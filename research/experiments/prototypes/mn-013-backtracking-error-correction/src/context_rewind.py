"""Context Rewind Engine for MN-013.

Manages working prompt context under 4 experimental arms:
- Arm 1: Forward-only (no rewind, no negative directive)
- Arm 2: Naive history (appends error traces directly, unconstrained context growth)
- Arm 3: Context rewind only (pops failed turn tokens, no negative directive)
- Arm 4: Full MN-013 (Context rewind + 15-token negative directive + phase gating)
"""
from __future__ import annotations

from typing import List, Optional
from mong_nhiem.context import ContextPacker, sanitize_chat_tokens


class ContextRewindManager:
    def __init__(self, max_budget: int = 512):
        self.max_budget = max_budget
        self.packer = ContextPacker(max_budget=max_budget)
        self.history_records: List[str] = []
        self.active_negative_directive: Optional[str] = None

    def record_success(self, action_str: str, observation_str: str) -> None:
        """Record successful action and observation to history."""
        self.history_records.append(f"{action_str} -> {observation_str}")
        self.active_negative_directive = None

    def record_failure_arm2(self, action_str: str, error_reason: str) -> None:
        """Arm 2: Naive History Accumulation - appends error trace directly to context."""
        self.history_records.append(f"{action_str} -> ERROR: {error_reason}")

    def rewind_arm3(self) -> None:
        """Arm 3: Context Rewind Only - drops failed attempt, no negative directive."""
        self.active_negative_directive = None

    def rewind_arm4(self, negative_directive: str) -> None:
        """Arm 4: Full MN-013 - drops failed attempt, injects compact negative directive."""
        self.active_negative_directive = negative_directive

    def build_turn_prompt(
        self,
        system_prompt: str,
        task_query: str,
        state_summary: str,
        latest_observation: str,
        arm: int = 4,
    ) -> str:
        """Construct prompt and ensure it stays strictly within the 512-token budget."""
        safe_query = sanitize_chat_tokens(task_query)
        safe_state = sanitize_chat_tokens(state_summary)
        safe_obs = sanitize_chat_tokens(latest_observation)

        if arm == 2:
            # Arm 2 includes unpruned history directly, deliberately causing prompt inflation
            hist_str = "\n".join(self.history_records) if self.history_records else "None"
            return (
                f"{system_prompt}\n\n"
                f"Task: {safe_query}\n\n"
                f"State Summary: {safe_state}\n\n"
                f"Full Execution History:\n{hist_str}\n\n"
                f"Latest Observation:\n{safe_obs}\n\n"
                f"Directive: ACTION:"
            )

        chunks = []
        if safe_state:
            chunks.append(f"State Summary: {safe_state}")

        # Arms 1, 3, 4: bound history to last 2 actions
        recent = self.history_records[-2:] if self.history_records else ["None"]
        chunks.append(f"Recent History: {' | '.join(recent)}")

        if self.active_negative_directive and arm == 4:
            chunks.append(f"Constraint:\n{self.active_negative_directive}")

        if safe_obs:
            chunks.append(f"Latest Observation:\n{safe_obs}")

        packed_body = self.packer.pack(chunks, query=safe_query)

        return (
            f"{system_prompt}\n\n"
            f"=== WORKING MEMORY (L1) ===\n"
            f"{packed_body}\n\n"
            f"=== CURRENT TASK ===\n"
            f"{safe_query}\n\n"
            f"Directive: ACTION:"
        )
