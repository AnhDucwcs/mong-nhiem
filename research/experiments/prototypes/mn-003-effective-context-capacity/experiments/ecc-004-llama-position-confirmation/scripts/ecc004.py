#!/usr/bin/env python3
"""Deterministic scientific contracts for the Llama-only ECC-004 confirmation."""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEFINITION = ROOT / "definition"
SCHEMAS = ROOT / "schemas"
CONFIGS = ROOT / "configs"
RUNS = ROOT / "runs"
ECC003_SCRIPTS = ROOT.parent / "ecc-003-evidence-position-sensitivity" / "scripts"
sys.path.insert(0, str(ECC003_SCRIPTS))
import ecc003

ecc002 = ecc003.ecc002
ContractError = ecc003.ContractError
TokenRuntime = ecc003.TokenRuntime
BuiltCase = ecc003.BuiltCase
ServerClient = ecc003.ServerClient


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


def _historical_targets() -> tuple[set[str], set[str]]:
    historical_cases = load_json(ecc002.DEFINITION / "cases.json")["cases"] + load_json(ecc003.DEFINITION / "cases.json")["cases"]
    return {case["entity"] for case in historical_cases}, {case["answer"] for case in historical_cases}


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
    if any(case["id"] != case["generator_case_id"] for case in cases):
        raise ContractError("fresh ECC-004 generator IDs must equal case IDs")
    historical_entities, historical_answers = _historical_targets()
    if {case["entity"] for case in cases} & historical_entities or {case["answer"] for case in cases} & historical_answers:
        raise ContractError("ECC-004 target inventory overlaps historical ECC-002/ECC-003 targets")
    levels = definition["independent_variables"]["requested_input_tokens"]["levels"]
    if levels != [8192, 16384]:
        raise ContractError("ECC-004 context levels must be the frozen 8192/16384 pair")
    if [item["id"] for item in positions(definition)] != ["early", "middle", "late"]:
        raise ContractError("evidence positions must be frozen as early/middle/late")
    return definition, cases


def compose(case: dict[str, str], pairs: int, position: str, seed: int) -> tuple[str, str, str, list[dict[str, Any]]]:
    return ecc003.compose(case, pairs, position, seed)


def allocation(pairs: int, position: str) -> tuple[int, int]:
    return ecc003.allocation(pairs, position)


def relevant_fact(case: dict[str, str]) -> str:
    return ecc003.relevant_fact(case)


def build_case(runtime: TokenRuntime, case: dict[str, str], target: int, position: str, definition: dict[str, Any]) -> BuiltCase:
    return ecc003.build_case(runtime, case, target, position, definition)


def built_case_dict(value: BuiltCase) -> dict[str, Any]:
    return ecc003.built_case_dict(value)


def _contains_expected_code(raw: str, expected: str) -> bool:
    return bool(re.search(rf"(?<![A-Za-z0-9-]){re.escape(expected)}(?![A-Za-z0-9-])", raw, flags=re.IGNORECASE))


def classify_failure(case: dict[str, str], raw: str, pairs: int, position: str, definition: dict[str, Any]) -> dict[str, Any] | None:
    passed, normalized = ecc002.evaluate(case["answer"], raw)
    if passed:
        return None
    if _contains_expected_code(raw, case["answer"]):
        return {"kind": "expected_code_with_extra_text"}
    for item in ecc003.distractor_metadata(case, pairs, position, definition["case_generation"]["seed"]):
        if normalized == ecc002.normalize_answer(item["answer"]):
            return {"kind": "tracked_distractor_code", "selected_distractor": item}
    if re.search(r"\b[A-Za-z]{2}-\d{4}\b", raw):
        return {"kind": "invented_code"}
    if re.search(r"\b(?:[A-Za-z]{1,3}[- ]?\d{1,4}|\d{1,4})\b", raw):
        return {"kind": "partial_or_malformed_code"}
    return {"kind": "other_text"}


