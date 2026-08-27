#!/usr/bin/env python3
"""Deterministic scientific contracts for ECC-003."""
from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
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
ECC002_SCRIPTS = ROOT.parent / "ecc-002-confusable-context-retrieval" / "scripts"
sys.path.insert(0, str(ECC002_SCRIPTS))
import ecc002


class ContractError(RuntimeError):
    """Raised when the frozen experiment or retained evidence is inconsistent."""


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
        digest.update(label.encode())
        digest.update(b"\0")
        digest.update(canonical_json(value))
    return digest.hexdigest()


def definition_fingerprint() -> str:
    return fingerprint_values(load_json(DEFINITION / "experiment.json"), load_json(DEFINITION / "cases.json"))


def schema_errors(value: Any, schema_name: str) -> list[str]:
    return [error.message for error in Draft202012Validator(load_json(SCHEMAS / schema_name)).iter_errors(value)]


def positions(definition: dict[str, Any]) -> list[dict[str, Any]]:
    return definition["independent_variables"]["evidence_position"]["levels"]


def position_spec(definition: dict[str, Any], position: str) -> dict[str, Any]:
    return next(item for item in positions(definition) if item["id"] == position)


def load_definition() -> tuple[dict[str, Any], list[dict[str, str]]]:
    definition = load_json(DEFINITION / "experiment.json")
    inventory = load_json(DEFINITION / "cases.json")
    errors = schema_errors(definition, "experiment-definition.schema.json")
    cases = inventory.get("cases", [])
    if errors:
        raise ContractError(f"invalid experiment definition: {errors[0]}")
    if inventory.get("version") != 1 or len(cases) != definition["case_generation"]["semantic_cases"]:
        raise ContractError("case inventory version/count does not match the definition")
    for field in ("id", "generator_case_id", "entity", "answer"):
        if len({case[field] for case in cases}) != len(cases):
            raise ContractError(f"case {field} values must be unique")
    levels = definition["independent_variables"]["requested_input_tokens"]["levels"]
    if levels != sorted(levels) or len(levels) != len(set(levels)):
        raise ContractError("context levels must be unique and ascending")
    if [item["id"] for item in positions(definition)] != ["early", "middle", "late"]:
        raise ContractError("evidence positions must be frozen as early/middle/late")
    return definition, cases


def generator_case(case: dict[str, str]) -> dict[str, str]:
    return {**case, "id": case["generator_case_id"]}


def record(entity: str, answer: str) -> str:
    return ecc002.record(entity, answer)


def relevant_fact(case: dict[str, str]) -> str:
    return record(case["entity"], case["answer"])


def question(case: dict[str, str]) -> str:
    return ecc002.question(case)


def distractor(case: dict[str, str], index: int, side: str, seed: int) -> str:
    return ecc002.distractor(generator_case(case), index, side, seed)


def distractor_values(case: dict[str, str], index: int, side: str, seed: int) -> tuple[str, str]:
    return ecc002.distractor_values(generator_case(case), index, side, seed)


def allocation(pairs: int, position: str) -> tuple[int, int]:
    """Allocate the same 2*pairs records around the target without a marker."""
    total = 2 * pairs
    if position == "middle":
        return pairs, pairs
    target = 0.1 if position == "early" else 0.9
    # The header and target record are material at short contexts.  Bias the
    # discrete allocation toward the boundary so model-token measurement can
    # remain within the frozen tolerance without changing task content.
    raw = target * (total + 1) - 0.5
    before = math.floor(raw) if position == "early" else math.ceil(raw)
    before = max(0, min(total, before))
    return before, total - before


def distractor_metadata(case: dict[str, str], pairs: int, position: str, seed: int) -> list[dict[str, Any]]:
    before, after = allocation(pairs, position)
    total_records = before + after + 1
    records: list[dict[str, Any]] = []
    for index in range(1, before + 1):
        entity, answer = distractor_values(case, index, "A", seed)
        ordinal = index - 1
        records.append({"entity": entity, "answer": answer, "side": "before", "record_ordinal": ordinal, "relative_record_position": round(ordinal / max(total_records - 1, 1), 6), "distance_from_target_records": before - index + 1})
    for index in range(1, after + 1):
        entity, answer = distractor_values(case, index, "B", seed)
        ordinal = before + index
        records.append({"entity": entity, "answer": answer, "side": "after", "record_ordinal": ordinal, "relative_record_position": round(ordinal / max(total_records - 1, 1), 6), "distance_from_target_records": index})
    return records


