"""Scoped Context Delivery Engine for MN-009.

Deterministic, CPU-bound context scaffolding designed to compress unstructured
document streams, graph networks, and tabular states into a strict <=512 token
window under local Llama 3.2 token accounting. Zero GPU/VRAM overhead.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

_RE_TOKEN = re.compile(r"\w+|[^\w\s]")
_RE_PARAGRAPH = re.compile(r"\n\s*\n+")
_RE_SENTENCE = re.compile(r"(?<=[.!?])\s+")
_RE_WORD_LOWER = re.compile(r"\w+")


@dataclass(frozen=True)
class TextChunk:
    """Atomic chunk with boundary preservation."""
    chunk_id: int
    content: str
    token_count: int
    salience_score: float = 0.0


class InvariantViolationError(ValueError):
    """Raised when hard scaffolding invariants are violated."""


def sanitize_chat_tokens(text: str) -> str:
    """Escape Llama 3 chat-template control tokens to prevent prompt injection."""
    if "<|" not in text:
        return text
    patterns = [
        ("<|begin_of_text|>", r"\<\|begin_of_text\|\>"),
        ("<|end_of_text|>", r"\<\|end_of_text\|\>"),
        ("<|start_header_id|>", r"\<\|start_header_id\|\>"),
        ("<|end_header_id|>", r"\<\|end_header_id\|\>"),
        ("<|eot_id|>", r"\<\|eot_id\|\>"),
    ]
    sanitized = text
    for raw, escaped in patterns:
        sanitized = sanitized.replace(raw, escaped)
    return sanitized


def assert_temporal_invariant(
    active_entities: Iterable[str],
    latest_state_table: dict[str, Any],
) -> None:
    """Verify that every entity active in the query/situation has an explicit latest state.
    
    Prevents small-model state hallucination when encountering unanchored entities.
    """
    for entity in active_entities:
        if entity not in latest_state_table:
            raise InvariantViolationError(
                f"Temporal Invariant Violation: Entity '{entity}' missing explicit latest state."
            )


def slice_graph_by_khop(
    graph: dict[str, list[str]],
    target_entities: set[str],
    max_hops: int = 2,
) -> dict[str, list[str]]:
    """Extract induced k-hop subgraph centered around target entities via BFS.
    
    Compresses hundreds of distant graph nodes to immediate geodesic neighbors in O(V+E).
    """
    subgraph_nodes = set(target_entities)
    frontier = set(target_entities)

    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            neighbors = graph.get(node, [])
            for neighbor in neighbors:
                if neighbor not in subgraph_nodes:
                    next_frontier.add(neighbor)
        subgraph_nodes.update(next_frontier)
        frontier = next_frontier
        if not frontier:
            break

    # Build pruned induced subgraph
    sliced = {}
    for node in subgraph_nodes:
        sliced[node] = [tgt for tgt in graph.get(node, []) if tgt in subgraph_nodes]
    return sliced


def slice_table_by_projection(
    table: dict[str, dict[str, Any]],
    active_entities: set[str],
    target_columns: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Filter rows by active entities and project only relevant attributes."""
    sliced = {}
    for entity in active_entities:
        if entity in table:
            row = table[entity]
            if target_columns is not None:
                sliced[entity] = {k: v for k, v in row.items() if k in target_columns}
            else:
                sliced[entity] = dict(row)
    return sliced


