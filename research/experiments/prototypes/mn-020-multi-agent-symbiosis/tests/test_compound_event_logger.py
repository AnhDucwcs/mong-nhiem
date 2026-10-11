"""Unit tests for Compound Event Logger."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from compound_event_logger import CompoundEventLogger


def test_event_logging_and_hash_integrity():
    logger = CompoundEventLogger()

    # Record event 1 by agent_1
    e1 = logger.record_event(
        tick=1,
        event_type="ACTION",
        actor_id="agent_1",
        entity_id="wind_turbine",
        pre_state={"pitch_deg": 10.0},
        post_state={"pitch_deg": 30.0},
        triggering_action="ACTION: DISPATCH regulate_wind_pitch 30.0",
    )
    assert len(e1.event_hash) == 64
    assert len(e1.causal_parent_hashes) == 0

    # Record event 2 on same entity by agent_2
    e2 = logger.record_event(
        tick=2,
        event_type="ACTION",
        actor_id="agent_2",
        entity_id="wind_turbine",
        pre_state={"pitch_deg": 30.0},
        post_state={"pitch_deg": 45.0},
        triggering_action="ACTION: DISPATCH regulate_wind_pitch 45.0",
    )
    assert e1.event_hash in e2.causal_parent_hashes
    assert logger.verify_dag_integrity() is True
