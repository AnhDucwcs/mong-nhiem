"""Mộng Nhiễm Cognitive Orchestration Subsystem.

Provides dual-layer dynamic affordance steering, Context-Free Grammar (GBNF)
compilation, host Memento state checkpointing, and bounded context rewinding.
100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

from .affordance import BaseAffordanceProvider, DeclarativeAffordanceEngine
from .circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from .coordinator import CognitiveOrchestrator
from .grammar import DynamicGBNFCompiler
from .memento import Memento, MementoStack
from .phase_gate import PhaseGate
from .protocol import (
    ActionType,
    AffordanceSpec,
    OrchestratorResult,
    ToolAction,
    TurnRecord,
    format_action,
    format_affordance_prior,
    parse_action,
)
from .rewind import ContextRewindManager

__all__ = [
    "ActionType",
    "AffordanceSpec",
    "BaseAffordanceProvider",
    "CircuitBreaker",
    "CircuitBreakerStatus",
    "CognitiveOrchestrator",
    "ContextRewindManager",
    "DeclarativeAffordanceEngine",
    "DynamicGBNFCompiler",
    "Memento",
    "MementoStack",
    "OrchestratorResult",
    "PhaseGate",
    "ToolAction",
    "TurnRecord",
    "format_action",
    "format_affordance_prior",
    "parse_action",
]
