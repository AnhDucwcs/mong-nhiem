"""Mộng Nhiễm Cognitive Orchestration Subsystem.

Provides dual-layer dynamic affordance steering, Context-Free Grammar (GBNF)
compilation, host Memento state checkpointing, bounded context rewinding,
multi-resource concurrency leases, star consensus governance, and hierarchical planning.
100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

from .affordance import BaseAffordanceProvider, DeclarativeAffordanceEngine
from .arbiter import MultiResourceArbiter, ResourceLease
from .circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from .consensus import ByzantineAdmissionGate, ProposalFilterResult, StarConsensusHub
from .coordinator import CognitiveOrchestrator
from .grammar import DynamicGBNFCompiler
from .memento import Memento, MementoStack
from .phase_gate import PhaseGate
from .planner import HierarchicalPlanner, MissionGraph, SubGoal
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
from .transport import AsynchronousTransport, NetworkPacket

__all__ = [
    "ActionType",
    "AffordanceSpec",
    "AsynchronousTransport",
    "BaseAffordanceProvider",
    "ByzantineAdmissionGate",
    "CircuitBreaker",
    "CircuitBreakerStatus",
    "CognitiveOrchestrator",
    "ContextRewindManager",
    "DeclarativeAffordanceEngine",
    "DynamicGBNFCompiler",
    "HierarchicalPlanner",
    "Memento",
    "MementoStack",
    "MissionGraph",
    "MultiResourceArbiter",
    "NetworkPacket",
    "OrchestratorResult",
    "PhaseGate",
    "ProposalFilterResult",
    "ResourceLease",
    "StarConsensusHub",
    "SubGoal",
    "ToolAction",
    "TurnRecord",
    "format_action",
    "format_affordance_prior",
    "parse_action",
]
