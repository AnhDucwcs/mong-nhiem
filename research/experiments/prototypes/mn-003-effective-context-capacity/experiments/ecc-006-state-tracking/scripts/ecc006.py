#!/usr/bin/env python3
"""Deterministic contracts for the ECC-006 State Tracking baseline."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from dataclasses import asdict, dataclass
from itertools import pairwise
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def definition_fingerprint() -> str:
    digest = hashlib.sha256()
    for name in ("experiment.json", "cases.json"):
        digest.update(name.encode()); digest.update(b"\0")
        digest.update((json.dumps(load_json(DEFINITION / name), sort_keys=True, separators=(",", ":")) + "\n").encode())
    return digest.hexdigest()


def load_definition() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    definition, inventory = load_json(DEFINITION / "experiment.json"), load_json(DEFINITION / "cases.json")
    cases, levels = inventory.get("cases", []), definition["independent_variable"]["requested_input_tokens"]["levels"]
    if definition.get("id") != "ecc-006-state-tracking" or inventory.get("version") != 1:
        raise ContractError("invalid ECC-006 definition version")
    if len(cases) != definition["case_generation"]["semantic_cases"] or levels != [512, 2048, 8192, 16384]:
        raise ContractError("ECC-006 frozen case count or ladder differs")
    for key in ("id", "entity", "answer"):
        if len({case[key] for case in cases}) != len(cases): raise ContractError(f"case {key} values must be unique")
    if any(len(case["updates"]) != definition["controls"]["target_updates"] or case["updates"][-1] != case["answer"] for case in cases):
        raise ContractError("target updates must have exactly four events and final answer")
    return definition, cases


def target_events(case: dict[str, Any]) -> list[str]:
    return [f"State update: {case['entity']} changed to {state}." for state in case["updates"]]


def distractor(case_id: str, index: int, side: str, seed: int) -> list[str]:
    digest = hashlib.sha256(f"{seed}:{case_id}:{index}:{side}".encode()).digest()
    entity = f"Unit Drift {1000 + int.from_bytes(digest[:2], 'big') % 8000}"
    states = ("RED", "BLUE", "AMBER", "GREEN", "SILVER", "VIOLET", "ORANGE", "BLACK")
    return [f"State update: {entity} changed to {states[(digest[offset] + offset) % len(states)]}." for offset in range(4)]


def compose(case: dict[str, Any], histories: int, seed: int) -> tuple[str, str, str, list[str]]:
    before = [line for index in range(1, histories + 1) for line in distractor(case["id"], index, "before", seed)]
    after = [line for index in range(1, histories + 1) for line in distractor(case["id"], index, "after", seed)]
    target = target_events(case)
    prefix = "Context event log:\n" + ("\n".join(before) + "\n" if before else "")
    context = prefix + "\n".join(target) + ("\n" + "\n".join(after) if after else "")
    content = context + f"\n\nQuestion:\nWhat is the current state of {case['entity']}? Return only the state."
    return context, content, prefix, before + after


@dataclass(frozen=True)
class BuiltCase:
    case_id: str; requested_input_tokens: int; actual_input_tokens: int; content_tokens: int
    prompt_overhead_tokens: int; context_tokens: int; evidence_start_token: int; evidence_position_ratio: float
    distractor_histories: int; relevant_fact: str; expected_answer: str; context_sha256: str; content: str


def build_case(runtime: TokenRuntime, case: dict[str, Any], target: int, definition: dict[str, Any]) -> BuiltCase:
    seed = definition["case_generation"]["seed"]
    def count(histories: int) -> int: return runtime.count_prompt(compose(case, histories, seed)[1])
    if count(0) > target: raise ContractError(f"{case['id']} cannot fit target {target}")
    low, high = 0, 1
    while count(high) <= target:
        low, high = high, high * 2
        if high > target: break
    while low + 1 < high:
        middle = (low + high) // 2
        if count(middle) <= target: low = middle
        else: high = middle
    context, content, prefix, _ = compose(case, low, seed)
    actual, content_tokens, context_tokens = runtime.count_prompt(content), runtime.count_text(content), runtime.count_text(context)
    start, ratio, shortfall = runtime.count_text(prefix), runtime.count_text(prefix) / context_tokens, target - actual
    budget, controls = definition["token_budget"], definition["controls"]
    if not 0 <= shortfall <= budget["maximum_target_shortfall_tokens"]: raise ContractError("token shortfall violates definition")
    if abs(ratio - controls["evidence_position"]["target_ratio"]) > controls["evidence_position"]["allowed_absolute_error"]: raise ContractError("target sequence violates midpoint policy")
    if actual + budget["output_tokens"] > budget["configured_context_size"]: raise ContractError("context overflow")
    return BuiltCase(case["id"], target, actual, content_tokens, actual-content_tokens, context_tokens, start, round(ratio,6), low, "\n".join(target_events(case)), case["answer"], hashlib.sha256(content.encode()).hexdigest(), content)


def evaluate(expected: str, raw: str) -> tuple[bool, str]: return ecc001.evaluate(expected, raw)


def failure(expected: str, raw: str, error: dict[str, Any] | None) -> str | None:
    if error: return "runtime_or_infrastructure_error"
    passed, normalized = evaluate(expected, raw)
    if passed: return None
    return "malformed_response" if not normalized.isalpha() or " " in normalized else "incorrect_state"


def summarize(run_id: str, records: list[dict[str, Any]], levels: list[int], case_ids: list[str], complete: bool) -> dict[str, Any]:
    invalid = sum(bool(row["error"]) or row["truncated"] for row in records); expected = len(levels)*len(case_ids); valid = complete and len(records)==expected and not invalid
    rows=[]
    for level in levels:
        group=[row for row in records if row["requested_input_tokens"]==level and not row["error"] and not row["truncated"]]; accuracy=sum(row["evaluation"]["passed"] for row in group)/len(group) if group else None
        rows.append({"requested_input_tokens":level,"cases":len(group),"passed":sum(row["evaluation"]["passed"] for row in group),"accuracy":accuracy,"relative_accuracy":None,"actual_input_tokens_min":min((row["actual_input_tokens"] for row in group),default=None),"actual_input_tokens_max":max((row["actual_input_tokens"] for row in group),default=None)})
    baseline=rows[0]["accuracy"] if rows else None
    if baseline:
        for row in rows: row["relative_accuracy"]=row["accuracy"]/baseline if row["accuracy"] is not None else None
    def threshold(value: float) -> int | None:
        answer=None
        for row in rows:
            if row["relative_accuracy"] is None or row["relative_accuracy"] < value: break
            answer=row["requested_input_tokens"]
        return answer
    times=[row["timing"]["total_ms"] for row in records if not row["error"]]
    return {"run_id":run_id,"run_status":"valid" if valid else "invalid","coverage":{"complete":valid,"expected_results":expected,"observed_results":len(records)},"total_results":len(records),"invalid_results":invalid,"baseline_context_level":levels[0],"baseline_accuracy":baseline,"levels":rows,"ecc":{"ECC95":threshold(.95) if valid and baseline else None,"ECC90":threshold(.90) if valid and baseline else None,"ECC80":threshold(.80) if valid and baseline else None,"status":"resolved" if valid and baseline else "unresolved","rule":"contiguous tested prefix; no interpolation"},"non_monotonic":any(b>a for a,b in pairwise([row["accuracy"] for row in rows if row["accuracy"] is not None])),"failure_analysis":{kind:sum(row.get("failure")==kind for row in records) for kind in ("runtime_or_infrastructure_error","invalid_case","malformed_response","incorrect_state")},"runtime":{"median_total_ms":statistics.median(times) if times else None}}


def built_case_dict(value: BuiltCase) -> dict[str, Any]: return asdict(value)


def validate_run(run: Path) -> dict[str, Any]:
    definition, cases = load_definition()
    metadata, summary = load_json(run / "metadata.json"), load_json(run / "summary.json")
    records = [json.loads(line) for line in (run / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    if metadata["definition_fingerprint"] != definition_fingerprint(): raise ContractError("definition fingerprint mismatch")
    selection = metadata["selection"]
    complete = selection["context_levels"] == definition["independent_variable"]["requested_input_tokens"]["levels"] and selection["case_ids"] == [case["id"] for case in cases]
    if selection["complete_definition_coverage"] != complete or complete and metadata["repository"]["dirty"]: raise ContractError("clean complete-run contract mismatch")
    expected = {(case, level) for case in selection["case_ids"] for level in selection["context_levels"]}
    if {(row["case_id"],row["requested_input_tokens"]) for row in records} != expected or len(records) != len(expected): raise ContractError("coverage mismatch")
    lookup={case["id"]:case for case in cases}
    for row in records:
        case=lookup[row["case_id"]]; _ctx,content,_prefix,_distractors=compose(case,row["distractor_histories"],definition["case_generation"]["seed"])
        passed,normalized=evaluate(case["answer"],row["output"]["raw_text"])
        if row["request"]["messages"][0]["content"] != content or hashlib.sha256(content.encode()).hexdigest()!=row["context_sha256"] or row["expected_answer"]!=case["answer"] or row["relevant_fact"]!="\n".join(target_events(case)) or row["output"]["normalized_text"]!=normalized or row["evaluation"]!={"passed":passed,"score":float(passed)}: raise ContractError("case replay or evaluation mismatch")
        if row["truncated"] or row["actual_input_tokens"]+row["output_token_budget"]>row["configured_context_size"]: raise ContractError("invalid context result")
    recomputed=summarize(metadata["run_id"],records,selection["context_levels"],selection["case_ids"],selection["complete_definition_coverage"])
    if summary != recomputed: raise ContractError("summary mismatch")
    return summary