def _level_rows(records: list[dict[str, Any]], selected_levels: list[int], position: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for level in selected_levels:
        values = [item for item in records if item["requested_input_tokens"] == level and item["requested_evidence_position"] == position and not item["error"] and not item["truncated"]]
        times = [item["timing"]["total_ms"] for item in values]
        rows.append({"requested_input_tokens": level, "cases": len(values), "passed": sum(item["evaluation"]["passed"] for item in values), "accuracy": sum(item["evaluation"]["passed"] for item in values) / len(values) if values else None, "actual_input_tokens_min": min((item["actual_input_tokens"] for item in values), default=None), "actual_input_tokens_max": max((item["actual_input_tokens"] for item in values), default=None), "runtime": {"count": len(times), "median_total_ms": statistics.median(times) if times else None, "min_total_ms": min(times) if times else None, "max_total_ms": max(times) if times else None}})
    return rows


def paired_transitions(records: list[dict[str, Any]], selected_levels: list[int], selected_case_ids: list[str]) -> list[dict[str, Any]]:
    comparisons = (("early", "middle"), ("early", "late"), ("middle", "late"))
    output: list[dict[str, Any]] = []
    for level in selected_levels:
        by_case: dict[str, dict[str, bool]] = {case_id: {} for case_id in selected_case_ids}
        for item in records:
            if item["requested_input_tokens"] == level and not item["error"] and not item["truncated"]:
                by_case.get(item["case_id"], {})[item["requested_evidence_position"]] = item["evaluation"]["passed"]
        values: dict[str, Any] = {}
        for left, right in comparisons:
            rows = [states for states in by_case.values() if left in states and right in states]
            values[f"{left}_vs_{right}"] = {f"{left}_pass_{right}_fail": sum(states[left] and not states[right] for states in rows), f"{left}_fail_{right}_pass": sum(not states[left] and states[right] for states in rows), "paired_cases": len(rows)}
        output.append({"requested_input_tokens": level, "comparisons": values})
    return output


def failure_analysis(records: list[dict[str, Any]], definition: dict[str, Any]) -> dict[str, Any]:
    failures = [item for item in records if not item["error"] and not item["truncated"] and not item["evaluation"]["passed"]]
    kinds = definition["failure_analysis"]["classes"]
    by_level = {str(level): sum(item["requested_input_tokens"] == level for item in failures) for level in definition["independent_variables"]["requested_input_tokens"]["levels"]}
    by_position = {position["id"]: sum(item["requested_evidence_position"] == position["id"] for item in failures) for position in positions(definition)}
    by_kind = {kind: sum(item["failure"] and item["failure"]["kind"] == kind for item in failures) for kind in kinds}
    level_sets: dict[str, set[int]] = {}
    position_sets: dict[str, set[str]] = {}
    tracked = [item for item in failures if item["failure"] and item["failure"]["kind"] == "tracked_distractor_code"]
    for item in failures:
        level_sets.setdefault(item["case_id"], set()).add(item["requested_input_tokens"])
        position_sets.setdefault(item["case_id"], set()).add(item["requested_evidence_position"])
    nearby = definition["failure_analysis"]["nearby_distance_records"]
    return {"total_failures": len(failures), "by_context_level": by_level, "by_position": by_position, "by_diagnostic_class": by_kind, "tracked_distractor_sides": {"before": sum(item["failure"]["selected_distractor"]["side"] == "before" for item in tracked), "after": sum(item["failure"]["selected_distractor"]["side"] == "after" for item in tracked)}, "nearby_distractor_selections": sum(item["failure"]["selected_distractor"]["distance_from_target_records"] <= nearby for item in tracked), "repeated_failing_case_ids_across_levels": sorted(case_id for case_id, values in level_sets.items() if len(values) > 1), "repeated_failing_case_ids_across_positions": sorted(case_id for case_id, values in position_sets.items() if len(values) > 1)}


def _confirmation(metrics: list[dict[str, Any]], paired: list[dict[str, Any]], complete: bool, definition: dict[str, Any]) -> dict[str, Any]:
    criterion = definition["confirmation_criterion"]
    endpoint = next((item for item in metrics if item["requested_input_tokens"] == 16384), None)
    paired_endpoint = next((item for item in paired if item["requested_input_tokens"] == 16384), None)
    if not complete or endpoint is None or paired_endpoint is None or any(value is None for value in endpoint["accuracy_by_position"].values()):
        return {"status": "unresolved", "criterion": criterion, "unmet_conditions": list(criterion["consistent_with_replication_if"])}
    accuracy = endpoint["accuracy_by_position"]
    transitions = paired_endpoint["comparisons"]["early_vs_late"]
    checks = {"early_greater_than_late": accuracy["early"] > accuracy["late"], "gap_at_least_0_10": endpoint["pairwise_differences"]["early_minus_late"] >= 0.10, "at_least_four_early_pass_late_fail": transitions["early_pass_late_fail"] >= 4, "early_pass_late_fail_outnumbers_reverse": transitions["early_pass_late_fail"] > transitions["early_fail_late_pass"]}
    unmet = [label for label, passed in checks.items() if not passed]
    status = "replicated" if not unmet else ("partially_replicated_or_weakened" if checks["early_greater_than_late"] else "not_replicated")
    return {"status": status, "criterion": criterion, "checks": checks, "unmet_conditions": unmet, "primary_endpoint": {"requested_input_tokens": 16384, "early_minus_late": endpoint["pairwise_differences"]["early_minus_late"], "early_pass_late_fail": transitions["early_pass_late_fail"], "early_fail_late_pass": transitions["early_fail_late_pass"]}}


def summarize(run_id: str, records: list[dict[str, Any]], selected_levels: list[int], selected_positions: list[str], selected_case_ids: list[str], complete_definition_coverage: bool, definition: dict[str, Any]) -> dict[str, Any]:
    invalid = sum(bool(item["error"]) or item["truncated"] for item in records)
    expected = len(selected_levels) * len(selected_positions) * len(selected_case_ids)
    complete = complete_definition_coverage and len(records) == expected and invalid == 0
    position_rows = [{"position": position, "levels": _level_rows(records, selected_levels, position)} for position in selected_positions]
    metrics: list[dict[str, Any]] = []
    for level in selected_levels:
        accuracy = {position["position"]: next(row for row in position["levels"] if row["requested_input_tokens"] == level)["accuracy"] for position in position_rows}
        values = list(accuracy.values())
        metrics.append({"requested_input_tokens": level, "accuracy_by_position": accuracy, "position_gap": max(values) - min(values) if all(value is not None for value in values) else None, "pairwise_differences": {"early_minus_middle": accuracy["early"] - accuracy["middle"] if accuracy.get("early") is not None and accuracy.get("middle") is not None else None, "early_minus_late": accuracy["early"] - accuracy["late"] if accuracy.get("early") is not None and accuracy.get("late") is not None else None, "middle_minus_late": accuracy["middle"] - accuracy["late"] if accuracy.get("middle") is not None and accuracy.get("late") is not None else None}})
    paired = paired_transitions(records, selected_levels, selected_case_ids)
    runtime_rows = [{"requested_input_tokens": level, "position": position["position"], **next(row for row in position["levels"] if row["requested_input_tokens"] == level)["runtime"]} for level in selected_levels for position in position_rows]
    timings = [item["timing"]["total_ms"] for item in records if not item["error"]]
    return {"run_id": run_id, "run_status": "valid" if complete else "invalid", "coverage": {"complete": complete, "expected_results": expected, "observed_results": len(records)}, "total_results": len(records), "invalid_results": invalid, "positions": position_rows, "position_metrics": metrics, "paired_transitions": paired, "failure_analysis": failure_analysis(records, definition), "confirmation": _confirmation(metrics, paired, complete, definition), "capability": {"interpretation": "Llama-only direct-context confusable retrieval confirmation"}, "runtime": {"median_total_ms": statistics.median(timings) if timings else None, "by_context_position": runtime_rows}}


def validate_run(run: Path) -> dict[str, Any]:
    definition, cases = load_definition()
    metadata, summary = load_json(run / "metadata.json"), load_json(run / "summary.json")
    records = [json.loads(line) for line in (run / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    for value, schema, label in ((metadata, "run-metadata.schema.json", "metadata"), (summary, "run-summary.schema.json", "summary")):
        errors = schema_errors(value, schema)
        if errors:
            raise ContractError(f"{run.name}/{label}: {errors[0]}")
    if metadata["definition_fingerprint"] != definition_fingerprint() or metadata["model"]["key"] != "llama-3.2-3b":
        raise ContractError(f"{run.name}: definition fingerprint or Llama-only model scope mismatch")
    selection = metadata["selection"]
    all_levels = definition["independent_variables"]["requested_input_tokens"]["levels"]
    all_positions = [item["id"] for item in positions(definition)]
    all_cases = [case["id"] for case in cases]
    selection_complete = selection["context_levels"] == all_levels and selection["evidence_positions"] == all_positions and selection["case_ids"] == all_cases
    if selection["complete_definition_coverage"] != selection_complete or selection_complete and metadata["repository"]["dirty"]:
        raise ContractError(f"{run.name}: complete selection or clean-worktree contract is inconsistent")
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
        _context, content, _prefix, expected_distractors = compose(case, item["distractor_pairs"], item["requested_evidence_position"], definition["case_generation"]["seed"])
        if item["request"]["messages"][0]["content"] != content or item["relevant_fact"] != relevant_fact(case) or item["expected_answer"] != case["answer"] or item["distractor_records"] != expected_distractors:
            raise ContractError(f"{run.name}/{item['case_id']}: stored generator output is inconsistent")
        before, after = allocation(item["distractor_pairs"], item["requested_evidence_position"])
        if (item["distractors_before"], item["distractors_after"]) != (before, after) or hashlib.sha256(content.encode()).hexdigest() != item["context_sha256"]:
            raise ContractError(f"{run.name}/{item['case_id']}: allocation or request hash is inconsistent")
        passed, normalized = ecc002.evaluate(case["answer"], item["output"]["raw_text"])
        expected_failure = None if item["error"] else classify_failure(case, item["output"]["raw_text"], item["distractor_pairs"], item["requested_evidence_position"], definition)
        if item["output"]["normalized_text"] != normalized or item["evaluation"] != {"passed": passed, "score": float(passed)} or item["failure"] != expected_failure:
            raise ContractError(f"{run.name}/{item['case_id']}: exact evaluation or diagnostic is inconsistent")
        shortfall = item["requested_input_tokens"] - item["actual_input_tokens"]
        expected_ratio = position_spec(definition, item["requested_evidence_position"])["target_ratio"]
        ratio = round(item["evidence_start_token"] / item["context_tokens"], 6)
        if item["truncated"] or item["actual_input_tokens"] + item["output_token_budget"] > item["configured_context_size"] or shortfall < 0 or shortfall > definition["token_budget"]["maximum_target_shortfall_tokens"] or item["content_tokens"] + item["prompt_overhead_tokens"] != item["actual_input_tokens"] or ratio != item["evidence_position_ratio"] or abs(ratio - expected_ratio) > definition["independent_variables"]["evidence_position"]["allowed_absolute_error"]:
            raise ContractError(f"{run.name}/{item['case_id']}: token, position, overflow, or truncation contract is inconsistent")
        inference = metadata["inference"]
        for key, value in {"temperature": inference["temperature"], "seed": inference["seed"], "max_tokens": inference["output_tokens"], "chat_template_kwargs": inference["chat_template_kwargs"]}.items():
            if item["request"][key] != value:
                raise ContractError(f"{run.name}/{item['case_id']}: request {key} differs from metadata")
        if item["configured_context_size"] != inference["configured_context_size"] or item["output_token_budget"] != inference["output_tokens"]:
            raise ContractError(f"{run.name}/{item['case_id']}: context settings differ from metadata")
        if item["error"] is None:
            response = item["output"]["response"] or {}
            if response.get("choices", [{}])[0].get("message", {}).get("content") != item["output"]["raw_text"] or response.get("usage", {}).get("prompt_tokens") != item["actual_input_tokens"]:
                raise ContractError(f"{run.name}/{item['case_id']}: retained response is inconsistent")
    recomputed = summarize(metadata["run_id"], records, selection["context_levels"], selection["evidence_positions"], selection["case_ids"], selection["complete_definition_coverage"], definition)
    if summary != recomputed:
        raise ContractError(f"{run.name}: stored summary is not reproducible")
    return summary