class ContextPacker:
    """Deterministic Knapsack Context Packer with Lexical Salience and Chronological Sorting."""

    def __init__(
        self,
        max_budget: int = 512,
        tokenizer_func: Callable[[str], int] | None = None,
    ) -> None:
        self.max_budget = max_budget
        # Approximate 1 token ~= 3.5 chars in English/code if no offline tokenizer provided
        self.tokenizer_func = tokenizer_func or self._fallback_tokenizer

    def _fallback_tokenizer(self, text: str) -> int:
        """Conservative lexical token estimator."""
        words = len(_RE_TOKEN.findall(text))
        return max(1, int(words * 1.15))

    def count_tokens(self, text: str) -> int:
        """Count tokens using verified tokenizer callback or conservative fallback."""
        if not text or not text.strip():
            return 0
        return self.tokenizer_func(text)

    def split_natural_boundaries(self, text: str) -> list[str]:
        """Split text into atomic paragraphs and sentences without mid-sentence cuts."""
        raw_paragraphs = [p.strip() for p in _RE_PARAGRAPH.split(text) if p.strip()]
        chunks = []
        for p in raw_paragraphs:
            if self._fallback_tokenizer(p) <= 120:
                chunks.append(p)
            else:
                # Split large paragraphs by sentence endings
                sentences = [s.strip() for s in _RE_SENTENCE.split(p) if s.strip()]
                current_parts: list[str] = []
                current_tokens = 0
                for s in sentences:
                    s_tok = self._fallback_tokenizer(s)
                    if current_tokens + s_tok > 100 and current_parts:
                        chunks.append(" ".join(current_parts))
                        current_parts = [s]
                        current_tokens = s_tok
                    else:
                        current_parts.append(s)
                        current_tokens += s_tok
                if current_parts:
                    chunks.append(" ".join(current_parts))
        return chunks

    def compute_lexical_salience(self, chunk: str, query_terms: Counter) -> float:
        """Compute fast linear term-frequency overlap score against target query."""
        chunk_words = _RE_WORD_LOWER.findall(chunk.lower())
        if not chunk_words:
            return 0.0
        score = 0.0
        for word in chunk_words:
            if word in query_terms:
                score += query_terms[word]
        # Normalize slightly by chunk length to prevent bias toward raw length
        return score / math.sqrt(len(chunk_words))

    def pack(
        self,
        raw_documents: list[str],
        query: str,
        system_prefix: str = "",
        anchor_first_chunk: bool = True,
    ) -> str:
        """Pack document streams into <= max_budget tokens while maximizing query salience."""
        system_prefix = sanitize_chat_tokens(system_prefix.strip())
        query = sanitize_chat_tokens(query.strip())

        prefix_header = ""
        if system_prefix:
            prefix_header = f"{system_prefix}\n\n"
        query_footer = f"\n\nQuery: {query}\nResponse:"

        overhead_tokens = (
            self.count_tokens(prefix_header) if prefix_header.strip() else 0
        ) + (self.count_tokens(query_footer) if query_footer.strip() else 0)
        available_budget = self.max_budget - overhead_tokens
        if available_budget <= 50:
            raise ValueError(
                f"Prefix and query consume {overhead_tokens} tokens, exceeding safe margin for budget {self.max_budget}."
            )

        # 1. Flatten documents and split on natural boundaries
        all_text = "\n\n".join(raw_documents)
        raw_chunks = self.split_natural_boundaries(all_text)
        if not raw_chunks:
            return f"{prefix_header.strip()}{query_footer}".strip()

        # Tokenize and score all chunks using single-pass lexical analysis
        query_terms = Counter(_RE_WORD_LOWER.findall(query.lower()))
        indexed_chunks = []
        for idx, c in enumerate(raw_chunks):
            c_clean = sanitize_chat_tokens(c)
            words = _RE_WORD_LOWER.findall(c_clean.lower())
            word_count = len(words)
            tok_count = max(1, int(word_count * 1.15))
            score = 0.0
            if word_count > 0:
                raw_score = sum(query_terms[w] for w in words if w in query_terms)
                score = raw_score / math.sqrt(word_count)
            indexed_chunks.append(TextChunk(idx, c_clean, tok_count, score))

        # 2. Anchor-and-Spoke: Reserve Chunk 0 (Executive Anchor) if requested
        selected_chunks: list[TextChunk] = []
        current_used = 0

        remaining_candidates = list(indexed_chunks)
        if anchor_first_chunk and indexed_chunks:
            anchor = indexed_chunks[0]
            if anchor.token_count <= available_budget:
                selected_chunks.append(anchor)
                current_used += anchor.token_count
                remaining_candidates = indexed_chunks[1:]

        # 3. Sort candidates by salience score descending (Greedy Knapsack)
        remaining_candidates.sort(key=lambda x: x.salience_score, reverse=True)

        for candidate in remaining_candidates:
            if current_used + candidate.token_count <= available_budget:
                selected_chunks.append(candidate)
                current_used += candidate.token_count

        # 4. Chronological Invariant: Re-sort selected chunks by original document order
        selected_chunks.sort(key=lambda x: x.chunk_id)

        # 5. Assemble final prompt
        body_text = "\n\n".join(ch.content for ch in selected_chunks)
        result = f"{prefix_header}{body_text}{query_footer}".strip()

        # 6. Final Hard Assertion Guard
        final_token_count = self.count_tokens(result)
        while selected_chunks and final_token_count > self.max_budget:
            # Deterministically prune lowest salience non-anchor chunk
            candidates_to_prune = (
                selected_chunks[1:]
                if anchor_first_chunk and len(selected_chunks) > 1
                else selected_chunks
            )
            lowest_chunk = min(candidates_to_prune, key=lambda x: x.salience_score)
            selected_chunks.remove(lowest_chunk)
            body_text = "\n\n".join(ch.content for ch in selected_chunks)
            result = f"{prefix_header}{body_text}{query_footer}".strip()
            final_token_count = self.count_tokens(result)

        return result
