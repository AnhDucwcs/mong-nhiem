"""Frontier evaluator and metric calculation engine for MN-011.

Calculates context conversion efficiency, handles parametric knapsack budget packing,
and extracts causal graph reachability components.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple

from mong_nhiem.context import ContextPacker, sanitize_chat_tokens, slice_graph_by_khop


def compute_conversion_efficiency(salient_tokens: int, fed_tokens: int) -> float:
    """Compute context conversion efficiency eta = salient_tokens / fed_tokens.
    
    Quantifies the cognitive utility per token injected into the prompt.
    """
    if fed_tokens <= 0:
        return 0.0
    return round(min(1.0, salient_tokens / fed_tokens), 4)


_CAUSAL_EDGE_REGEX = re.compile(r"(\w+)\s+directly causes\s+(\w+)", re.IGNORECASE)


def parse_causal_graph(edge_sentences: List[str]) -> Dict[str, List[str]]:
    """Parse textual causal edge statements into an adjacency list."""
    graph: Dict[str, List[str]] = {}
    for sentence in edge_sentences:
        match = _CAUSAL_EDGE_REGEX.search(sentence)
        if match:
            u, v = match.group(1), match.group(2)
            if u not in graph:
                graph[u] = []
            graph[u].append(v)
            if v not in graph:
                graph[v] = []
    return graph


def check_graph_reachability(graph: Dict[str, List[str]], source: str, target: str) -> bool:
    """Determine whether target is reachable from source via BFS traversal."""
    if source not in graph:
        return False
    visited: Set[str] = set()
    queue = [source]
    while queue:
        curr = queue.pop(0)
        if curr == target:
            return True
        if curr not in visited:
            visited.add(curr)
            for neighbor in graph.get(curr, []):
                if neighbor not in visited:
                    queue.append(neighbor)
    return False


def build_scaffolded_causal_prompt(
    raw_edges: List[str],
    source: str,
    target: str,
    query: str,
    packer: ContextPacker,
) -> Tuple[str, int, int]:
    """Extract induced causal subgraph and pack into bounded prompt (<= 512 tokens).
    
    Returns (packed_prompt, prompt_tokens, pruned_edge_count).
    """
    graph = parse_causal_graph(raw_edges)
    # Extract 2-hop neighborhood centered around source and target
    subgraph = slice_graph_by_khop(graph, target_entities={source, target}, max_hops=2)

    # Format pruned edges
    pruned_edges = []
    for u, neighbors in subgraph.items():
        for v in neighbors:
            pruned_edges.append(f"{u} directly causes {v}.")

    if not pruned_edges:
        pruned_text = "No direct or indirect causal link found between entities."
    else:
        pruned_text = "\n".join(pruned_edges)

    packed_prompt = packer.pack(
        [pruned_text],
        query=query,
        system_prefix="You are a rigorous causal reasoning engine. Answer with exactly YES or NO.",
    )
    prompt_tokens = packer.count_tokens(packed_prompt)
    return packed_prompt, prompt_tokens, len(pruned_edges)
