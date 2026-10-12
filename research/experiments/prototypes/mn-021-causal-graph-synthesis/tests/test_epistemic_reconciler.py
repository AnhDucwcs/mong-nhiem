"""Unit tests for Epistemic Reconciler Engine (MN-021)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.causal_dag import CausalEventDAG
from src.epistemic_reconciler import EpistemicObservation, EpistemicReconciler


def test_nominal_match():
    reconciler = EpistemicReconciler()
    dag = CausalEventDAG()

    obs1 = EpistemicObservation("o1", "agent_alpha", "power_grid", 2, {"voltage": 48})
    obs2 = EpistemicObservation("o2", "agent_beta", "power_grid", 4, {"voltage": 48})

    res = reconciler.reconcile_observations(obs1, obs2, dag)
    assert res.status == "NOMINAL_MATCH"


def test_temporal_evolution():
    reconciler = EpistemicReconciler()
    dag = CausalEventDAG()

    obs1 = EpistemicObservation("o1", "agent_alpha", "power_grid", 2, {"voltage": 48})
    # Intermediate event in DAG at t=3
    dag.add_event(
        actor="agent_alpha",
        action_name="BOOST_VOLTAGE",
        target_entity="power_grid",
        state_delta={"voltage": 52},
        tick=3,
    )
    obs2 = EpistemicObservation("o2", "agent_beta", "power_grid", 5, {"voltage": 52})

    res = reconciler.reconcile_observations(obs1, obs2, dag)
    assert res.status == "TEMPORAL_EVOLUTION"
    assert res.intervening_event is not None
    assert "evolved" in res.delta_notice_for_earlier


def test_contested_anomaly():
    reconciler = EpistemicReconciler()
    dag = CausalEventDAG()

    obs1 = EpistemicObservation("o1", "agent_alpha", "power_grid", 2, {"voltage": 48})
    # No intermediate event in DAG! (Exogenous anomaly / shock)
    obs2 = EpistemicObservation("o2", "agent_beta", "power_grid", 5, {"voltage": 32})

    res = reconciler.reconcile_observations(obs1, obs2, dag)
    assert res.status == "CONTESTED_ANOMALY"
    assert reconciler.is_entity_contested("power_grid")
    assert "ANOMALY" in res.delta_notice_for_earlier
