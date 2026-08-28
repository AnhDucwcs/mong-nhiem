#!/usr/bin/env python3
"""Deterministic contracts for the ECC-007 causal-reasoning baseline."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from dataclasses import asdict, dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFINITION, CONFIGS, RUNS = ROOT / "definition", ROOT / "configs", ROOT / "runs"
ECC006 = ROOT.parent / "ecc-006-state-tracking" / "scripts"
sys.path.insert(0, str(ECC006))
import ecc006

ContractError = ecc006.ContractError
ServerClient = ecc006.ServerClient
TokenRuntime = ecc006.TokenRuntime


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def definition_fingerprint() -> str:
    digest = hashlib.sha256()
    for name in ("experiment.json", "cases.json"):
        digest.update(name.encode("utf-8")); digest.update(b"\0")
        canonical = json.dumps(load_json(DEFINITION / name), sort_keys=True, separators=(",", ":")) + "\n"
        digest.update(canonical.encode("utf-8"))
    return digest.hexdigest()


def graph(case_index: int, hop_count: int, positive: bool, case_id: str | None = None) -> dict[str, Any]:
    prefix = f"NODE_{700 + case_index}_"
    chain = [prefix + chr(65 + index) for index in range(hop_count + 1)]
    return {
        "id": case_id or f"c{case_index:02d}",
        "case_index": case_index,
        "hop_count": hop_count,
        "positive": positive,
        "source": chain[0],
        "target": chain[-1] if positive else prefix + "Z",
        "edges": [(chain[index], chain[index + 1]) for index in range(hop_count)],
    }


def reachable(edges: list[tuple[str, str]], source: str, target: str) -> bool:
    seen, pending = {source}, [source]
    while pending:
        node = pending.pop()
        for left, right in edges:
            if left == node and right not in seen:
                seen.add(right); pending.append(right)
    return target in seen


def edge_text(edge: tuple[str, str]) -> str:
    return f"Causal link: {edge[0]} causes {edge[1]}."


def distractor(case_id: str, index: int, side: str, _seed: int) -> tuple[str, str]:
    """Return a unique, disconnected edge in exactly the target-record format."""
    stem = case_id.replace("-", "_")
    return (f"NODE_D_{stem}_{side}_{index}_A", f"NODE_D_{stem}_{side}_{index}_B")


def compose(
    case: dict[str, Any], distractor_edges: int, seed: int, before_edges: int | None = None
) -> tuple[str, str, str, list[tuple[str, str]]]:
    before_edges = distractor_edges // 2 if before_edges is None else before_edges
    after_edges = distractor_edges - before_edges
    before = [distractor(case["id"], index, "before", seed) for index in range(1, before_edges + 1)]
    after = [distractor(case["id"], index, "after", seed) for index in range(1, after_edges + 1)]
    prefix = "Causal graph statements:\n" + ("\n".join(edge_text(edge) for edge in before) + "\n" if before else "")
    context = prefix + "\n".join(edge_text(edge) for edge in case["edges"])
    if after:
        context += "\n" + "\n".join(edge_text(edge) for edge in after)
    content = context + f"\n\nQuestion:\nDoes {case['source']} eventually cause {case['target']}? Return only YES or NO."
    return context, content, prefix, before + after


def expected_answer(case: dict[str, Any]) -> str:
    return "YES" if case["positive"] else "NO"


def relevant_graph(case: dict[str, Any]) -> str:
    return "\n".join(edge_text(edge) for edge in case["edges"])


def load_definition() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    definition, inventory = load_json(DEFINITION / "experiment.json"), load_json(DEFINITION / "cases.json")
    cases = inventory.get("cases", [])
    levels = definition["independent_variable"]["requested_input_tokens"]["levels"]
    if definition.get("id") != "ecc-007-causal-reasoning" or inventory.get("version") != 1:
        raise ContractError("invalid ECC-007 definition version")
    if levels != [512, 2048, 8192, 16384] or len(cases) != definition["case_generation"]["semantic_cases"]:
        raise ContractError("ECC-007 frozen case count or ladder differs")
    if len({case.get("id") for case in cases}) != len(cases) or len({case.get("case_index") for case in cases}) != len(cases):
        raise ContractError("case identifiers must be unique")
    if sum(bool(case.get("positive")) for case in cases) * 2 != len(cases):
        raise ContractError("ECC-007 cases must be balanced positive/negative")
    hop_count = definition["controls"]["causal_hop_count"]
    for case in cases:
        generated = graph(case["case_index"], hop_count, case["positive"], case["id"])
        if (
            case.get("source") != generated["source"]
            or case.get("target") != generated["target"]
            or [tuple(edge) for edge in case.get("edges", [])] != generated["edges"]
        ):
            raise ContractError(f"case graph mismatch: {case.get('id')}")
        if reachable(case["edges"], case["source"], case["target"]) != case["positive"]:
            raise ContractError(f"case reachability mismatch: {case['id']}")
        if len(case["edges"]) != hop_count or len(set(map(tuple, case["edges"]))) != hop_count:
            raise ContractError(f"case hop count or edges invalid: {case['id']}")
    return definition, cases


@dataclass(frozen=True)
class BuiltCase:
    case_id: str; requested_input_tokens: int; actual_input_tokens: int; content_tokens: int
    prompt_overhead_tokens: int; context_tokens: int; evidence_start_token: int; evidence_position_ratio: float
    distractor_edges: int; distractor_edges_before: int; relevant_graph: str; expected_answer: str
    context_sha256: str; content: str


def build_case(runtime: TokenRuntime, case: dict[str, Any], target: int, definition: dict[str, Any]) -> BuiltCase:
    seed = definition["case_generation"]["seed"]
    def count(edges: int) -> int:
        return runtime.count_prompt(compose(case, edges, seed)[1])
    if count(0) > target:
        raise ContractError(f"{case['id']} cannot fit target {target}")
    low, high = 0, 1
    while count(high) <= target:
        low, high = high, high * 2
        if high > target:
            break
    while low + 1 < high:
        middle = (low + high) // 2
        if count(middle) <= target:
            low = middle
        else:
            high = middle
    candidates = []
    for before_edges in range(low + 1):
        context, content, prefix, _ = compose(case, low, seed, before_edges)
        actual = runtime.count_prompt(content)
        if actual <= target:
            ratio = runtime.count_text(prefix) / runtime.count_text(context)
            candidates.append((abs(ratio - definition["controls"]["evidence_position"]["target_ratio"]), context, content, prefix, actual, before_edges))
    if not candidates:
        raise ContractError("no valid midpoint placement candidate")
    _distance, context, content, prefix, actual, before = min(candidates, key=lambda item: item[0])
    content_tokens, context_tokens = runtime.count_text(content), runtime.count_text(context)
    start = runtime.count_text(prefix)
    ratio, shortfall = start / context_tokens, target - actual
    budget, controls = definition["token_budget"], definition["controls"]
    if not 0 <= shortfall <= budget["maximum_target_shortfall_tokens"]:
        raise ContractError("token shortfall violates definition")
    if abs(ratio - controls["evidence_position"]["target_ratio"]) > controls["evidence_position"]["allowed_absolute_error"]:
        raise ContractError("target graph violates midpoint policy")
    if actual + budget["output_tokens"] > budget["configured_context_size"]:
        raise ContractError("context overflow")
    return BuiltCase(
        case["id"], target, actual, content_tokens, actual - content_tokens, context_tokens, start, round(ratio, 6),
        low, before, relevant_graph(case), expected_answer(case), hashlib.sha256(content.encode("utf-8")).hexdigest(), content,
    )


def evaluate(case: dict[str, Any], raw: str) -> tuple[bool, str]:
    normalized = ecc006.ecc001.normalize_answer(raw)
    return normalized == expected_answer(case).lower(), normalized


def failure(case: dict[str, Any], raw: str, error: dict[str, Any] | None) -> str | None:
    if error:
        return "runtime_or_infrastructure_error"
    passed, normalized = evaluate(case, raw)
    if passed:
        return None
    return "malformed_response" if normalized not in {"yes", "no"} else "incorrect_causal_inference"


def summarize(run_id: str, records: list[dict[str, Any]], levels: list[int], case_ids: list[str], complete: bool) -> dict[str, Any]:
    invalid = sum(bool(row["error"]) or row["truncated"] for row in records)
    expected = len(levels) * len(case_ids)
    valid = complete and len(records) == expected and not invalid
    rows = []
    for level in levels:
        group = [row for row in records if row["requested_input_tokens"] == level and not row["error"] and not row["truncated"]]
        accuracy = sum(row["evaluation"]["passed"] for row in group) / len(group) if group else None
        times = [row["timing"]["total_ms"] for row in group]
        rows.append({
            "requested_input_tokens": level, "cases": len(group), "passed": sum(row["evaluation"]["passed"] for row in group),
            "accuracy": accuracy, "relative_accuracy": None,
            "actual_input_tokens_min": min((row["actual_input_tokens"] for row in group), default=None),
            "actual_input_tokens_max": max((row["actual_input_tokens"] for row in group), default=None),
            "runtime_total_ms": {"median": statistics.median(times) if times else None, "min": min(times) if times else None, "max": max(times) if times else None},
        })
    baseline = rows[0]["accuracy"] if rows else None
    if baseline:
        for row in rows:
            row["relative_accuracy"] = row["accuracy"] / baseline if row["accuracy"] is not None else None
    def threshold(value: float) -> tuple[int | None, str]:
        answer = None
        for row in rows:
            if row["relative_accuracy"] is None or row["relative_accuracy"] < value:
                return answer, "resolved"
            answer = row["requested_input_tokens"]
        return answer, "right_censored_lower_bound"
    ecc = {}
    for label, value in (("ECC95", .95), ("ECC90", .90), ("ECC80", .80)):
        level, status = threshold(value) if valid and baseline else (None, "unresolved")
        ecc[label] = {"tested_level": level, "status": status}
    failures = ("runtime_or_infrastructure_error", "invalid_case", "malformed_response", "incorrect_causal_inference")
    return {
        "run_id": run_id, "run_status": "valid" if valid else "invalid",
        "coverage": {"complete": valid, "expected_results": expected, "observed_results": len(records)},
        "total_results": len(records, ), "invalid_results": invalid,
        "baseline_context_level": levels[0], "baseline_accuracy": baseline, "levels": rows,
        "ecc": {"metrics": ecc, "rule": "contiguous tested prefix; no interpolation"},
        "non_monotonic": any(second > first for first, second in pairwise([row["accuracy"] for row in rows if row["accuracy"] is not None])),
        "failure_analysis": {kind: sum(row.get("failure") == kind for row in records) for kind in failures},
        "runtime": {"median_total_ms": statistics.median([row["timing"]["total_ms"] for row in records if not row["error"]]) if any(not row["error"] for row in records) else None},
    }


def built_case_dict(value: BuiltCase) -> dict[str, Any]:
    return asdict(value)


def validate_run(run: Path) -> dict[str, Any]:
    definition, cases = load_definition()
    metadata, summary = load_json(run / "metadata.json"), load_json(run / "summary.json")
    records = [json.loads(line) for line in (run / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    jsonschema.validate(definition, load_json(ROOT / "schemas" / "experiment-definition.schema.json"))
    jsonschema.validate(metadata, load_json(ROOT / "schemas" / "run-metadata.schema.json"))
    jsonschema.validate(summary, load_json(ROOT / "schemas" / "run-summary.schema.json"))
    case_schema = load_json(ROOT / "schemas" / "case-result.schema.json")
    for row in records:
        jsonschema.validate(row, case_schema)
    if metadata["definition_fingerprint"] != definition_fingerprint():
        raise ContractError("definition fingerprint mismatch")
    selection = metadata["selection"]
    complete = selection["context_levels"] == definition["independent_variable"]["requested_input_tokens"]["levels"] and selection["case_ids"] == [case["id"] for case in cases]
    if selection["complete_definition_coverage"] != complete or complete and metadata["repository"]["dirty"]:
        raise ContractError("clean complete-run contract mismatch")
    expected = {(case_id, level) for case_id in selection["case_ids"] for level in selection["context_levels"]}
    if {(row["case_id"], row["requested_input_tokens"]) for row in records} != expected or len(records) != len(expected):
        raise ContractError("coverage mismatch")
    lookup = {case["id"]: case for case in cases}
    for row in records:
        case = lookup[row["case_id"]]
        _context, content, _prefix, distractors = compose(case, row["distractor_edges"], definition["case_generation"]["seed"], row["distractor_edges_before"])
        all_edges = [tuple(edge) for edge in case["edges"]] + distractors
        if len(all_edges) != len(set(all_edges)) or reachable(distractors, case["source"], case["target"]):
            raise ContractError("duplicate or target-leaking distractor edge")
        passed, normalized = evaluate(case, row["output"]["raw_text"])
        if (
            row["request"]["messages"][0]["content"] != content
            or hashlib.sha256(content.encode("utf-8")).hexdigest() != row["context_sha256"]
            or row["expected_answer"] != expected_answer(case)
            or row["relevant_graph"] != relevant_graph(case)
            or row["output"]["normalized_text"] != normalized
            or row["evaluation"] != {"passed": passed, "score": float(passed)}
        ):
            raise ContractError("case replay or evaluation mismatch")
        if row["truncated"] or row["actual_input_tokens"] + row["output_token_budget"] > row["configured_context_size"]:
            raise ContractError("invalid context result")
    recomputed = summarize(metadata["run_id"], records, selection["context_levels"], selection["case_ids"], selection["complete_definition_coverage"])
    if summary != recomputed:
        raise ContractError("summary mismatch")
    return summary
