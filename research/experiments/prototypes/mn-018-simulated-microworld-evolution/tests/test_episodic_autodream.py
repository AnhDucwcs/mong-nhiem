"""Unit tests for EpisodicLog, cryptographic provenance, and AutoDreamEngine."""
import pytest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from autodream_engine import AutoDreamEngine
from episodic_memory import EpisodicLog
from microworld_engine import MicroworldEngine, WorldEntity


def test_episodic_log_cryptographic_chain():
    log = EpisodicLog()
    assert log.last_hash == "GENESIS_00000000"

    e1 = log.append(tick=1, entity_id="ent_1", action_name="OPEN", status="SUCCESS", details={"val": 10})
    assert e1.prev_hash == "GENESIS_00000000"
    assert len(e1.event_hash) == 16

    e2 = log.append(tick=2, entity_id="ent_2", action_name="CLOSE", status="SUCCESS", details={"val": 20})
    assert e2.prev_hash == e1.event_hash
    assert len(e2.event_hash) == 16


def test_autodream_trigger_and_consolidation():
    engine = MicroworldEngine(domain="orbital_station")
    for i in range(5):
        engine.register_entity(WorldEntity(f"node_{i}", "sensor", properties={"temp": 20 + i}))

    log = EpisodicLog()
    dream = AutoDreamEngine(event_threshold=15, token_threshold=2000)

    # Append 14 events with realistic telemetry details -> should not trigger
    for i in range(14):
        log.append(
            tick=i+1,
            entity_id=f"node_{i % 5}",
            action_name="TELEMETRY_LOG",
            status="SUCCESS",
            details={
                "sensor_reading_mrem": 25.4 + i,
                "subsystem_bus_voltage": 28.2,
                "telemetry_stream_quality": "NOMINAL_HEALTH_OK",
                "calibration_epoch": 1728550000,
            },
        )

    assert not dream.should_trigger(log)
    did_run, count = dream.consolidate(log, engine)
    assert not did_run
    assert count == 0

    # Append 1 more event -> reaches 15, should trigger
    log.append(
        tick=15,
        entity_id="node_0",
        action_name="ALERT_TELEMETRY",
        status="SUCCESS",
        details={
            "sensor_reading_mrem": 39.4,
            "subsystem_bus_voltage": 28.2,
            "telemetry_stream_quality": "WARN_THRESHOLD",
            "calibration_epoch": 1728550000,
        },
    )
    assert dream.should_trigger(log)

    did_run, count = dream.consolidate(log, engine)
    assert did_run
    assert count == 15
    assert dream.stats.total_cycles == 1
    assert dream.stats.total_events_consolidated == 15
    # High compression ratio >= 70%
    assert dream.stats.compression_ratio >= 0.70

    # Verify zero contradictions: only 1 declarative card per entity
    assert len(dream.declarative_cards) <= 5
    decl_text = dream.render_declarative_context()
    assert "[CONSOLIDATED DECLARATIVE MEMORY]" in decl_text
    for i in range(5):
        assert f"node_{i}" in decl_text

    # After consolidation, unconsolidated events should be 0
    assert len(log.get_unconsolidated_events()) == 0
    assert not dream.should_trigger(log)
