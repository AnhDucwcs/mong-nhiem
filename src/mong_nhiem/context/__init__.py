"""Context delivery and scaffolding subsystem for Mộng Nhiễm."""
from __future__ import annotations

from mong_nhiem.context.config import (
    DEFAULT_CONTEXT_BUDGET,
    MODEL_BUDGET_PROFILES,
    register_model_budget_profile,
    resolve_context_budget,
)
from mong_nhiem.context.coordinator import (
    ActionType,
    AgentAction,
    CircuitBreaker,
    CircuitBreakerStatus,
    CoordinatorResult,
    IterativeCoordinator,
    TurnRecord,
    format_action,
    parse_action,
)
from mong_nhiem.context.packer import (
    ContextPacker,
    InvariantViolationError,
    TextChunk,
    assert_temporal_invariant,
    sanitize_chat_tokens,
    slice_graph_by_khop,
    slice_table_by_projection,
)
from mong_nhiem.context.slicer import CodebaseSlicer, slice_codebase

__all__ = [
    "DEFAULT_CONTEXT_BUDGET",
    "MODEL_BUDGET_PROFILES",
    "register_model_budget_profile",
    "resolve_context_budget",
    "ContextPacker",
    "TextChunk",
    "InvariantViolationError",
    "sanitize_chat_tokens",
    "assert_temporal_invariant",
    "slice_graph_by_khop",
    "slice_table_by_projection",
    "CodebaseSlicer",
    "slice_codebase",
    "ActionType",
    "AgentAction",
    "parse_action",
    "format_action",
    "CircuitBreakerStatus",
    "CircuitBreaker",
    "TurnRecord",
    "CoordinatorResult",
    "IterativeCoordinator",
]

