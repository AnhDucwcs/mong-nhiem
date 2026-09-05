#!/usr/bin/env python3
"""Execute one predeclared MN-004 phase; never changes the frozen experiment."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import re
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

import mn004

PHASES = ("llama_reproduction", "llama_untreated", "llama_ledger", "qwen_untreated", "qwen_ledger")


def command_output(arguments: list[str]) -> str:
    result = subprocess.run(arguments, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    return (result.stdout or "") + (result.stderr or "")


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def runtime_identity(server: Path) -> dict[str, Any]:
    raw = command_output([str(server), "--version"])
    match = re.search(r"version:\s*(.*?)\s*\(build\s+(\d+),\s*commit\s+([0-9a-f]+)", raw, re.IGNORECASE)
    return {"backend": "llama.cpp", "version": match.group(1).strip() if match else None, "build": match.group(2) if match else None, "commit": match.group(3) if match else None, "raw_version_output": raw}


def hardware_identity() -> dict[str, Any]:
    gpu = command_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"])
    fields = [field.strip() for field in next((line for line in gpu.splitlines() if line.strip()), "").split(",")]
    return {"os": platform.platform() or None, "cpu": platform.processor() or None, "gpu": fields[0] if fields else None, "vram_bytes": int(fields[1]) * 1024 * 1024 if len(fields) > 1 and fields[1].isdigit() else None, "driver": fields[2] if len(fields) > 2 else None}


def wait_for_server(process: subprocess.Popen[Any], url: str) -> None:
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise mn004.ContractError(f"llama-server exited: {process.returncode}")
        try:
            with urllib.request.urlopen(url + "/health", timeout=2) as response:
                if response.status == 200:
                    return
        except (TimeoutError, urllib.error.URLError):
            time.sleep(0.5)
    raise mn004.ContractError("llama-server did not become healthy")


def model_for_phase(phase: str) -> tuple[str, str, bool]:
    if phase == "llama_reproduction": return "llama-3.2-3b", "natural_language", True
    if phase == "llama_untreated": return "llama-3.2-3b", "natural_language", False
    if phase == "llama_ledger": return "llama-3.2-3b", "ledger", False
    if phase == "qwen_untreated": return "qwen3-4b", "natural_language", False
    if phase == "qwen_ledger": return "qwen3-4b", "ledger", False
    raise mn004.ContractError(f"unknown phase {phase}")


def phase_runs(phase: str) -> list[Path]:
    return sorted(path for path in mn004.RUNS.glob("*") if (path / "metadata.json").is_file() and mn004.load_json(path / "metadata.json").get("phase") == phase)


def valid_phase_result(phase: str) -> dict[str, Any] | None:
    runs = phase_runs(phase)
    if not runs:
        return None
    run = runs[-1]
    records = [json.loads(line) for line in (run / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    if any(row["validator_status"] != "valid" or row["truncated"] or row["error"] for row in records):
        return None
    return {"run": run, "records": records}


def passes_by_level(records: list[dict[str, Any]]) -> dict[int, int]:
    return {level: sum(bool(row["evaluation"]["passed"]) for row in records if row["requested_input_tokens"] == level) for level in (512, 2048, 8192, 16384)}


def enforce_order(phase: str, definition: dict[str, Any]) -> None:
    reproduction = valid_phase_result("llama_reproduction")
    untreated = valid_phase_result("llama_untreated")
    ledger = valid_phase_result("llama_ledger")
    qwen_untreated = valid_phase_result("qwen_untreated")
    if phase == "llama_reproduction":
        return
    if not reproduction:
        raise mn004.ContractError("execution order requires a valid Llama reproduction")
    counts = passes_by_level(reproduction["records"])
    compatibility = definition["baseline_compatibility"]
    if any(not compatibility[str(level)][0] <= counts[level] <= compatibility[str(level)][1] for level in counts):
        raise mn004.ContractError("baseline_drift: Gate B forbids subsequent Llama treatment")
    if phase == "llama_untreated": return
    if phase == "llama_ledger":
        if not untreated: raise mn004.ContractError("execution order requires valid Llama untreated evidence")
        return
    if not ledger:
        raise mn004.ContractError("execution order requires valid Llama ledger evidence")
    if phase == "qwen_untreated": return
    if not qwen_untreated:
        raise mn004.ContractError("execution order requires valid Qwen untreated evidence")
    counts = passes_by_level(qwen_untreated["records"])
    if any(counts[level] < definition["qwen_rules"]["per_level_eligibility_minimum"] for level in counts) or sum(counts.values()) < definition["qwen_rules"]["aggregate_eligibility_minimum"]:
        raise mn004.ContractError("control_not_qualified: Gate B forbids Qwen ledger treatment")


def validate_preflight(definition: dict[str, Any], inventory: dict[str, Any], model_key: str) -> dict[str, Any]:
    preflight = mn004.load_json(mn004.DEFINITION / f"preflight-{model_key}.json")
    if preflight["definition_fingerprint"] != mn004.definition_fingerprint(definition) or preflight["inventory_fingerprint"] != inventory["inventory_fingerprint"]:
        raise mn004.ContractError("preflight authority mismatch")
    if preflight["status"] != "feasible":
        raise mn004.ContractError("contract_not_executable: hard token preflight blocks all completion requests")
    return preflight


def start_server(server: Path, model: Path, definition: dict[str, Any], kwargs: dict[str, Any], port: int, stdout: Path, stderr: Path) -> subprocess.Popen[Any]:
    runtime = definition["runtime"]
    command = [str(server), "-m", str(model), "--host", "127.0.0.1", "--port", str(port), "-c", str(runtime["configured_context_size"]), "-t", str(runtime["threads"]), "-b", str(runtime["batch_size"]), "-np", str(runtime["parallel_slots"]), "-fa", "on" if runtime["flash_attention"] else "off", "--temp", "0", "--seed", str(runtime["seed"]), "--jinja", "--no-webui", "--no-cache-prompt", "--metrics", "--chat-template-kwargs", json.dumps(kwargs, separators=(",", ":"))]
    return subprocess.Popen(command, stdout=stdout.open("w", encoding="utf-8"), stderr=stderr.open("w", encoding="utf-8"))


def preflight_lookup(preflight: dict[str, Any], item: dict[str, Any], condition: str) -> dict[str, Any]:
    for record in preflight["records"]:
        if record["case_id"] == item["case_id"] and record["requested_input_tokens"] == item["requested_input_tokens"]:
            return record["conditions"][condition]
    raise mn004.ContractError("preflight record is missing matched source case")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    configs = mn004.load_json(mn004.CONFIGS / "models.json")
    parser.add_argument("--phase", required=True, choices=PHASES)
    parser.add_argument("--models-dir", type=Path, default=Path(configs["default_models_dir"]))
    parser.add_argument("--llama-server", type=Path, default=Path(configs["default_llama_server"]))
    parser.add_argument("--port", type=int, default=18614)
    args = parser.parse_args()
    definition = mn004.validate_definition()
    inventory = mn004.load_json(mn004.DEFINITION / "source-inventory.json")
    model_key, condition, frozen_only = model_for_phase(args.phase)
    preflight = validate_preflight(definition, inventory, model_key)
    enforce_order(args.phase, definition)
    model_config = definition["models"][model_key]
    model = args.models_dir / model_config["file"]
    if not model.is_file() or not args.llama_server.is_file() or file_digest(model) != model_config["sha256"]:
        raise mn004.ContractError("model/runtime dependency mismatch")
    identity = runtime_identity(args.llama_server)
    if any(identity[field] != definition["runtime"][field] for field in ("backend", "version", "build", "commit")):
        raise mn004.ContractError("runtime identity mismatch")
    selected = [item for item in inventory["cases"] if not frozen_only or item["origin"] == "frozen"]
    created = dt.datetime.now(dt.UTC)
    run_id = f"{created:%Y%m%dT%H%M%SZ}-mn-004-{args.phase}-{uuid.uuid4().hex[:8]}"
    run_dir, raw = mn004.RUNS / run_id, mn004.RUNS / run_id / "raw"
    raw.mkdir(parents=True)
    metadata = {"run_id": run_id, "created_at": created.isoformat(), "phase": args.phase, "definition_fingerprint": mn004.definition_fingerprint(definition), "inventory_fingerprint": inventory["inventory_fingerprint"], "model": {"key": model_key, "file": model.name, "sha256": model_config["sha256"]}, "runtime": identity, "hardware": hardware_identity(), "inference": {**definition["runtime"], "chat_template_kwargs": model_config["chat_template_kwargs"]}, "selection": {"cases": len(selected), "levels": definition["workload"]["context_levels"], "condition": condition}, "repository": {"commit": command_output(["git", "rev-parse", "HEAD"]).strip(), "dirty": bool(command_output(["git", "status", "--porcelain", "--untracked-files=all"]).strip())}}
    mn004.dump_json(run_dir / "metadata.json", metadata)
    process: subprocess.Popen[Any] | None = None
    records: list[dict[str, Any]] = []
    try:
        process = start_server(args.llama_server, model, definition, model_config["chat_template_kwargs"], args.port, raw / "llama-server.stdout.txt", raw / "llama-server.stderr.txt")
        base_url = f"http://127.0.0.1:{args.port}"
        wait_for_server(process, base_url)
        client = mn004.ServerClient(base_url, model_config["chat_template_kwargs"])
        for item in selected:
            prompt = item["natural_prompt" if condition == "natural_language" else "ledger_prompt"]
            pair = preflight_lookup(preflight, item, condition)
            started, error, response, raw_text = time.perf_counter(), None, None, ""
            {"messages": [{"role": "user", "content": prompt}], "temperature": definition["runtime"]["temperature"], "seed": definition["runtime"]["seed"], "max_tokens": definition["runtime"]["output_tokens"], "chat_template_kwargs": model_config["chat_template_kwargs"]}
            try:
                _request, response = client.complete(prompt, {"temperature": definition["runtime"]["temperature"], "seed": definition["runtime"]["seed"], "output_tokens": definition["runtime"]["output_tokens"]})
                raw_text = response["choices"][0]["message"].get("content") or ""
                observed = response.get("usage", {}).get("prompt_tokens")
                if observed != pair["actual_prompt_tokens"]:
                    raise mn004.ContractError(f"token accounting mismatch: preflight={pair['actual_prompt_tokens']} API={observed}")
            except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError, mn004.ContractError) as exc:
                error = {"type": "model_request_error", "message": f"{type(exc).__name__}: {exc}"}
            truncated = bool(response and response.get("choices") and response["choices"][0].get("finish_reason") == "length")
            failure, diagnostic, normalized = mn004.classify_output(item["target"], item["expected_answer"], item["source_events"], raw_text, error)
            if truncated: failure, diagnostic = "truncation", None
            passed, _ = mn004.evaluate(item["target"], item["expected_answer"], raw_text)
            record = {"evidence_schema_version": definition["evidence_schema_version"], "definition_fingerprint": mn004.definition_fingerprint(definition), "inventory_fingerprint": inventory["inventory_fingerprint"], "case_id": item["case_id"], "case_origin": item["origin"], "requested_input_tokens": item["requested_input_tokens"], "condition": condition, "structured_source_events": item["source_events"], "source_event_hash": item["source_event_hash"], "target": item["target"], "expected_answer": item["expected_answer"], "rendered_prompt": prompt, "prompt_hash": pair["prompt_hash"], "actual_prompt_tokens": pair["actual_prompt_tokens"], "content_tokens": pair["content_tokens"], "prompt_overhead_tokens": pair["prompt_overhead_tokens"], "event_count": len(item["source_events"]), "target_event_indexes": item["target_event_indexes"], "target_event_token_positions": pair["target_event_token_positions"], "target_update_count": 4, "distractor_event_count": len(item["source_events"]) - 4, "model": metadata["model"], "runtime": identity, "inference": metadata["inference"], "output": {"raw_text": raw_text, "normalized_text": normalized, "response": response}, "evaluation": {"passed": bool(passed and not error and not truncated), "score": float(bool(passed and not error and not truncated))}, "failure_class": failure, "diagnostic": diagnostic, "truncated": truncated, "protocol_flags": [], "timing": {"total_ms": round((time.perf_counter() - started) * 1000, 3)}, "error": error, "validator_status": "valid" if not error and not truncated else "invalid"}
            mn004.validate_request_record(record)
            records.append(record)
            print(f"{item['case_id']}@{item['requested_input_tokens']}: {'PASS' if record['evaluation']['passed'] else failure}", flush=True)
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=5)
        (run_dir / "results.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    expected = len(selected)
    valid = len(records) == expected and all(row["validator_status"] == "valid" for row in records)
    mn004.dump_json(run_dir / "summary.json", {"run_id": run_id, "phase": args.phase, "status": "valid" if valid else "invalid", "expected_results": expected, "observed_results": len(records), "passes_by_level": mn004.__dict__.get("_unused", None) or passes_by_level(records), "failure_classes": {kind: sum(row["failure_class"] == kind for row in records) for kind in ("correct", "incorrect_state", "malformed_response", "truncation", "runtime_or_infrastructure_error")}})
    if not valid:
        raise mn004.ContractError(f"{args.phase}: invalid run retained at {run_dir}")
    print(f"Validated phase run: {run_dir}")


if __name__ == "__main__":
    main()
