#!/usr/bin/env python3
"""Deterministic ECC-005 Qwen-only contracts and offline evidence validation."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFINITION, CONFIGS, RUNS, SCHEMAS = ROOT / "definition", ROOT / "configs", ROOT / "runs", ROOT / "schemas"
ECC004_SCRIPTS = ROOT.parent / "ecc-004-llama-position-confirmation" / "scripts"
sys.path.insert(0, str(ECC004_SCRIPTS))
import ecc004

ContractError, ServerClient, TokenRuntime, BuiltCase = ecc004.ContractError, ecc004.ServerClient, ecc004.TokenRuntime, ecc004.BuiltCase
ecc002, ecc003 = ecc004.ecc002, ecc004.ecc003


def load_json(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding="utf-8"))
def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
def fingerprint_values(definition: dict[str, Any], cases: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    for name, value in (("experiment.json", definition), ("cases.json", cases)):
        digest.update(name.encode()); digest.update(b"\0"); digest.update((json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode())
    return digest.hexdigest()
def definition_fingerprint() -> str: return fingerprint_values(load_json(DEFINITION / "experiment.json"), load_json(DEFINITION / "cases.json"))
def positions(definition: dict[str, Any]) -> list[dict[str, Any]]: return definition["independent_variables"]["evidence_position"]["levels"]
def position_spec(definition: dict[str, Any], position: str) -> dict[str, Any]: return next(item for item in positions(definition) if item["id"] == position)
def validate_schema(value: Any, name: str) -> None:
    try: jsonschema.validate(value, load_json(SCHEMAS / name))
    except jsonschema.ValidationError as exc: raise ContractError(f"schema validation failed for {name}: {exc.message}") from exc


def load_definition() -> tuple[dict[str, Any], list[dict[str, str]]]:
    definition, inventory = load_json(DEFINITION / "experiment.json"), load_json(DEFINITION / "cases.json")
    validate_schema(definition, "experiment-definition.schema.json")
    cases = inventory.get("cases", [])
    if definition.get("id") != "ecc-005-qwen-position-confirmation" or inventory.get("version") != 1 or len(cases) != 30:
        raise ContractError("ECC-005 definition or fresh case count is invalid")
    for field in ("id", "generator_case_id", "entity", "answer"):
        if len({case[field] for case in cases}) != 30: raise ContractError(f"fresh case {field} values must be unique")
    historical = []
    for module in (ecc002, ecc003, ecc004): historical.extend(module.load_json(module.DEFINITION / "cases.json")["cases"])
    if {case["entity"] for case in cases} & {case["entity"] for case in historical} or {case["answer"] for case in cases} & {case["answer"] for case in historical}:
        raise ContractError("ECC-005 targets overlap historical experiments")
    if definition["independent_variables"]["requested_input_tokens"]["levels"] != [8192, 16384] or [item["id"] for item in positions(definition)] != ["early", "late"]:
        raise ContractError("ECC-005 matrix must be frozen as 8k/16k by early/late")
    return definition, cases


def compose(case: dict[str, str], pairs: int, position: str, seed: int): return ecc004.compose(case, pairs, position, seed)
def build_case(runtime: TokenRuntime, case: dict[str, str], target: int, position: str, definition: dict[str, Any]) -> BuiltCase: return ecc004.build_case(runtime, case, target, position, definition)
def classify_failure(case: dict[str, str], raw: str, pairs: int, position: str, definition: dict[str, Any]): return ecc004.classify_failure(case, raw, pairs, position, definition)
def built_case_dict(value: BuiltCase) -> dict[str, Any]: return ecc004.built_case_dict(value)


def summarize(run_id: str, records: list[dict[str, Any]], levels: list[int], positions_: list[str], case_ids: list[str], complete_definition_coverage: bool, definition: dict[str, Any]) -> dict[str, Any]:
    invalid = sum(bool(row["error"]) or row["truncated"] for row in records); expected = len(levels) * len(positions_) * len(case_ids); complete = complete_definition_coverage and len(records) == expected and not invalid
    positions_out = []
    for position in positions_:
        rows = []
        for level in levels:
            values = [row for row in records if row["requested_input_tokens"] == level and row["requested_evidence_position"] == position and not row["error"] and not row["truncated"]]
            times = [row["timing"]["total_ms"] for row in values]
            rows.append({"requested_input_tokens":level,"cases":len(values),"passed":sum(row["evaluation"]["passed"] for row in values),"accuracy":sum(row["evaluation"]["passed"] for row in values)/len(values) if values else None,"actual_input_tokens_min":min((row["actual_input_tokens"] for row in values),default=None),"actual_input_tokens_max":max((row["actual_input_tokens"] for row in values),default=None),"runtime":{"count":len(times),"median_total_ms":statistics.median(times) if times else None,"min_total_ms":min(times) if times else None,"max_total_ms":max(times) if times else None}})
        positions_out.append({"position":position,"levels":rows})
    metrics, paired = [], []
    for level in levels:
        accuracy = {item["position"]:next(row for row in item["levels"] if row["requested_input_tokens"] == level)["accuracy"] for item in positions_out}
        gap = accuracy["early"] - accuracy["late"] if None not in accuracy.values() else None
        lookup = {(row["case_id"],row["requested_evidence_position"]):row["evaluation"]["passed"] for row in records if row["requested_input_tokens"] == level and not row["error"] and not row["truncated"]}
        states = [(lookup[(case,"early")],lookup[(case,"late")]) for case in case_ids if (case,"early") in lookup and (case,"late") in lookup]
        transition = {"early_pass_late_fail":sum(left and not right for left,right in states),"early_fail_late_pass":sum(not left and right for left,right in states),"paired_cases":len(states)}
        metrics.append({"requested_input_tokens":level,"accuracy_by_position":accuracy,"early_minus_late":gap}); paired.append({"requested_input_tokens":level,"early_vs_late":transition})
    failures = [row for row in records if not row["error"] and not row["truncated"] and not row["evaluation"]["passed"]]
    failure = {"total_failures":len(failures),"by_context_level":{str(level):sum(row["requested_input_tokens"]==level for row in failures) for level in levels},"by_position":{position:sum(row["requested_evidence_position"]==position for row in failures) for position in positions_},"by_diagnostic_class":{kind:sum(row["failure"] and row["failure"]["kind"]==kind for row in failures) for kind in definition["failure_classes"]},"numeric_suffix_matches_expected":sum(row["output"]["raw_text"].strip() == row["expected_answer"].split("-")[1] for row in failures)}
    endpoint = next((item for item in metrics if item["requested_input_tokens"] == 16384), None)
    transitions = next((item for item in paired if item["requested_input_tokens"] == 16384), None)
    if not complete or endpoint is None or transitions is None: status = "unresolved"
    elif endpoint["early_minus_late"] >= .10 and transitions["early_vs_late"]["early_pass_late_fail"] >= 4 and transitions["early_vs_late"]["early_pass_late_fail"] > transitions["early_vs_late"]["early_fail_late_pass"]: status = "position_sensitivity_observed"
    elif abs(endpoint["early_minus_late"]) <= .10 and abs(transitions["early_vs_late"]["early_pass_late_fail"]-transitions["early_vs_late"]["early_fail_late_pass"]) < 4: status = "stable"
    else: status = "possible_position_sensitivity"
    runtime = [{"requested_input_tokens":level,"position":item["position"],**next(row for row in item["levels"] if row["requested_input_tokens"]==level)["runtime"]} for level in levels for item in positions_out]
    return {"run_id":run_id,"run_status":"valid" if complete else "invalid","coverage":{"complete":complete,"expected_results":expected,"observed_results":len(records)},"total_results":len(records),"invalid_results":invalid,"positions":positions_out,"position_metrics":metrics,"paired_transitions":paired,"failure_analysis":failure,"interpretation":{"status":status,"rule":definition["interpretation"]},"runtime":{"by_context_position":runtime}}


def validate_run(run: Path) -> dict[str, Any]:
    definition,cases=load_definition(); metadata,summary=load_json(run/"metadata.json"),load_json(run/"summary.json"); records=[json.loads(line) for line in (run/"results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    validate_schema(metadata, "run-metadata.schema.json"); validate_schema(summary, "run-summary.schema.json")
    if metadata["definition_fingerprint"] != definition_fingerprint() or metadata["model"]["key"] != "qwen3-4b": raise ContractError("fingerprint or Qwen-only scope mismatch")
    selection=metadata["selection"]; all_cases=[case["id"] for case in cases]; complete=selection["context_levels"]==[8192,16384] and selection["evidence_positions"]==["early","late"] and selection["case_ids"]==all_cases
    if selection["complete_definition_coverage"] != complete or complete and metadata["repository"]["dirty"]: raise ContractError("selection or clean-worktree contract mismatch")
    expected={(case,level,pos) for case in selection["case_ids"] for level in selection["context_levels"] for pos in selection["evidence_positions"]}; observed=[(row["case_id"],row["requested_input_tokens"],row["requested_evidence_position"]) for row in records]
    if len(observed)!=len(set(observed)) or set(observed)!=expected: raise ContractError("coverage mismatch")
    lookup={case["id"]:case for case in cases}
    for row in records:
        validate_schema(row, "case-result.schema.json")
        case=lookup[row["case_id"]]; _ctx,content,_prefix,distractors=compose(case,row["distractor_pairs"],row["requested_evidence_position"],definition["case_generation"]["seed"])
        passed,normal=ecc002.evaluate(case["answer"],row["output"]["raw_text"]); expected_failure=None if row["error"] else classify_failure(case,row["output"]["raw_text"],row["distractor_pairs"],row["requested_evidence_position"],definition)
        if row["request"]["messages"][0]["content"]!=content or row["distractor_records"]!=distractors or hashlib.sha256(content.encode()).hexdigest()!=row["context_sha256"] or row["evaluation"]!={"passed":passed,"score":float(passed)} or row["output"]["normalized_text"]!=normal or row["failure"]!=expected_failure: raise ContractError("generator, hash, evaluation, or diagnostic mismatch")
        shortfall=row["requested_input_tokens"]-row["actual_input_tokens"]; ratio=round(row["evidence_start_token"]/row["context_tokens"],6)
        if row["truncated"] or row["actual_input_tokens"]+row["output_token_budget"]>row["configured_context_size"] or not 0<=shortfall<=160 or abs(ratio-position_spec(definition,row["requested_evidence_position"])["target_ratio"])>.05: raise ContractError("token/position/truncation mismatch")
    recomputed=summarize(metadata["run_id"],records,selection["context_levels"],selection["evidence_positions"],selection["case_ids"],selection["complete_definition_coverage"],definition)
    if summary!=recomputed: raise ContractError("summary mismatch")
    return summary
