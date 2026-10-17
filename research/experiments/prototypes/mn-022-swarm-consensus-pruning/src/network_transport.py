"""Network Transport Layer simulating stochastic packet latency and out-of-order arrival."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NetworkPacket:
    packet_id: str
    sender_id: str
    recipient_id: str
    payload: Dict[str, Any]
    send_tick: int
    arrival_tick: int
    delivered: bool = False


class NetworkTransport:
    """Simulates asynchronous network transmission with stochastic delays tau in [min_latency, max_latency]."""

    def __init__(
        self,
        min_latency: int = 0,
        max_latency: int = 5,
        out_of_order_prob: float = 0.1,
        drop_prob: float = 0.0,
        seed: Optional[int] = None,
    ) -> None:
        self.min_latency = min_latency
        self.max_latency = max_latency
        self.out_of_order_prob = out_of_order_prob
        self.drop_prob = drop_prob
        self._rng = random.Random(seed)
        self._queue: List[NetworkPacket] = []
        self._counter = 0

    def send(
        self,
        sender_id: str,
        recipient_id: str,
        payload: Dict[str, Any],
        current_tick: int,
    ) -> Optional[NetworkPacket]:
        """Enqueues a packet with stochastic propagation delay."""
        if self.drop_prob > 0.0 and self._rng.random() < self.drop_prob:
            return None  # Dropped packet (lossy / noisy channel)

        latency = self._rng.randint(self.min_latency, self.max_latency)
        # Potential jitter / out-of-order reordering
        if self.out_of_order_prob > 0.0 and self._rng.random() < self.out_of_order_prob:
            latency = min(self.max_latency, latency + self._rng.randint(1, 2))

        arrival_tick = current_tick + latency
        self._counter += 1
        packet = NetworkPacket(
            packet_id=f"pkt-{self._counter:05d}",
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload=payload,
            send_tick=current_tick,
            arrival_tick=arrival_tick,
            delivered=False,
        )
        self._queue.append(packet)
        return packet

    def poll(self, current_tick: int, recipient_id: str) -> List[NetworkPacket]:
        """Retrieves and marks delivered all packets due on or before current_tick for recipient."""
        due_packets: List[NetworkPacket] = []
        for pkt in self._queue:
            if not pkt.delivered and pkt.recipient_id == recipient_id and pkt.arrival_tick <= current_tick:
                pkt.delivered = True
                due_packets.append(pkt)
        return due_packets

    def get_in_flight(self, current_tick: int) -> int:
        """Returns the number of un-delivered packets still in flight."""
        return sum(1 for p in self._queue if not p.delivered and p.arrival_tick > current_tick)

    def reset(self, seed: Optional[int] = None) -> None:
        """Resets the packet queue and seed."""
        self._queue.clear()
        self._counter = 0
        if seed is not None:
            self._rng.seed(seed)
