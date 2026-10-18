"""Mộng Nhiễm Cognitive Orchestration Subsystem.

Provides dual-layer dynamic affordance steering, Context-Free Grammar (GBNF)
compilation, host Memento state checkpointing, bounded context rewinding,
multi-resource concurrency leases, star consensus governance, and hierarchical planning.
100% Python Standard Library. Zero external dependencies.
"""
from __future__ import annotations

from .affordance import BaseAffordanceProvider, DeclarativeAffordanceEngine
from .affordance_ranker import GoalConditionedAffordanceRanker
from .arbiter import MultiResourceArbiter, ResourceLease
from .circuit_breaker import CircuitBreaker, CircuitBreakerStatus
from .consensus import ByzantineAdmissionGate, ProposalFilterResult, StarConsensusHub
from .coordinator import CognitiveOrchestrator
from .grammar import DynamicGBNFCompiler
from .jitter_arbiter import VirtualJitterArbiter, VirtualRoleProfile
from .memento import Memento, MementoStack
from .phase_gate import PhaseGate
from .planner import HierarchicalPlanner, MissionGraph, SubGoal
from .preemption_gate import ActionClass, PreemptiveInterruptGate, PreemptiveShock
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
from .reflex_breaker import RedlineRule, ReflexCircuitBreaker, ReflexState
from .rewind import ContextRewindManager
from .telemetry_observer import BlackoutMode, ProxyEstimator, TelemetryObserver
from .transport import AsynchronousTransport, NetworkPacket

__all__ = [
    "ActionClass",
    "ActionType",
    "AffordanceSpec",
    "AsynchronousTransport",
    "BaseAffordanceProvider",
    "BlackoutMode",
    "ByzantineAdmissionGate",
    "CircuitBreaker",
    "CircuitBreakerStatus",
    "CognitiveOrchestrator",
    "ContextRewindManager",
    "DeclarativeAffordanceEngine",
    "DynamicGBNFCompiler",
    "GoalConditionedAffordanceRanker",
    "HierarchicalPlanner",
    "Memento",
    "MementoStack",
    "MissionGraph",
    "MultiResourceArbiter",
    "NetworkPacket",
    "OrchestratorResult",
    "PhaseGate",
    "PreemptiveInterruptGate",
    "PreemptiveShock",
    "ProposalFilterResult",
    "ProxyEstimator",
    "RedlineRule",
    "ReflexCircuitBreaker",
    "ReflexState",
    "ResourceLease",
    "StarConsensusHub",
    "SubGoal",
    "TelemetryObserver",
    "ToolAction",
    "TurnRecord",
    "VirtualJitterArbiter",
    "VirtualRoleProfile",
    "format_action",
    "format_affordance_prior",
    "parse_action",
]
