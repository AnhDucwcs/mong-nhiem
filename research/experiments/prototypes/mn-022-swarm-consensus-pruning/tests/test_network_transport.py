"""Unit tests for NetworkTransport layer."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pytest
from src.network_transport import NetworkTransport


def test_transport_propagation_delay():
    transport = NetworkTransport(min_latency=1, max_latency=3, out_of_order_prob=0.0, seed=42)
    pkt = transport.send("agent_1", "HOST", {"test": 123}, current_tick=0)
    assert pkt is not None
    assert pkt.arrival_tick >= 1
    assert pkt.arrival_tick <= 3

    # At tick 0, poll should return nothing
    assert transport.poll(0, "HOST") == []

    # At tick 3, packet must be delivered
    delivered = transport.poll(3, "HOST")
    assert len(delivered) == 1
    assert delivered[0].payload == {"test": 123}

    # Polling again should yield nothing (delivered flag set)
    assert transport.poll(3, "HOST") == []


def test_transport_out_of_order():
    transport = NetworkTransport(min_latency=0, max_latency=5, out_of_order_prob=0.5, seed=123)
    for i in range(5):
        transport.send(f"agent_{i+1}", "HOST", {"seq": i}, current_tick=0)
    assert transport.get_in_flight(0) <= 5
