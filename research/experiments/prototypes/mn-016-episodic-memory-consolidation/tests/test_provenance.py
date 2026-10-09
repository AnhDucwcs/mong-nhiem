"""Unit tests for Event Provenance and Episodic Stream."""

import sys
import tempfile
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from provenance import EpisodicEvent, EpisodicStream, EventProvenance


def test_provenance_hashing_determinism() -> None:
    payload1 = {"balance": 100, "user": "alice"}
    payload2 = {"user": "alice", "balance": 100}  # Key order different
    hash1 = EventProvenance.compute_hash(payload1)
    hash2 = EventProvenance.compute_hash(payload2)
    assert hash1 == hash2
    assert len(hash1) == 16


def test_episodic_stream_in_memory_and_queries() -> None:
    stream = EpisodicStream()
    e1 = EpisodicEvent(
        event_id="e1",
        tick=1,
        entity_id="vault_a",
        action_name="create",
        success=True,
        state_delta={"balance": 500},
    )
    e2 = EpisodicEvent(
        event_id="e2",
        tick=2,
        entity_id="vault_b",
        action_name="create",
        success=True,
        state_delta={"balance": 200},
    )
    e3 = EpisodicEvent(
        event_id="e3",
        tick=3,
        entity_id="vault_a",
        action_name="read",
        success=True,
        state_delta={},
    )
    stream.append(e1)
    stream.append(e2)
    stream.append(e3)

    assert len(stream) == 3
    assert len(stream.get_events_since_tick(1)) == 2
    assert len(stream.get_events_for_entity("vault_a")) == 2
    assert stream.count_mutations_since_tick(0) == 2  # e1 and e2 mutate, e3 is read
    assert stream.count_mutations_since_tick(1) == 1  # e2


def test_episodic_stream_disk_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "events.jsonl"
        stream1 = EpisodicStream(log_path)
        prov = EventProvenance(
            event_id="e1",
            tick=10,
            source_channel="ledger",
            raw_payload_hash="abcd1234",
        )
        e1 = EpisodicEvent(
            event_id="e1",
            tick=10,
            entity_id="vault_x",
            action_name="deposit",
            success=True,
            state_delta={"balance": 1000},
            provenance=prov,
        )
        stream1.append(e1)

        # Reload in a fresh stream object
        stream2 = EpisodicStream(log_path)
        assert len(stream2) == 1
        loaded = stream2.get_all_events()[0]
        assert loaded.entity_id == "vault_x"
        assert loaded.state_delta == {"balance": 1000}
        assert loaded.provenance is not None
        assert loaded.provenance.raw_payload_hash == "abcd1234"
