#!/usr/bin/env python3
"""Frozen-definition helpers and deterministic evaluator for MCB v0.3.0."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmark" / "v0.3.0"
CASES = BENCHMARK / "cases"
VERSION = "0.3.0"
SUITES = ("instruction_following", "structured_output", "context_retrieval", "state_tracking", "causal_reasoning")


def normalize_surface(value: str) -> str:
    """Conservative comparison for declared non-structured aliases only."""
    value = unicodedata.normalize("NFKC", value).strip()
    value = re.sub(r"[.!?]+$", "", value).strip()
    return " ".join(value.casefold().split())


def evaluate(case: dict[str, Any], text: str) -> tuple[bool, str | None, str]:
    """Return pass, accepted canonical answer, and normalized response.

    The evaluator accepts only the case's explicitly declared values, after the
    documented punctuation/whitespace/case normalization. It never uses
    substring, embedding, or open-ended semantic matching.
    """
    method = case["evaluation"]["method"]
    normalized = normalize_surface(text)
    if method == "json_schema":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return False, None, normalized
        schema = case["expected"]["schema"]
        required = schema["required"]
        if not isinstance(parsed, dict) or set(parsed) != set(required):
            return False, None, normalized
        if all(parsed[key] == schema["properties"][key]["const"] for key in required):
            return True, json.dumps(parsed, sort_keys=True), normalized
        return False, None, normalized
    for accepted in case["expected"]["accepted_values"]:
        if normalized == normalize_surface(accepted):
            return True, case["expected"]["value"], normalized
    return False, None, normalized


def definition_fingerprint() -> str:
    digest = hashlib.sha256()
    for file in sorted(CASES.glob("*.jsonl")):
        digest.update(file.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file.read_bytes())
    return digest.hexdigest()


def load_cases() -> list[dict[str, Any]]:
    return [json.loads(line) for suite in SUITES for line in (CASES / f"{suite}.jsonl").read_text(encoding="utf-8").splitlines() if line]


def validate_definitions() -> None:
    cases = load_cases()
    counts = {suite: sum(case["suite"] == suite for case in cases) for suite in SUITES}
    if len(cases) != 100 or len({case["id"] for case in cases}) != 100 or any(value != 20 for value in counts.values()):
        raise RuntimeError(f"invalid case inventory: {counts}, total={len(cases)}")
    for case in cases:
        if case["version"] != 3 or "accepted_values" not in case["expected"]:
            raise RuntimeError(f"invalid v0.3 contract in {case['id']}")
    print(f"Validated MCB {VERSION}; definition fingerprint {definition_fingerprint()}")
