"""Context delivery and scaffolding subsystem for Mộng Nhiễm."""
from __future__ import annotations

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
    "ContextPacker",
    "TextChunk",
    "InvariantViolationError",
    "sanitize_chat_tokens",
    "assert_temporal_invariant",
    "slice_graph_by_khop",
    "slice_table_by_projection",
    "CodebaseSlicer",
    "slice_codebase",
]
