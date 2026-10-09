"""Autonomous AutoDream Trigger with Context Pressure Protection.

Autonomous AutoDream activation architecture for Mộng Nhiễm:
- Replaces wall-clock time with discrete world ticks.
- Replaces human session counts with authoritative state mutation flux.
- Adds an Emergency Context Budget Pressure Interceptor (threshold >= 400 tokens)
  that bypasses cadence gates to guarantee zero context overflow.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

try:
    from .consolidation_lock import ConsolidationLock, ConsolidationState
except ImportError:
    from consolidation_lock import ConsolidationLock, ConsolidationState


class TriggerType(str, Enum):
    """Reason why memory consolidation was triggered."""

    NONE = "none"
    CADENCE_GATES = "cadence_gates"
    EMERGENCY_PRESSURE = "emergency_pressure"


@dataclass(frozen=True)
class TriggerConfig:
    """Configurable thresholds for AutoDream activation."""

    min_ticks_interval: int = 25
    min_mutations_count: int = 10
    context_pressure_token_threshold: int = 400  # 78.1% of 512-token ceiling


@dataclass(frozen=True)
class TriggerResult:
    """Evaluation outcome of the trigger check."""

    should_consolidate: bool
    trigger_type: TriggerType
    reason: str


class AutonomousAutoDreamTrigger:
    """Evaluates whether the background consolidation pass should fire."""

    def __init__(
        self,
        memory_dir: Path,
        config: TriggerConfig | None = None,
    ) -> None:
        self.config = config or TriggerConfig()
        self.lock = ConsolidationLock(memory_dir)

    def evaluate(
        self,
        state: ConsolidationState,
        current_tick: int,
        unconsolidated_mutations: int,
        current_working_tokens: int,
    ) -> TriggerResult:
        """Evaluate cheapest-first gates plus emergency context pressure interceptor."""

        # ---------------------------------------------------------------------
        # Interceptor: Emergency Context Budget Pressure
        # ---------------------------------------------------------------------
        if current_working_tokens >= self.config.context_pressure_token_threshold:
            if self.lock.try_acquire():
                return TriggerResult(
                    should_consolidate=True,
                    trigger_type=TriggerType.EMERGENCY_PRESSURE,
                    reason=(
                        f"Context budget saturated ({current_working_tokens} >= "
                        f"{self.config.context_pressure_token_threshold} tokens); "
                        "emergency consolidation lock acquired"
                    ),
                )
            return TriggerResult(
                should_consolidate=False,
                trigger_type=TriggerType.NONE,
                reason="Context pressure triggered but consolidation lock is busy",
            )

        # ---------------------------------------------------------------------
        # Cadence Gate 1: Tick / Horizon Gate (Cheapest - arithmetic check)
        # ---------------------------------------------------------------------
        ticks_elapsed = current_tick - state.last_consolidated_tick
        if ticks_elapsed < self.config.min_ticks_interval:
            return TriggerResult(
                should_consolidate=False,
                trigger_type=TriggerType.NONE,
                reason=(
                    f"Tick gate not satisfied ({ticks_elapsed} < "
                    f"{self.config.min_ticks_interval} ticks)"
                ),
            )

        # ---------------------------------------------------------------------
        # Cadence Gate 2: Mutation Flux Gate (Event count check)
        # ---------------------------------------------------------------------
        if unconsolidated_mutations < self.config.min_mutations_count:
            return TriggerResult(
                should_consolidate=False,
                trigger_type=TriggerType.NONE,
                reason=(
                    f"Mutation gate not satisfied ({unconsolidated_mutations} < "
                    f"{self.config.min_mutations_count} mutations)"
                ),
            )

        # ---------------------------------------------------------------------
        # Cadence Gate 3: Lock Gate (Acquire atomic mutex)
        # ---------------------------------------------------------------------
        if not self.lock.try_acquire():
            return TriggerResult(
                should_consolidate=False,
                trigger_type=TriggerType.NONE,
                reason="Lock gate failed: another process is consolidating",
            )

        return TriggerResult(
            should_consolidate=True,
            trigger_type=TriggerType.CADENCE_GATES,
            reason=(
                f"Cadence gates satisfied ({ticks_elapsed} ticks, "
                f"{unconsolidated_mutations} mutations); lock acquired"
            ),
        )

    def release_lock(self) -> None:
        """Release the consolidation lock."""
        self.lock.release()
