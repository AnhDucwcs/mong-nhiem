#!/usr/bin/env python3
"""Calibrated ECC-006 State Tracking baseline runner for Qwen models.

Fixes:
1. Fine-grained line-level distractor budgeting at small contexts (512 tokens)
   to eliminate integer quantization error (Nyquist sampling artifact).
2. O(log N) binary search for midpoint placement, eliminating the 700-call HTTP
   roundtrip bottleneck in build_case.
3. Preserves 100% compatibility with frozen Gate B measurement contracts.
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFINITION, CONFIGS, RUNS = ROOT / "definition", ROOT / "configs", ROOT / "runs"
ECC001_SCRIPTS = ROOT.parent / "ecc-001-context-retrieval" / "scripts"
sys.path.insert(0, str(ECC001_SCRIPTS))
import ecc001

ContractError = ecc001.ContractError
ServerClient = ecc001.ServerClient
TokenRuntime = ecc001.TokenRuntime

# Inherit constants and helpers from canonical ecc006
import ecc006

load_json = ecc006.load_json
dump_json = ecc006.dump_json
definition_fingerprint = ecc006.definition_fingerprint
load_definition = ecc006.load_definition
target_events = ecc006.target_events
distractor = ecc006.distractor
BuiltCase = ecc006.BuiltCase
evaluate = ecc006.evaluate
built_case_dict = ecc006.built_case_dict
failure = ecc006.failure


def distractor_pool(case_id: str, count: int, side: str, seed: int) -> list[str]:
    """Generate fine-grained line-level distractors with deterministic hashing."""
    lines: list[str] = []
    block_idx = 1
    while len(lines) < count:
        lines.extend(distractor(case_id, block_idx, side, seed))
        block_idx += 1
    return lines[:count]


def compose_lines(
    case: dict[str, Any],
    total_lines: int,
    seed: int,
    before_lines: int | None = None,
) -> tuple[str, str, str, list[str]]:
    """Compose prompt with exact line-level granularity for fine-grained midpoint placement."""
    before_lines = total_lines // 2 if before_lines is None else before_lines
    after_lines = total_lines - before_lines
    before = distractor_pool(case["id"], before_lines, "before", seed)
    after = distractor_pool(case["id"], after_lines, "after", seed)
    target = target_events(case)
    prefix = "Context event log:\n" + ("\n".join(before) + "\n" if before else "")
    context = prefix + "\n".join(target) + ("\n" + "\n".join(after) if after else "")
    content = context + f"\n\nQuestion:\nWhat is the current state of {case['entity']}? Return only the state."
    return context, content, prefix, before + after


def build_case_calibrated(
    runtime: TokenRuntime,
    case: dict[str, Any],
    target: int,
    definition: dict[str, Any],
) -> BuiltCase:
    """Optimized case builder with line-level budgeting and O(log N) midpoint convergence."""
    seed = definition["case_generation"]["seed"]

    # 1. Determine optimal distractor line count using binary search
    def count_prompt_lines(lines: int) -> int:
        _, content, _, _ = compose_lines(case, lines, seed)
        return runtime.count_prompt(content)

    if count_prompt_lines(0) > target:
        raise ContractError(f"{case['id']} cannot fit target {target}")

    low_lines, high_lines = 0, 1
    while count_prompt_lines(high_lines) <= target:
        low_lines, high_lines = high_lines, high_lines * 2
        if high_lines > target * 2:
            break

    while low_lines + 1 < high_lines:
        mid = (low_lines + high_lines) // 2
        if count_prompt_lines(mid) <= target:
            low_lines = mid
        else:
            high_lines = mid

    # 2. Optimize Midpoint Placement via Binary Search in O(log N)
    # Target context tokens is invariant across before/after reordering
    sample_context, _, _, _ = compose_lines(case, low_lines, seed, low_lines // 2)
    context_tokens = runtime.count_text(sample_context)
    target_ratio = definition["controls"]["evidence_position"]["target_ratio"]
    target_prefix_tokens = context_tokens * target_ratio

    low_b, high_b = 0, low_lines
    best_candidate = None
    best_distance = float("inf")

    # Binary search for closest prefix token count to target_prefix_tokens
    while low_b <= high_b:
        mid_b = (low_b + high_b) // 2
        ctx, content, prefix, _ = compose_lines(case, low_lines, seed, mid_b)
        prefix_tokens = runtime.count_text(prefix)
        ratio = prefix_tokens / context_tokens if context_tokens else 0.0
        distance = abs(ratio - target_ratio)

        if distance < best_distance:
            best_distance = distance
            actual_cand = runtime.count_prompt(content)
            best_candidate = (distance, ctx, content, prefix, actual_cand, mid_b, prefix_tokens, ratio)

        if prefix_tokens < target_prefix_tokens:
            low_b = mid_b + 1
        elif prefix_tokens > target_prefix_tokens:
            high_b = mid_b - 1
        else:
            break

    if not best_candidate:
        raise ContractError("no valid midpoint placement candidate")

    _dist, context, content, prefix, actual, _before, start, ratio = best_candidate
    content_tokens = runtime.count_text(content)
    shortfall = target - actual
    budget = definition["token_budget"]
    controls = definition["controls"]

    if not (0 <= shortfall <= budget["maximum_target_shortfall_tokens"]):
        raise ContractError(f"token shortfall {shortfall} violates definition ({budget['maximum_target_shortfall_tokens']})")
    if abs(ratio - controls["evidence_position"]["target_ratio"]) > controls["evidence_position"]["allowed_absolute_error"]:
        raise ContractError(f"target sequence violates midpoint policy: ratio={ratio:.4f} (target {target_ratio} +- {controls['evidence_position']['allowed_absolute_error']})")
    if actual + budget["output_tokens"] > budget["configured_context_size"]:
        raise ContractError("context overflow")

    return BuiltCase(
        case_id=case["id"],
        requested_input_tokens=target,
        actual_input_tokens=actual,
        content_tokens=content_tokens,
        prompt_overhead_tokens=actual - content_tokens,
        context_tokens=context_tokens,
        evidence_start_token=start,
        evidence_position_ratio=round(ratio, 6),
        distractor_histories=low_lines // 4,
        distractor_histories_before=_before // 4,
        relevant_fact="\n".join(target_events(case)),
        expected_answer=case["answer"],
        context_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        content=content,
    )
