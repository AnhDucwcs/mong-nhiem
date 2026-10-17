"""Unit tests for EpistemicReconciler and temporal discrepancy arbitration."""

from mong_nhiem.knowledge.causal_dag import CausalEventDAG
from mong_nhiem.knowledge.epistemic import EpistemicObservation, EpistemicReconciler


def test_epistemic_reconciliation_temporal_evolution():
    dag = CausalEventDAG()
    # Event occurs at tick 3 modifying sub_1 status
    evt = dag.add_event(
        actor="agent_1",
        action_name="ACT_STABILIZE",
        target_entity="sub_1",
        state_delta={"status": "STABILIZED"},
        tick=3,
    )

    # Agent A observed sub_1 at tick 2 as UNSTABLE
    obs_a = EpistemicObservation(
        observation_id="obs_a",
        observer="agent_2",
        target_entity="sub_1",
        observed_tick=2,
        observed_attributes={"status": "UNSTABLE"},
    )

    # Agent B observed sub_1 at tick 4 as STABILIZED
    obs_b = EpistemicObservation(
        observation_id="obs_b",
        observer="agent_1",
        target_entity="sub_1",
        observed_tick=4,
        observed_attributes={"status": "STABILIZED"},
    )

    reconciler = EpistemicReconciler()
    res = reconciler.reconcile_observations(obs_a, obs_b, dag)

    assert res.status == "TEMPORAL_EVOLUTION"
    assert res.intervening_event is not None
    assert res.intervening_event.event_id == evt.event_id
    assert "evolved" in res.delta_notice_for_earlier
    assert reconciler.is_entity_contested("sub_1") is False


def test_epistemic_reconciliation_contested_anomaly():
    dag = CausalEventDAG()
    # No event in DAG explains why status is different
    obs_a = EpistemicObservation(
        observation_id="obs_a",
        observer="agent_2",
        target_entity="sub_1",
        observed_tick=2,
        observed_attributes={"status": "UNSTABLE"},
    )
    obs_b = EpistemicObservation(
        observation_id="obs_b",
        observer="agent_3",
        target_entity="sub_1",
        observed_tick=4,
        observed_attributes={"status": "DESTROYED"},
    )

    reconciler = EpistemicReconciler()
    res = reconciler.reconcile_observations(obs_a, obs_b, dag)

    assert res.status == "CONTESTED_ANOMALY"
    assert reconciler.is_entity_contested("sub_1") is True
    assert "CROSS_INSPECT" in res.delta_notice_for_earlier