def compose(case: dict[str, str], pairs: int, position: str, seed: int) -> tuple[str, str, str, list[dict[str, Any]]]:
    before, after = allocation(pairs, position)
    before_lines = [distractor(case, index, "A", seed) for index in range(1, before + 1)]
    after_lines = [distractor(case, index, "B", seed) for index in range(1, after + 1)]
    prefix = "Registry entries:\n" + ("\n".join(before_lines) + "\n" if before_lines else "")
    context = prefix + relevant_fact(case) + ("\n" + "\n".join(after_lines) if after_lines else "")
    metadata = distractor_metadata(case, pairs, position, seed)
    validate_record_set(case, context, pairs, position, seed, metadata)
    return context, context + "\n\nQuestion:\n" + question(case), prefix, metadata


def validate_record_set(case: dict[str, str], context: str, pairs: int, position: str, seed: int, metadata: list[dict[str, Any]]) -> None:
    lines = context.splitlines()
    before, after = allocation(pairs, position)
    records = lines[1:]
    target = relevant_fact(case)
    if not lines or lines[0] != "Registry entries:" or len(records) != before + after + 1:
        raise ContractError("registry context construction is invalid")
    if len(records) != len(set(records)) or records.count(target) != 1:
        raise ContractError("target and distractor records must be unique")
    if context.count(case["entity"]) != 1 or context.count(case["answer"]) != 1:
        raise ContractError("target entity/answer leakage violates the definition")
    expected = [distractor(case, index, "A", seed) for index in range(1, before + 1)] + [target] + [distractor(case, index, "B", seed) for index in range(1, after + 1)]
    if records != expected or len(metadata) != before + after:
        raise ContractError("context does not match deterministic position generator")
    if any("TARGET" in line.upper() for line in records):
        raise ContractError("target marker is forbidden")
    for line in records:
        if not line.startswith("Registry entry: Project ") or " has access code " not in line or not line.endswith("."):
            raise ContractError("target/distractor template differs")


class TokenRuntime(Protocol):
    def count_text(self, text: str) -> int: ...
    def count_prompt(self, content: str) -> int: ...


@dataclass(frozen=True)
class BuiltCase:
    case_id: str
    requested_input_tokens: int
    requested_evidence_position: str
    actual_input_tokens: int
    content_tokens: int
    prompt_overhead_tokens: int
    context_tokens: int
    evidence_start_token: int
    evidence_position_ratio: float
    distractor_pairs: int
    distractors_before: int
    distractors_after: int
    relevant_fact: str
    expected_answer: str
    distractor_records: list[dict[str, Any]]
    context_sha256: str
    content: str


def build_case(runtime: TokenRuntime, case: dict[str, str], target: int, position: str, definition: dict[str, Any]) -> BuiltCase:
    seed = definition["case_generation"]["seed"]
    output_tokens = definition["token_budget"]["output_tokens"]
    configured = definition["token_budget"]["configured_context_size"]

    def prompt_tokens(pairs: int) -> int:
        return runtime.count_prompt(compose(case, pairs, position, seed)[1])

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
    expected_ratio = position_spec(definition, position)["target_ratio"]
    tolerance = definition["independent_variables"]["evidence_position"]["allowed_absolute_error"]
    maximum_shortfall = definition["token_budget"]["maximum_target_shortfall_tokens"]
    selected: tuple[int, str, str, str, list[dict[str, Any]], int, int, int, float] | None = None
    for candidate in range(low, -1, -1):
        context, content, prefix, metadata = compose(case, candidate, position, seed)
        actual = runtime.count_prompt(content)
        shortfall = target - actual
        if shortfall > maximum_shortfall:
            break
        context_tokens = runtime.count_text(context)
        evidence_start = runtime.count_text(prefix)
        ratio = evidence_start / context_tokens
        if shortfall >= 0 and abs(ratio - expected_ratio) <= tolerance:
            selected = (candidate, context, content, prefix, metadata, actual, context_tokens, evidence_start, ratio)
            break
    if selected is None:
        raise ContractError(f"{case['id']} target {target}/{position}: no valid token/position construction")
    low, context, content, prefix, metadata, actual, context_tokens, evidence_start, ratio = selected
    before, after = allocation(low, position)
    content_tokens = runtime.count_text(content)
    if actual + output_tokens > configured:
        raise ContractError(f"{case['id']} target {target}: {actual}+{output_tokens} exceeds context {configured}")
    return BuiltCase(case["id"], target, position, actual, content_tokens, actual - content_tokens, context_tokens, evidence_start, round(ratio, 6), low, before, after, relevant_fact(case), case["answer"], metadata, hashlib.sha256(content.encode()).hexdigest(), content)


