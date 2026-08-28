#!/usr/bin/env python3
"""Deterministic scientific contracts for ECC-002."""
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
    """Raised when scientific or retained-evidence contracts are violated."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical_json(value: Any) -> bytes:
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
    if errors:
        raise ContractError(f"invalid experiment definition: {errors[0]}")
    if inventory.get("version") != 1 or len(cases) != definition["case_generation"]["semantic_cases"]:
        raise ContractError("case inventory version/count does not match experiment definition")
    if len({case["id"] for case in cases}) != len(cases):
        raise ContractError("case IDs must be unique")
    if len({case["entity"] for case in cases}) != len(cases) or len({case["answer"] for case in cases}) != len(cases):
        raise ContractError("target entities and answers must be unique")
    levels = definition["independent_variable"]["levels"]
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


_VOWELS = ("a", "e", "i", "o", "u")
_TAILS = ("n", "r", "s", "v", "x")


def record(entity: str, answer: str) -> str:
    """The sole semantic record template for both target and distractors."""
    return f"Registry entry: Project {entity} has access code {answer}."


def distractor_values(case: dict[str, str], pair_index: int, side: str, seed: int) -> tuple[str, str]:
    """Return a deterministic, confusable entity/code pair without target leakage."""
    if pair_index < 1 or side not in {"A", "B"}:
        raise ContractError("distractor pair index/side is invalid")
    serial = pair_index * 2 + (0 if side == "A" else 1)
    if serial >= 8000:
        raise ContractError("distractor sequence exceeds the frozen four-digit uniqueness range")
    digest = hashlib.sha256(f"{seed}:{case['id']}:{pair_index}:{side}".encode()).digest()
    stem = case["entity"].split("-", maxsplit=1)[0][:3]
    entity = f"{stem}{_VOWELS[digest[0] % len(_VOWELS)]}{_TAILS[digest[1] % len(_TAILS)]}-{2000 + serial:04d}"
    prefix = case["answer"].split("-", maxsplit=1)[0]
    answer = f"{prefix}-{serial:04d}"
    if entity == case["entity"] or answer == case["answer"]:
        raise ContractError("distractor collides with target")
    return entity, answer


def distractor(case: dict[str, str], pair_index: int, side: str, seed: int) -> str:
    entity, answer = distractor_values(case, pair_index, side, seed)
    return record(entity, answer)


def relevant_fact(case: dict[str, str]) -> str:
    return record(case["entity"], case["answer"])


def question(case: dict[str, str]) -> str:
    return f"What is the access code for Project {case['entity']}? Return only the access code."


def compose(case: dict[str, str], pairs: int, seed: int) -> tuple[str, str, str]:
    before = [distractor(case, index, "A", seed) for index in range(1, pairs + 1)]
    after = [distractor(case, index, "B", seed) for index in range(1, pairs + 1)]
    before_text = "\n".join(before)
    after_text = "\n".join(after)
    prefix = "Registry entries:\n" + (before_text + "\n" if before_text else "")
    context = prefix + relevant_fact(case) + ("\n" + after_text if after_text else "")
    validate_record_set(case, context, pairs, seed)
    return context, context + "\n\nQuestion:\n" + question(case), prefix


def validate_record_set(case: dict[str, str], context: str, pairs: int, seed: int) -> None:
    """Prove the generated context contains only one unmarked, ordinary target record."""
    lines = context.splitlines()
    if not lines or lines[0] != "Registry entries:":
        raise ContractError("registry context header is invalid")
    records = lines[1:]
    expected = 2 * pairs + 1
    if len(records) != expected or len(records) != len(set(records)):
        raise ContractError("registry records must be present and unique")
    target = relevant_fact(case)
    if records.count(target) != 1 or records.count(case["entity"]) != 0:
        raise ContractError("target record/entity occurrence is invalid")
    if context.count(case["answer"]) != 1 or context.count(case["entity"]) != 1:
        raise ContractError("target answer/entity must occur exactly once")
    generated = [distractor(case, index, side, seed) for index in range(1, pairs + 1) for side in ("A", "B")]
    if set(records) != {target, *generated}:
        raise ContractError("registry record sequence does not match deterministic generator")
    for line in records:
        match = re.fullmatch(r"Registry entry: Project ([A-Za-z]+-[0-9]{4}) has access code ([A-Z]{2}-[0-9]{4})\.", line)
        if not match or record(match.group(1), match.group(2)) != line:
            raise ContractError("target and distractors must share the frozen record template")
    if any("TARGET" in line.upper() for line in records):
        raise ContractError("target marker is forbidden")


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
    if shortfall < 0 or shortfall > definition["token_budget"]["maximum_target_shortfall_tokens"]:
        raise ContractError(f"{case['id']} target {target}: token shortfall {shortfall} exceeds the definition")
    if abs(ratio - definition["evidence_position"]["target_ratio"]) > definition["evidence_position"]["allowed_absolute_error"]:
        raise ContractError(f"{case['id']} target {target}: evidence ratio {ratio:.4f} violates midpoint policy")
    if actual + output_tokens > configured:
        raise ContractError(f"{case['id']} target {target}: {actual}+{output_tokens} exceeds context {configured}")
    return BuiltCase(case["id"], target, actual, content_tokens, actual - content_tokens, context_tokens, evidence_start, round(ratio, 6), low, relevant_fact(case), case["answer"], hashlib.sha256(content.encode("utf-8")).hexdigest(), content)


class ServerClient:
    def __init__(self, base_url: str, chat_template_kwargs: dict[str, Any]):
        self.base_url = base_url.rstrip("/")
        self.chat_template_kwargs = chat_template_kwargs

    def post(self, path: str, payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
        request = urllib.request.Request(self.base_url + path, json.dumps(payload).encode("utf-8"), {"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def count_text(self, text: str) -> int:
        return len(self.post("/tokenize", {"content": text, "add_special": False})["tokens"])

    def count_prompt(self, content: str) -> int:
        template = self.post("/apply-template", {"messages": [{"role": "user", "content": content}], "add_generation_prompt": True, "chat_template_kwargs": self.chat_template_kwargs})["prompt"]
        return len(self.post("/tokenize", {"content": template, "add_special": True})["tokens"])

    def complete(self, content: str, inference: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = {"messages": [{"role": "user", "content": content}], "temperature": inference["temperature"], "seed": inference["seed"], "max_tokens": inference["output_tokens"], "chat_template_kwargs": self.chat_template_kwargs}
        return payload, self.post("/v1/chat/completions", payload)


def threshold_ecc(levels: list[dict[str, Any]], threshold: float) -> int | None:
    result = None
    for level in levels:
        if level["relative_accuracy"] is None or level["relative_accuracy"] < threshold:
            break
        result = level["requested_input_tokens"]
    return result


def summarize(run_id: str, records: list[dict[str, Any]], selected_levels: list[int], selected_case_ids: list[str], complete_definition_coverage: bool) -> dict[str, Any]:
    invalid = sum(bool(row["error"]) or row["truncated"] for row in records)
    expected = len(selected_levels) * len(selected_case_ids)
    complete = complete_definition_coverage and len(records) == expected and invalid == 0
    levels: list[dict[str, Any]] = []
    for level in selected_levels:
        rows = [row for row in records if row["requested_input_tokens"] == level and not row["error"] and not row["truncated"]]
        timings = [row["timing"]["total_ms"] for row in rows]
        accuracy = sum(row["evaluation"]["passed"] for row in rows) / len(rows) if rows else None
        levels.append({"requested_input_tokens": level, "cases": len(rows), "passed": sum(row["evaluation"]["passed"] for row in rows), "accuracy": accuracy, "relative_accuracy": None, "actual_input_tokens_min": min((row["actual_input_tokens"] for row in rows), default=None), "actual_input_tokens_max": max((row["actual_input_tokens"] for row in rows), default=None), "runtime": {"count": len(timings), "median_total_ms": statistics.median(timings) if timings else None, "min_total_ms": min(timings) if timings else None, "max_total_ms": max(timings) if timings else None}})
    baseline = levels[0]["accuracy"] if levels else None
    if baseline:
        for row in levels:
            row["relative_accuracy"] = row["accuracy"] / baseline if row["accuracy"] is not None else None
    resolved = complete and baseline is not None and baseline > 0
    thresholds = {"ECC95": 0.95, "ECC90": 0.90, "ECC80": 0.80}
    ecc_values = {name: threshold_ecc(levels, threshold) if resolved else None for name, threshold in thresholds.items()}
    right_censored = [name for name, value in ecc_values.items() if resolved and value == selected_levels[-1]]
    timings = [row["timing"]["total_ms"] for row in records if not row["error"]]
    return {"run_id": run_id, "run_status": "valid" if complete else "invalid", "coverage": {"complete": complete, "expected_results": expected, "observed_results": len(records)}, "total_results": len(records), "invalid_results": invalid, "baseline_context_level": selected_levels[0] if selected_levels else None, "baseline_accuracy": baseline, "levels": levels, "ecc": {**ecc_values, "status": "unresolved" if not resolved else ("right_censored" if right_censored else "resolved"), "right_censored_thresholds": right_censored, "rule": "contiguous tested prefix; no interpolation"}, "non_monotonic": any(later > earlier for earlier, later in pairwise([row["accuracy"] for row in levels if row["accuracy"] is not None])), "capability": {"interpretation": "direct-context confusable retrieval accuracy only"}, "runtime": {"median_total_ms": statistics.median(timings) if timings else None, "per_context_level": [{"requested_input_tokens": row["requested_input_tokens"], **row["runtime"]} for row in levels]}}


def validate_run(run: Path) -> dict[str, Any]:
    definition, cases = load_definition()
    metadata, summary = load_json(run / "metadata.json"), load_json(run / "summary.json")
    records = [json.loads(line) for line in (run / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    for value, schema, label in ((metadata, "run-metadata.schema.json", "metadata"), (summary, "run-summary.schema.json", "summary")):
        errors = schema_errors(value, schema)
        if errors:
            raise ContractError(f"{run.name}/{label}: {errors[0]}")
    if metadata["definition_fingerprint"] != definition_fingerprint():
        raise ContractError(f"{run.name}: definition fingerprint mismatch")
    selection = metadata["selection"]
    all_levels, all_cases = definition["independent_variable"]["levels"], [case["id"] for case in cases]
    selection_complete = selection["context_levels"] == all_levels and selection["case_ids"] == all_cases
    if selection["complete_definition_coverage"] != selection_complete:
        raise ContractError(f"{run.name}: complete-coverage flag does not match the definition")
    if selection_complete and metadata["repository"]["dirty"]:
        raise ContractError(f"{run.name}: complete run was produced from a dirty worktree")
    expected = {(case_id, level) for case_id in selection["case_ids"] for level in selection["context_levels"]}
    observed = [(row["case_id"], row["requested_input_tokens"]) for row in records]
    if len(observed) != len(set(observed)):
        raise ContractError(f"{run.name}: duplicate case/context result")
    if set(observed) != expected:
        raise ContractError(f"{run.name}: result coverage differs from metadata selection")
    lookup = {case["id"]: case for case in cases}
    for row in records:
        errors = schema_errors(row, "case-result.schema.json")
        if errors:
            raise ContractError(f"{run.name}/{row.get('case_id', '?')}: {errors[0]}")
        case = lookup[row["case_id"]]
        content = row["request"]["messages"][0]["content"]
        _expected_context, expected_content, _ = compose(case, row["distractor_pairs"], definition["case_generation"]["seed"])
        if content != expected_content or row["relevant_fact"] != relevant_fact(case) or row["expected_answer"] != case["answer"]:
            raise ContractError(f"{run.name}/{row['case_id']}: stored task content is not the frozen generator output")
        if hashlib.sha256(content.encode("utf-8")).hexdigest() != row["context_sha256"]:
            raise ContractError(f"{run.name}/{row['case_id']}: request hash mismatch")
        passed, normalized = evaluate(case["answer"], row["output"]["raw_text"])
        if row["output"]["normalized_text"] != normalized or row["evaluation"] != {"passed": passed, "score": float(passed)}:
            raise ContractError(f"{run.name}/{row['case_id']}: stored evaluation is incorrect")
        if row["actual_input_tokens"] + row["output_token_budget"] > row["configured_context_size"] or row["truncated"]:
            raise ContractError(f"{run.name}/{row['case_id']}: invalid context overflow or truncation marked as evidence")
        shortfall = row["requested_input_tokens"] - row["actual_input_tokens"]
        if shortfall < 0 or shortfall > definition["token_budget"]["maximum_target_shortfall_tokens"]:
            raise ContractError(f"{run.name}/{row['case_id']}: token target shortfall violates the definition")
        if row["content_tokens"] + row["prompt_overhead_tokens"] != row["actual_input_tokens"]:
            raise ContractError(f"{run.name}/{row['case_id']}: token accounting is inconsistent")
        ratio = round(row["evidence_start_token"] / row["context_tokens"], 6)
        if ratio != row["evidence_position_ratio"] or abs(ratio - definition["evidence_position"]["target_ratio"]) > definition["evidence_position"]["allowed_absolute_error"]:
            raise ContractError(f"{run.name}/{row['case_id']}: evidence position violates the definition")
        inference = metadata["inference"]
        for key, expected_value in {"temperature": inference["temperature"], "seed": inference["seed"], "max_tokens": inference["output_tokens"], "chat_template_kwargs": inference["chat_template_kwargs"]}.items():
            if row["request"][key] != expected_value:
                raise ContractError(f"{run.name}/{row['case_id']}: request {key} differs from run metadata")
        if row["configured_context_size"] != inference["configured_context_size"] or row["output_token_budget"] != inference["output_tokens"]:
            raise ContractError(f"{run.name}/{row['case_id']}: context/output settings differ from run metadata")
        if row["error"] is None:
            response = row["output"]["response"] or {}
            response_raw = response.get("choices", [{}])[0].get("message", {}).get("content") or ""
            if response_raw != row["output"]["raw_text"] or response.get("usage", {}).get("prompt_tokens") != row["actual_input_tokens"]:
                raise ContractError(f"{run.name}/{row['case_id']}: retained response is inconsistent")
    recomputed = summarize(metadata["run_id"], records, selection["context_levels"], selection["case_ids"], selection["complete_definition_coverage"])
    if summary != recomputed:
        raise ContractError(f"{run.name}: stored summary is not reproducible")
    return summary


def built_case_dict(value: BuiltCase) -> dict[str, Any]:
    return asdict(value)
