"""Multi-Agent Livelock & Starvation Detector.

Tracks directed wait-for dependency cycles across multiple agents issuing STANDBY commands.
Breaks circular livelocks by triggering priority preemption when cycle threshold is reached.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LivelockDetector:
    """Detects and resolves circular wait-for deadlocks in multi-agent environments."""

    cycle_threshold_ticks: int = 3
    _wait_graph: dict[str, str] = field(default_factory=dict)
    _cycle_history: dict[tuple[str, str], int] = field(default_factory=dict)
    _last_resolution: str | None = None

    def record_agent_standby(self, agent_id: str, waiting_for: str) -> bool:
        """Records that an agent entered STANDBY waiting for another agent.

        Returns True if a persistent cyclic deadlock is detected, False otherwise.
        """
        self._wait_graph[agent_id] = waiting_for

        # Check for circular wait
        if self._has_cycle(agent_id):
            cycle_key = tuple(sorted([agent_id, waiting_for]))
            current_ticks = self._cycle_history.get(cycle_key, 0) + 1
            self._cycle_history[cycle_key] = current_ticks

            if current_ticks >= self.cycle_threshold_ticks:
                self._last_resolution = "FORCE_DECOUPLED_DISPATCH"
                return True
        return False

    def _has_cycle(self, start_agent: str) -> bool:
        """Detects whether start_agent participates in a closed dependency cycle."""
        visited: set[str] = set()
        curr: str | None = start_agent

        while curr and curr not in visited:
            visited.add(curr)
            curr = self._wait_graph.get(curr)
            if curr == start_agent:
                return True
        return False

    def get_preemption_resolution(self) -> str:
        """Returns the breaking action resolution to overcome the circular livelock."""
        return self._last_resolution or "NOMINAL_DISPATCH"

    def reset(self) -> None:
        """Clears active wait graph and cycle counts."""
        self._wait_graph.clear()
        self._cycle_history.clear()
        self._last_resolution = None
