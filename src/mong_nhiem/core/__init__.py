"""Core primitives and invariants for Mộng Nhiễm cognitive architecture."""

from __future__ import annotations

from .events import CausalEvent
from .invariants import ConservationInvariantGuard, InvariantViolationError
from .semantic_gate import SemanticInvariantGate, SemanticPrecondition
from .vector_clock import VectorClock

__all__ = [
    "CausalEvent",
    "ConservationInvariantGuard",
    "InvariantViolationError",
    "SemanticInvariantGate",
    "SemanticPrecondition",
    "VectorClock",
]
