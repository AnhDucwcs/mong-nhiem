"""Unit tests for ConflictEngine in Milestone MN-025."""

import sys
from pathlib import Path

# Add prototype root
prototype_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(prototype_root))

from src.conflict_engine import CausalBeliefState, ConflictEngine


def test_divergence_calculation():
    state_a = CausalBeliefState(agent_id="alpha")
    state_b = CausalBeliefState(agent_id="beta")

    state_a.inferred_edges.add(("sensor_temp", "CAUSES", "core_overheat"))
    state_b.inferred_edges.add(("sensor_temp", "IS_GLITCH", "nominal"))

    # Both edges are in symmetric difference
    div = ConflictEngine.calculate_divergence(state_a, state_b)
    assert div == 2

    # Converging edge
    state_b.inferred_edges = set(state_a.inferred_edges)
    assert ConflictEngine.calculate_divergence(state_a, state_b) == 0


def test_dialectic_reconciliation_via_cross_inspect():
    state_a = CausalBeliefState(agent_id="alpha")
    state_b = CausalBeliefState(agent_id="beta")
    state_a.inferred_edges.add(("temp", "LEVEL", "HIGH"))
    state_b.inferred_edges.add(("temp", "LEVEL", "NORMAL"))

    # Turn 1: Without joint telemetry, conflict remains
    converged, div, msg = ConflictEngine.reconcile_beliefs(state_a, state_b, joint_telemetry=None, turn_count=1)
    assert not converged
    assert div == 2

    # Turn 2: Joint telemetry grounds truth
    joint_data = {"temp": "HIGH", "core_status": "CRITICAL"}
    converged, div, msg = ConflictEngine.reconcile_beliefs(state_a, state_b, joint_telemetry=joint_data, turn_count=2)
    assert converged
    assert div == 0
    assert msg == "CONVERGED_VIA_CROSS_INSPECT"


def test_host_tie_break():
    state_a = CausalBeliefState(agent_id="safety_officer")
    state_b = CausalBeliefState(agent_id="load_balancer")

    # Invariant breach scenario (temp = 320 > 300)
    world_state = {"core_temp": 320.0}
    winner, reason = ConflictEngine.host_arbitrate_tie_break(world_state, state_a, state_b)
    assert winner == "safety_officer"
    assert "safety isolation" in reason
