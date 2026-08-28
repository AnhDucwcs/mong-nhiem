#!/usr/bin/env python3
"""Deterministic scientific contracts for ECC-001."""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import unicodedata
import urllib.request
from dataclasses import asdict, dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any, Protocol

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEFINITION = ROOT / "definition"
SCHEMAS = ROOT / "schemas"
CONFIGS = ROOT / "configs"
RUNS = ROOT / "runs"


class ContractError(RuntimeError):
    """Raised when scientific or evidence contracts are violated."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON; independent of file formatting and line endings."""
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def fingerprint_values(definition: dict[str, Any], cases: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    for label, value in (("experiment.json", definition), ("cases.json", cases)):
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(canonical_json(value))
    return digest.hexdigest()


def definition_fingerprint() -> str:
    return fingerprint_values(load_json(DEFINITION / "experiment.json"), load_json(DEFINITION / "cases.json"))


def schema_errors(value: Any, schema_name: str) -> list[str]:
    validator = Draft202012Validator(load_json(SCHEMAS / schema_name))
    return [error.message for error in validator.iter_errors(value)]


def load_definition() -> tuple[dict[str, Any], list[dict[str, str]]]:
    definition = load_json(DEFINITION / "experiment.json")
    inventory = load_json(DEFINITION / "cases.json")
    errors = schema_errors(definition, "experiment-definition.schema.json")
    cases = inventory.get("cases", [])
    levels = definition["independent_variable"]["levels"]
    if errors:
        raise ContractError(f"invalid experiment definition: {errors[0]}")
    if inventory.get("version") != 1 or len(cases) != definition["case_generation"]["semantic_cases"]:
        raise ContractError("case inventory version/count does not match experiment definition")
    if len({case["id"] for case in cases}) != len(cases):
        raise ContractError("case IDs must be unique")
    if len({case["entity"] for case in cases}) != len(cases) or len({case["answer"] for case in cases}) != len(cases):
        raise ContractError("entities and answers must be unique")
    if levels != sorted(levels) or len(levels) != len(set(levels)):
        raise ContractError("context levels must be unique and ascending")
    return definition, cases


def normalize_answer(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip()
    value = re.sub(r"[.!?]+$", "", value).strip()
    return " ".join(value.casefold().split())


def evaluate(expected: str, raw: str) -> tuple[bool, str]:
    normalized = normalize_answer(raw)
    return normalized == normalize_answer(expected), normalized


_NAMES = ("Amina", "Borin", "Celia", "Dario", "Esme", "Farah", "Galen", "Hana", "Ivo", "Jora", "Kian", "Lumi")
_PLACES = ("cedar depot", "north archive", "river terminal", "amber warehouse", "west registry", "granite annex")
_ITEMS = ("parcel", "ledger", "sample", "permit", "manifest", "instrument")
_STATES = ("routine review", "quality inspection", "scheduled transfer", "inventory reconciliation", "custody verification")


def distractor(case_id: str, pair_index: int, side: str, seed: int) -> str:
    """Create a plausible, irrelevant record without access-code language."""
    digest = hashlib.sha256(f"{seed}:{case_id}:{pair_index}:{side}".encode()).digest()
    name = _NAMES[digest[0] % len(_NAMES)]
    place = _PLACES[digest[1] % len(_PLACES)]
    item = _ITEMS[digest[2] % len(_ITEMS)]
    state = _STATES[digest[3] % len(_STATES)]
    day = 1 + digest[4] % 28
    batch = 100 + int.from_bytes(digest[5:7], "big") % 900
    return f"Registry record {pair_index:04d}-{side}: {name} logged a {item} at the {place} on day {day}; batch {batch} remains under {state}."


def relevant_fact(case: dict[str, str]) -> str:
    return f"The access code for Project {case['entity']} is {case['answer']}."


def question(case: dict[str, str]) -> str:
    return f"What is the access code for Project {case['entity']}? Return only the access code."


def compose(case: dict[str, str], pairs: int, seed: int) -> tuple[str, str, str]:
    before = [distractor(case["id"], index, "A", seed) for index in range(1, pairs + 1)]
    after = [distractor(case["id"], index, "B", seed) for index in range(1, pairs + 1)]
    before_text = "\n".join(before)
    after_text = "\n".join(after)
    prefix = "Context records:\n" + (before_text + "\n" if before_text else "") + "TARGET FACT: "
    context = prefix + relevant_fact(case) + ("\n" + after_text if after_text else "")
    content = context + "\n\nQuestion:\n" + question(case)
    return context, content, prefix


class TokenRuntime(Protocol):
    def count_text(self, text: str) -> int: ...
    def count_prompt(self, content: str) -> int: ...


@dataclass(frozen=True)
class BuiltCase:
    case_id: str
    requested_input_tokens: int
    actual_input_tokens: int
    content_tokens: int
    prompt_overhead_tokens: int
    context_tokens: int
    evidence_start_token: int
    evidence_position_ratio: float
    distractor_pairs: int
    relevant_fact: str
    expected_answer: str
    context_sha256: str
    content: str


def build_case(runtime: TokenRuntime, case: dict[str, str], target: int, definition: dict[str, Any]) -> BuiltCase:
    seed = definition["case_generation"]["seed"]
    output_tokens = definition["token_budget"]["output_tokens"]
    configured = definition["token_budget"]["configured_context_size"]

    def prompt_tokens(pairs: int) -> int:
        return runtime.count_prompt(compose(case, pairs, seed)[1])

    if prompt_tokens(0) > target:
        raise ContractError(f"{case['id']} cannot fit shortest target {target}")
    low, high = 0, 1
    while prompt_tokens(high) <= target:
        low, high = high, high * 2
        if high > target:
            break
    while low + 1 < high:
        middle = (low + high) // 2
        if prompt_tokens(middle) <= target:
            low = middle
        else:
            high = middle
    context, content, prefix = compose(case, low, seed)
    actual = runtime.count_prompt(content)
    content_tokens = runtime.count_text(content)
    context_tokens = runtime.count_text(context)
    evidence_start = runtime.count_text(prefix)
    ratio = evidence_start / context_tokens
    shortfall = target - actual
    maximum_shortfall = definition["token_budget"]["maximum_target_shortfall_tokens"]
    allowed_position_error = definition["evidence_position"]["allowed_absolute_error"]
    target_ratio = definition["evidence_position"]["target_ratio"]
    if shortfall < 0 or shortfall > maximum_shortfall:
        raise ContractError(f"{case['id']} target {target}: token shortfall {shortfall} exceeds {maximum_shortfall}")
    if abs(ratio - target_ratio) > allowed_position_error:
        raise ContractError(f"{case['id']} target {target}: evidence ratio {ratio:.4f} violates midpoint policy")
    if actual + output_tokens > configured:
        raise ContractError(f"{case['id']} target {target}: {actual}+{output_tokens} exceeds context {configured}")
    return BuiltCase(
        case_id=case["id"],
        requested_input_tokens=target,
        actual_input_tokens=actual,
        content_tokens=content_tokens,
        prompt_overhead_tokens=actual - content_tokens,
        context_tokens=context_tokens,
        evidence_start_token=evidence_start,
        evidence_position_ratio=round(ratio, 6),
        distractor_pairs=low,
        relevant_fact=relevant_fact(case),
        expected_answer=case["answer"],
        context_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        content=content,
    )


class ServerClient:
    def __init__(self, base_url: str, chat_template_kwargs: dict[str, Any]):
        self.base_url = base_url.rstrip("/")
        self.chat_template_kwargs = chat_template_kwargs

    def post(self, path: str, payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
        request = urllib.request.Request(
            self.base_url + path,
            json.dumps(payload).encode("utf-8"),
            {"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def count_text(self, text: str) -> int:
        result = self.post("/tokenize", {"content": text, "add_special": False})
        return len(result["tokens"])

    def count_prompt(self, content: str) -> int:
        template = self.post(
            "/apply-template",
            {
                "messages": [{"role": "user", "content": content}],
                "add_generation_prompt": True,
                "chat_template_kwargs": self.chat_template_kwargs,
            },
        )["prompt"]
        result = self.post("/tokenize", {"content": template, "add_special": True})
        return len(result["tokens"])

    def complete(self, content: str, inference: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = {
            "messages": [{"role": "user", "content": content}],
            "temperature": inference["temperature"],
            "seed": inference["seed"],
            "max_tokens": inference["output_tokens"],
            "chat_template_kwargs": self.chat_template_kwargs,
        }
        return payload, self.post("/v1/chat/completions", payload)


def threshold_ecc(levels: list[dict[str, Any]], threshold: float) -> int | None:
    value = None
    for level in levels:
        relative = level["relative_accuracy"]
        if relative is None or relative < threshold:
            break
        value = level["requested_input_tokens"]
    return value


def summarize(
    run_id: str,
    records: list[dict[str, Any]],
    selected_levels: list[int],
    selected_case_ids: list[str],
    complete_definition_coverage: bool,
) -> dict[str, Any]:
    invalid = sum(bool(record["error"]) or record["truncated"] for record in records)
    expected_results = len(selected_levels) * len(selected_case_ids)
    coverage_complete = complete_definition_coverage and len(records) == expected_results and invalid == 0
    level_rows: list[dict[str, Any]] = []
    for level in selected_levels:
        rows = [row for row in records if row["requested_input_tokens"] == level and not row["error"] and not row["truncated"]]
        passed = sum(row["evaluation"]["passed"] for row in rows)
        accuracy = passed / len(rows) if rows else None
        level_rows.append(
            {
                "requested_input_tokens": level,
                "cases": len(rows),
                "passed": passed,
                "accuracy": accuracy,
                "relative_accuracy": None,
                "actual_input_tokens_min": min((row["actual_input_tokens"] for row in rows), default=None),
                "actual_input_tokens_max": max((row["actual_input_tokens"] for row in rows), default=None),
            }
        )
    baseline_level = selected_levels[0] if selected_levels else None
    baseline_accuracy = level_rows[0]["accuracy"] if level_rows else None
    if baseline_accuracy:
        for row in level_rows:
            row["relative_accuracy"] = row["accuracy"] / baseline_accuracy if row["accuracy"] is not None else None
    accuracies = [row["accuracy"] for row in level_rows if row["accuracy"] is not None]
    non_monotonic = any(later > earlier for earlier, later in pairwise(accuracies))
    ecc_resolved = coverage_complete and baseline_accuracy is not None and baseline_accuracy > 0
    ecc = {
        "ECC95": threshold_ecc(level_rows, 0.95) if ecc_resolved else None,
        "ECC90": threshold_ecc(level_rows, 0.90) if ecc_resolved else None,
        "ECC80": threshold_ecc(level_rows, 0.80) if ecc_resolved else None,
        "status": "resolved" if ecc_resolved else "unresolved",
        "rule": "contiguous tested prefix; no interpolation",
    }
    timings = [row["timing"]["total_ms"] for row in records if not row["error"]]
    return {
        "run_id": run_id,
        "run_status": "valid" if coverage_complete else "invalid",
        "coverage": {"complete": coverage_complete, "expected_results": expected_results, "observed_results": len(records)},
        "total_results": len(records),
        "invalid_results": invalid,
        "baseline_context_level": baseline_level,
        "baseline_accuracy": baseline_accuracy,
        "levels": level_rows,
        "ecc": ecc,
        "non_monotonic": non_monotonic,
        "capability": {"interpretation": "direct-context retrieval accuracy only"},
        "runtime": {"median_total_ms": statistics.median(timings) if timings else None},
    }


def validate_run(run: Path) -> dict[str, Any]:
    definition, cases = load_definition()
    metadata = load_json(run / "metadata.json")
    summary = load_json(run / "summary.json")
    records = [json.loads(line) for line in (run / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    for value, schema, label in (
        (metadata, "run-metadata.schema.json", "metadata"),
        (summary, "run-summary.schema.json", "summary"),
    ):
        errors = schema_errors(value, schema)
        if errors:
            raise ContractError(f"{run.name}/{label}: {errors[0]}")
    if metadata["definition_fingerprint"] != definition_fingerprint():
        raise ContractError(f"{run.name}: definition fingerprint mismatch")
    selection = metadata["selection"]
    definition_levels = definition["independent_variable"]["levels"]
    definition_case_ids = [case["id"] for case in cases]
    selection_is_complete = (
        selection["context_levels"] == definition_levels
        and selection["case_ids"] == definition_case_ids
    )
    if selection["complete_definition_coverage"] != selection_is_complete:
        raise ContractError(f"{run.name}: complete-coverage flag does not match the definition")
    if selection_is_complete and metadata["repository"]["dirty"]:
        raise ContractError(f"{run.name}: complete run was produced from a dirty worktree")
    expected_pairs = {
        (case_id, level)
        for case_id in selection["case_ids"]
        for level in selection["context_levels"]
    }
    observed_pairs = [(record["case_id"], record["requested_input_tokens"]) for record in records]
    if len(observed_pairs) != len(set(observed_pairs)):
        raise ContractError(f"{run.name}: duplicate case/context result")
    if set(observed_pairs) != expected_pairs:
        raise ContractError(f"{run.name}: result coverage differs from metadata selection")
    case_lookup = {case["id"]: case for case in cases}
    for record in records:
        errors = schema_errors(record, "case-result.schema.json")
        if errors:
            raise ContractError(f"{run.name}/{record.get('case_id', '?')}: {errors[0]}")
        raw = record["output"]["raw_text"]
        case = case_lookup[record["case_id"]]
        if record["expected_answer"] != case["answer"] or record["relevant_fact"] != relevant_fact(case):
            raise ContractError(f"{run.name}/{record['case_id']}: stored task fact or answer is incorrect")
        passed, normalized = evaluate(case["answer"], raw)
        if record["output"]["normalized_text"] != normalized or record["evaluation"] != {"passed": passed, "score": float(passed)}:
            raise ContractError(f"{run.name}/{record['case_id']}: stored evaluation is incorrect")
        content = record["request"]["messages"][0]["content"]
        if hashlib.sha256(content.encode("utf-8")).hexdigest() != record["context_sha256"]:
            raise ContractError(f"{run.name}/{record['case_id']}: request hash mismatch")
        if record["actual_input_tokens"] + record["output_token_budget"] > record["configured_context_size"]:
            raise ContractError(f"{run.name}/{record['case_id']}: context overflow marked as evidence")
        shortfall = record["requested_input_tokens"] - record["actual_input_tokens"]
        if shortfall < 0 or shortfall > definition["token_budget"]["maximum_target_shortfall_tokens"]:
            raise ContractError(f"{run.name}/{record['case_id']}: token target shortfall violates the definition")
        if record["content_tokens"] + record["prompt_overhead_tokens"] != record["actual_input_tokens"]:
            raise ContractError(f"{run.name}/{record['case_id']}: token accounting is inconsistent")
        measured_ratio = round(record["evidence_start_token"] / record["context_tokens"], 6)
        if measured_ratio != record["evidence_position_ratio"]:
            raise ContractError(f"{run.name}/{record['case_id']}: stored evidence ratio is inconsistent")
        if abs(measured_ratio - definition["evidence_position"]["target_ratio"]) > definition["evidence_position"]["allowed_absolute_error"]:
            raise ContractError(f"{run.name}/{record['case_id']}: evidence position violates the definition")
        inference = metadata["inference"]
        expected_request = {
            "temperature": inference["temperature"],
            "seed": inference["seed"],
            "max_tokens": inference["output_tokens"],
            "chat_template_kwargs": inference["chat_template_kwargs"],
        }
        for key, expected in expected_request.items():
            if record["request"][key] != expected:
                raise ContractError(f"{run.name}/{record['case_id']}: request {key} differs from run metadata")
        if record["configured_context_size"] != inference["configured_context_size"] or record["output_token_budget"] != inference["output_tokens"]:
            raise ContractError(f"{run.name}/{record['case_id']}: context/output settings differ from run metadata")
        if record["error"] is None:
            response = record["output"]["response"] or {}
            response_raw = response.get("choices", [{}])[0].get("message", {}).get("content") or ""
            if response_raw != raw:
                raise ContractError(f"{run.name}/{record['case_id']}: raw output differs from retained response")
            usage = response.get("usage", {})
            if usage.get("prompt_tokens") != record["actual_input_tokens"]:
                raise ContractError(f"{run.name}/{record['case_id']}: API prompt-token count mismatch")
        if record["truncated"]:
            raise ContractError(f"{run.name}/{record['case_id']}: truncated result is invalid")
    recomputed = summarize(
        metadata["run_id"],
        records,
        metadata["selection"]["context_levels"],
        metadata["selection"]["case_ids"],
        metadata["selection"]["complete_definition_coverage"],
    )
    if summary != recomputed:
        raise ContractError(f"{run.name}: stored summary is not reproducible")
    return summary


def built_case_dict(value: BuiltCase) -> dict[str, Any]:
    return asdict(value)