ServerClient = ecc002.ServerClient


def classify_failure(case: dict[str, str], raw: str, pairs: int, position: str, definition: dict[str, Any]) -> dict[str, Any] | None:
    passed, normalized = ecc002.evaluate(case["answer"], raw)
    if passed:
        return None
    for item in distractor_metadata(case, pairs, position, definition["case_generation"]["seed"]):
        if normalized == ecc002.normalize_answer(item["answer"]):
            return {"kind": "distractor_code", "selected_distractor": item}
    return {"kind": "other_output"}


def threshold_ecc(levels: list[dict[str, Any]], threshold: float) -> int | None:
    result = None
    for level in levels:
        if level["relative_accuracy"] is None or level["relative_accuracy"] < threshold:
            break
        result = level["requested_input_tokens"]
    return result


def _level_rows(records: list[dict[str, Any]], selected_levels: list[int], position: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for level in selected_levels:
        values = [item for item in records if item["requested_input_tokens"] == level and item["requested_evidence_position"] == position and not item["error"] and not item["truncated"]]
        times = [item["timing"]["total_ms"] for item in values]
        accuracy = sum(item["evaluation"]["passed"] for item in values) / len(values) if values else None
        rows.append({"requested_input_tokens": level, "cases": len(values), "passed": sum(item["evaluation"]["passed"] for item in values), "accuracy": accuracy, "relative_accuracy": None, "actual_input_tokens_min": min((item["actual_input_tokens"] for item in values), default=None), "actual_input_tokens_max": max((item["actual_input_tokens"] for item in values), default=None), "runtime": {"count": len(times), "median_total_ms": statistics.median(times) if times else None, "min_total_ms": min(times) if times else None, "max_total_ms": max(times) if times else None}})
    return rows


def failure_analysis(records: list[dict[str, Any]], definition: dict[str, Any]) -> dict[str, Any]:
    failures = [item for item in records if not item["error"] and not item["truncated"] and not item["evaluation"]["passed"]]
    distractors = [item for item in failures if item["failure"] and item["failure"]["kind"] == "distractor_code"]
    nearby = definition["failure_analysis"]["nearby_distance_records"]
    level_counts: dict[str, set[int]] = {}
    position_counts: dict[str, set[str]] = {}
    for item in failures:
        level_counts.setdefault(item["case_id"], set()).add(item["requested_input_tokens"])
        position_counts.setdefault(item["case_id"], set()).add(item["requested_evidence_position"])
    return {"total_failures": len(failures), "distractor_code_failures": len(distractors), "other_output_failures": len(failures) - len(distractors), "selected_distractor_sides": {"before": sum(item["failure"]["selected_distractor"]["side"] == "before" for item in distractors), "after": sum(item["failure"]["selected_distractor"]["side"] == "after" for item in distractors)}, "nearby_distractor_selections": sum(item["failure"]["selected_distractor"]["distance_from_target_records"] <= nearby for item in distractors), "repeated_case_ids_across_levels": sorted(case_id for case_id, levels in level_counts.items() if len(levels) > 1), "repeated_case_ids_across_positions": sorted(case_id for case_id, values in position_counts.items() if len(values) > 1)}


def summarize(run_id: str, records: list[dict[str, Any]], selected_levels: list[int], selected_positions: list[str], selected_case_ids: list[str], complete_definition_coverage: bool, definition: dict[str, Any]) -> dict[str, Any]:
    invalid = sum(bool(item["error"]) or item["truncated"] for item in records)
    expected = len(selected_levels) * len(selected_positions) * len(selected_case_ids)
    complete = complete_definition_coverage and len(records) == expected and invalid == 0
    position_rows: list[dict[str, Any]] = []
    for position in selected_positions:
        levels = _level_rows(records, selected_levels, position)
        baseline = levels[0]["accuracy"] if levels else None
        if baseline:
            for row in levels:
                row["relative_accuracy"] = row["accuracy"] / baseline if row["accuracy"] is not None else None
        resolved = complete and baseline is not None and baseline > 0
        values = {name: threshold_ecc(levels, threshold) if resolved else None for name, threshold in (("ECC95", 0.95), ("ECC90", 0.9), ("ECC80", 0.8))}
        censored = [name for name, value in values.items() if resolved and value == selected_levels[-1]]
        position_rows.append({"position": position, "baseline_context_level": selected_levels[0] if selected_levels else None, "baseline_accuracy": baseline, "levels": levels, "ecc": {**values, "status": "unresolved" if not resolved else ("right_censored" if censored else "resolved"), "right_censored_thresholds": censored, "rule": "contiguous tested prefix; no interpolation"}, "non_monotonic": any(later > earlier for earlier, later in pairwise([row["accuracy"] for row in levels if row["accuracy"] is not None]))})
    metrics: list[dict[str, Any]] = []
    for level in selected_levels:
        accuracy = {position["position"]: next(row for row in position["levels"] if row["requested_input_tokens"] == level)["accuracy"] for position in position_rows}
        values = [value for value in accuracy.values() if value is not None]
        penalty = None if any(accuracy.get(key) is None for key in ("early", "middle", "late")) else ((accuracy["early"] + accuracy["late"]) / 2 - accuracy["middle"])
        metrics.append({"requested_input_tokens": level, "accuracy_by_position": accuracy, "position_gap": max(values) - min(values) if len(values) == len(selected_positions) else None, "middle_penalty": penalty})
    timings = [item["timing"]["total_ms"] for item in records if not item["error"]]
    runtime_rows = [{"requested_input_tokens": level, "position": position["position"], **next(row for row in position["levels"] if row["requested_input_tokens"] == level)["runtime"]} for level in selected_levels for position in position_rows]
    return {"run_id": run_id, "run_status": "valid" if complete else "invalid", "coverage": {"complete": complete, "expected_results": expected, "observed_results": len(records)}, "total_results": len(records), "invalid_results": invalid, "positions": position_rows, "position_metrics": metrics, "failure_analysis": failure_analysis(records, definition), "capability": {"interpretation": "direct-context confusable retrieval accuracy only"}, "runtime": {"median_total_ms": statistics.median(timings) if timings else None, "by_context_position": runtime_rows}}


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
    all_levels = definition["independent_variables"]["requested_input_tokens"]["levels"]
    all_positions = [item["id"] for item in positions(definition)]
    all_cases = [case["id"] for case in cases]
    selection_complete = selection["context_levels"] == all_levels and selection["evidence_positions"] == all_positions and selection["case_ids"] == all_cases
    if selection["complete_definition_coverage"] != selection_complete:
        raise ContractError(f"{run.name}: complete-coverage flag does not match the definition")
    if selection_complete and metadata["repository"]["dirty"]:
        raise ContractError(f"{run.name}: complete run was produced from a dirty worktree")
    expected = {(case_id, level, position) for case_id in selection["case_ids"] for level in selection["context_levels"] for position in selection["evidence_positions"]}
    observed = [(item["case_id"], item["requested_input_tokens"], item["requested_evidence_position"]) for item in records]
    if len(observed) != len(set(observed)) or set(observed) != expected:
        raise ContractError(f"{run.name}: result coverage has duplicates or differs from selection")
    lookup = {case["id"]: case for case in cases}
    for item in records:
        errors = schema_errors(item, "case-result.schema.json")
        if errors:
            raise ContractError(f"{run.name}/{item.get('case_id', '?')}: {errors[0]}")
        case = lookup[item["case_id"]]
        _context, expected_content, _prefix, expected_metadata = compose(case, item["distractor_pairs"], item["requested_evidence_position"], definition["case_generation"]["seed"])
        if item["request"]["messages"][0]["content"] != expected_content or item["relevant_fact"] != relevant_fact(case) or item["expected_answer"] != case["answer"] or item["distractor_records"] != expected_metadata:
            raise ContractError(f"{run.name}/{item['case_id']}: stored generator output is inconsistent")
        before, after = allocation(item["distractor_pairs"], item["requested_evidence_position"])
        if (item["distractors_before"], item["distractors_after"]) != (before, after):
            raise ContractError(f"{run.name}/{item['case_id']}: distractor allocation is inconsistent")
        content = item["request"]["messages"][0]["content"]
        if hashlib.sha256(content.encode()).hexdigest() != item["context_sha256"]:
            raise ContractError(f"{run.name}/{item['case_id']}: request hash mismatch")
        passed, normalized = ecc002.evaluate(case["answer"], item["output"]["raw_text"])
        expected_failure = None if item["error"] else classify_failure(case, item["output"]["raw_text"], item["distractor_pairs"], item["requested_evidence_position"], definition)
        if item["output"]["normalized_text"] != normalized or item["evaluation"] != {"passed": passed, "score": float(passed)} or item["failure"] != expected_failure:
            raise ContractError(f"{run.name}/{item['case_id']}: evaluation or failure analysis is inconsistent")
        if item["actual_input_tokens"] + item["output_token_budget"] > item["configured_context_size"] or item["truncated"]:
            raise ContractError(f"{run.name}/{item['case_id']}: invalid overflow/truncation marked as evidence")
        shortfall = item["requested_input_tokens"] - item["actual_input_tokens"]
        if shortfall < 0 or shortfall > definition["token_budget"]["maximum_target_shortfall_tokens"] or item["content_tokens"] + item["prompt_overhead_tokens"] != item["actual_input_tokens"]:
            raise ContractError(f"{run.name}/{item['case_id']}: token construction is inconsistent")
        ratio = round(item["evidence_start_token"] / item["context_tokens"], 6)
        expected_ratio = position_spec(definition, item["requested_evidence_position"])["target_ratio"]
        if ratio != item["evidence_position_ratio"] or abs(ratio - expected_ratio) > definition["independent_variables"]["evidence_position"]["allowed_absolute_error"]:
            raise ContractError(f"{run.name}/{item['case_id']}: evidence position violates definition")
        inference = metadata["inference"]
        for key, value in {"temperature": inference["temperature"], "seed": inference["seed"], "max_tokens": inference["output_tokens"], "chat_template_kwargs": inference["chat_template_kwargs"]}.items():
            if item["request"][key] != value:
                raise ContractError(f"{run.name}/{item['case_id']}: request {key} differs from metadata")
        if item["configured_context_size"] != inference["configured_context_size"] or item["output_token_budget"] != inference["output_tokens"]:
            raise ContractError(f"{run.name}/{item['case_id']}: context settings differ from metadata")
        if item["error"] is None:
            response = item["output"]["response"] or {}
            raw = response.get("choices", [{}])[0].get("message", {}).get("content") or ""
            if raw != item["output"]["raw_text"] or response.get("usage", {}).get("prompt_tokens") != item["actual_input_tokens"]:
                raise ContractError(f"{run.name}/{item['case_id']}: retained response is inconsistent")
    recomputed = summarize(metadata["run_id"], records, selection["context_levels"], selection["evidence_positions"], selection["case_ids"], selection["complete_definition_coverage"], definition)
    if summary != recomputed:
        raise ContractError(f"{run.name}: stored summary is not reproducible")
    return summary


def built_case_dict(value: BuiltCase) -> dict[str, Any]:
    return asdict(value)
