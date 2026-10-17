"""Cognitive Belief Conflict Reconciliation Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class CausalBeliefState:
    agent_id: str
    inferred_edges: Set[Tuple[str, str, str]] = field(default_factory=set)  # (source, relation, target)
    unexpressed_assumptions: Dict[str, Any] = field(default_factory=dict)  # latent assumptions (Trap 2.3)
    proposed_action: Optional[str] = None


class ConflictEngine:
    """Calculates epistemic divergence and coordinates dialectic reconciliation."""

    @staticmethod
    def calculate_divergence(state_a: CausalBeliefState, state_b: CausalBeliefState) -> int:
        """Computes symmetric difference distance: d(G_A, G_B) = |E_A ^ E_B|."""
        sym_diff = state_a.inferred_edges.symmetric_difference(state_b.inferred_edges)
        return len(sym_diff)

    @classmethod
    def reconcile_beliefs(
        cls,
        state_a: CausalBeliefState,
        state_b: CausalBeliefState,
        joint_telemetry: Optional[Dict[str, Any]] = None,
        turn_count: int = 1,
    ) -> Tuple[bool, int, Optional[str]]:
        """Coordinates a dialectic step between Agent A and Agent B.
        
        Returns:
            (is_converged, current_divergence, tie_break_message)
        """
        initial_div = cls.calculate_divergence(state_a, state_b)
        if initial_div == 0:
            return True, 0, None

        # Check for latent unexpressed assumption conflict (Trap 2.3)
        common_keys = set(state_a.unexpressed_assumptions.keys()) & set(state_b.unexpressed_assumptions.keys())
        for k in common_keys:
            if state_a.unexpressed_assumptions[k] != state_b.unexpressed_assumptions[k]:
                if joint_telemetry is None:
                    # Trapped: split-brain assumption persists
                    return False, initial_div, f"UNEXPRESSED_ASSUMPTION_DEADLOCK: Conflict on hidden assumption '{k}'"

        # If joint telemetry (CROSS_INSPECT) was executed, converge beliefs
        if joint_telemetry:
            # Objective ground truth resolves conflicting edges
            ground_truth_edges = set()
            for key, val in joint_telemetry.items():
                ground_truth_edges.add((key, "EQUALS", str(val)))
            state_a.inferred_edges = set(ground_truth_edges)
            state_b.inferred_edges = set(ground_truth_edges)
            return True, 0, "CONVERGED_VIA_CROSS_INSPECT"

        # If deadlock persists past threshold (turn >= 3), Host initiates tie-break
        if turn_count >= 3:
            return False, initial_div, "HOST_TIE_BREAK_REQUIRED"

        return False, initial_div, None

    @staticmethod
    def host_arbitrate_tie_break(
        world_state: Dict[str, Any],
        state_a: CausalBeliefState,
        state_b: CausalBeliefState,
    ) -> Tuple[str, str]:
        """Host deterministically breaks conflict tie by evaluating physical invariants.
        
        Returns:
            (winning_agent_id, reason)
        """
        # Physical reality test: If physical parameter exceeds safe limit, safety view wins
        core_temp = world_state.get("core_temp", world_state.get("sensor_core_temp", 250.0))
        freq = world_state.get("frequency", world_state.get("sensor_substation_freq", 50.0))
        co2 = world_state.get("co2_ppm", world_state.get("sensor_co2_scrubber", 400.0))

        if core_temp > 300.0 or abs(freq - 50.0) > 1.5 or co2 > 1000.0:
            # Physical safety invariant violated: Safety / Shutdown hypothesis wins
            return state_a.agent_id, "HOST_ARBITRATION: Physical invariant anomaly confirmed. Enforcing safety isolation."
        
        return state_b.agent_id, "HOST_ARBITRATION: Telemetry within nominal bounds. Enforcing load balancing."
