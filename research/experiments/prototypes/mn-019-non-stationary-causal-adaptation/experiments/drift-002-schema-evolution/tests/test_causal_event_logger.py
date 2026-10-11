"""Unit tests for Causal Event Logger (Stage 3 Forward-Compatibility)."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from causal_event_logger import CausalEvent, CausalEventLog


def test_record_causal_event():
    logger = CausalEventLog()
    ev1 = logger.record_event(
        tick=1,
        event_type="EMERGE",
        entity_id="aux_cooler",
        pre_state={},
        post_state={"cooling_kw": 30.0},
    )
    assert ev1.event_id == "CEVT-0001-0001"
    assert ev1.event_type == "EMERGE"
    assert len(ev1.event_hash) == 64
    assert len(logger.events) == 1


def test_causal_dag_hash_chaining():
    logger = CausalEventLog()
    ev1 = logger.record_event(
        tick=1,
        event_type="EMERGE",
        entity_id="aux_cooler",
        pre_state={},
        post_state={"cooling_kw": 30.0},
    )
    ev2 = logger.record_event(
        tick=2,
        event_type="ACTION",
        entity_id="aux_cooler",
        pre_state={"cooling_kw": 30.0},
        post_state={"cooling_kw": 30.0, "status": "active"},
        causal_parents=[ev1.event_id],
    )
    assert ev2.causal_parents == [ev1.event_id]
    assert ev2.event_hash != ev1.event_hash

    # Trace causal chain
    chain = logger.get_causal_chain(ev2.event_id)
    assert len(chain) == 2
    assert chain[0].event_id == ev2.event_id
    assert chain[1].event_id == ev1.event_id


def test_export_causal_traces():
    logger = CausalEventLog()
    logger.record_event(tick=1, event_type="EMERGE", entity_id="feeder", pre_state={}, post_state={"cap": 50})
    traces = logger.export_causal_traces()
    assert len(traces) == 1
    assert traces[0]["entity_id"] == "feeder"
    assert "event_hash" in traces[0]
