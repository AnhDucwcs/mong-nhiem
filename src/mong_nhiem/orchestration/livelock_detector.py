"""Multi-Agent Livelock & Starvation Detector.

Tracks directed wait-for dependency cycles across multiple agents issuing STANDBY commands.
Breaks circular livelocks by triggering priority preemption when cycle threshold is reached.
Eliminates Priority Inversion and Starvation via an Urgency-Cost + Aging Wait-Ticks scoring function.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LivelockDetector:
    """Detects and resolves circular wait-for deadlocks in multi-agent environments."""

    cycle_threshold_ticks: int = 3
    urgency_weight: float = 100.0
    aging_weight: float = 1.0
    _wait_graph: dict[str, str] = field(default_factory=dict)
    _cycle_history: dict[tuple[str, str], int] = field(default_factory=dict)
    _wait_ticks: dict[str, int] = field(default_factory=dict)
    _scram_margins: dict[str, float] = field(default_factory=dict)
    _last_resolution: str | None = None
    _elected_agent: str | None = None

    def update_agent_telemetry(self, agent_id: str, margin_to_scram: float) -> None:
        """Updates the physical proximity to safety trip/scram threshold for an agent."""
        self._scram_margins[agent_id] = max(1e-6, float(margin_to_scram))

    def record_agent_standby(self, agent_id: str, waiting_for: str) -> bool:
        """Records that an agent entered STANDBY waiting for another agent.

        Returns True if a persistent cyclic deadlock is detected, False otherwise.
        """
        self._wait_graph[agent_id] = waiting_for
        self._wait_ticks[agent_id] = self._wait_ticks.get(agent_id, 0) + 1

        # Check for circular wait
        if self._has_cycle(agent_id):
            cycle_key = tuple(sorted([agent_id, waiting_for]))
            current_ticks = self._cycle_history.get(cycle_key, 0) + 1
            self._cycle_history[cycle_key] = current_ticks

            if current_ticks >= self.cycle_threshold_ticks:
                self._last_resolution = "FORCE_DECOUPLED_DISPATCH"
                self._elected_agent = self.resolve_priority_agent([agent_id, waiting_for])
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

    def resolve_priority_agent(self, candidates: list[str] | None = None) -> str:
        """Selects the agent to dispatch using the Urgency-Cost + Aging Wait-Ticks function.

        Score(A) = w_urgency * (1.0 / margin_to_scram) + alpha_aging * wait_ticks
        Prevents Starvation (Priority Inversion) while honoring physical safety margin.
        """
        pool = candidates if candidates else list(self._wait_graph.keys())
        if not pool:
            return ""

        best_agent = pool[0]
        best_score = -1.0

        for agent in pool:
            margin = self._scram_margins.get(agent, 10.0)
            wait_t = self._wait_ticks.get(agent, 0)
            urgency_score = self.urgency_weight / margin
            aging_score = self.aging_weight * wait_t
            total_score = urgency_score + aging_score

            if total_score > best_score:
                best_score = total_score
                best_agent = agent

        # Reset wait ticks for the winning agent to prevent monopolization
        self._wait_ticks[best_agent] = 0
        self._elected_agent = best_agent
        return best_agent

    def get_preemption_resolution(self) -> str:
        """Returns the breaking action resolution to overcome the circular livelock."""
        return self._last_resolution or "NOMINAL_DISPATCH"

    def get_elected_agent(self) -> str | None:
        """Returns the specific agent chosen by priority arbitration to execute."""
        return self._elected_agent

    def reset(self) -> None:
        """Clears active wait graph, cycle counts, and priority tracking."""
        self._wait_graph.clear()
        self._cycle_history.clear()
        self._wait_ticks.clear()
        self._scram_margins.clear()
        self._last_resolution = None
        self._elected_agent = None
