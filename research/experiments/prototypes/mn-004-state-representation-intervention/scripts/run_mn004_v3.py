"""Execute one frozen MN-004 v3 phase."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time
import urllib.error
import uuid
from pathlib import Path
from typing import Any

import mn004
import mn004_v2
import mn004_v3
import run_mn004 as runtime

PHASES = ("llama_8k_reproduction", "llama_untreated", "llama_ledger", "qwen_8k_untreated", "qwen_8k_ledger")


def phase_spec(phase: str) -> tuple[str, str, list[int], bool]:
    mapping = {
        "llama_8k_reproduction": ("llama-3.2-3b", "natural_language", [8192], True),
        "llama_untreated": ("llama-3.2-3b", "natural_language", [2048, 8192], False),
        "llama_ledger": ("llama-3.2-3b", "ledger", [2048, 8192], False),
        "qwen_8k_untreated": ("qwen3-4b", "natural_language", [8192], False),
        "qwen_8k_ledger": ("qwen3-4b", "ledger", [8192], False),
    }
    return mapping[phase]


def phase_records(phase: str) -> list[dict[str, Any]] | None:
    runs = sorted(path for path in mn004.RUNS.glob("v3-*") if (path / "metadata.json").is_file() and mn004.load_json(path / "metadata.json").get("phase") == phase)
    if not runs:
        return None
    return [json.loads(line) for line in (runs[-1] / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]


def enforce_order(phase: str, definition: dict[str, Any]) -> None:
    reproduction = phase_records("llama_8k_reproduction")
    if phase == "llama_8k_reproduction":
        if reproduction:
            raise mn004.ContractError("v3 reproduction is already retained; no selective rerun")
        return
    if not reproduction:
        raise mn004.ContractError("execution order requires Llama reproduction")
    if mn004_v3.reproduction_verdict(reproduction, definition) != "compatible":
        raise mn004.ContractError("baseline_drift or invalid reproduction blocks v3")
    if phase == "llama_untreated":
        return
    untreated = phase_records("llama_untreated")
    if not untreated or not all(mn004_v3.record_is_valid(row) for row in untreated):
        raise mn004.ContractError("protocol/infrastructure failure blocks later phases")
    if phase == "llama_ledger":
        return
    ledger = phase_records("llama_ledger")
    if not ledger or not all(mn004_v3.record_is_valid(row) for row in ledger):
        raise mn004.ContractError("complete Llama ledger phase required")
    if phase == "qwen_8k_untreated":
        return
    qwen = phase_records("qwen_8k_untreated")
    if not qwen or mn004_v3.qwen_verdict(qwen, None, definition)["verdict"] != "eligible_pending_ledger":
        raise mn004.ContractError("control_not_qualified blocks Qwen ledger")


def select_rows(phase: str, definition: dict[str, Any]) -> list[dict[str, Any]]:
    _model, _condition, levels, frozen_only = phase_spec(phase)
    rows = [row for row in mn004_v3.inventory(definition) if row["requested_input_tokens"] in levels]
    if frozen_only:
        rows = [row for row in rows if row["origin"] == "frozen"]
    expected = 6 if frozen_only else 24 if levels == [8192] else 48
    if len(rows) != expected:
        raise mn004.ContractError("v3 selection mismatch")
    return rows


def preflight_pair(model_key: str, row: dict[str, Any], condition: str) -> dict[str, Any]:
    filename = "preflight-llama-3.2-3b.json" if model_key == "llama-3.2-3b" else "preflight-qwen3-4b.json"
    return mn004_v2.preflight_record(mn004.load_json(mn004.DEFINITION / filename), row)["conditions"][condition]


def run_phase(args: argparse.Namespace) -> None:
    definition = mn004_v3.validate_authority()
    mn004_v3.validate_offline()
    enforce_order(args.phase, definition)
    model_key, condition, _levels, _frozen_only = phase_spec(args.phase)
    config = definition["models"][model_key]
    model = args.models_dir / config["file"]
    if not model.is_file() or runtime.file_digest(model) != config["sha256"]:
        raise mn004.ContractError("model artifact mismatch")
    identity = runtime.runtime_identity(args.llama_server)
    if any(identity[key] != definition["runtime"][key] for key in ("backend", "version", "build", "commit")):
        raise mn004.ContractError("runtime identity mismatch")
    repo = {"commit": runtime.command_output(["git", "rev-parse", "HEAD"]).strip(), "dirty": bool(runtime.command_output(["git", "status", "--porcelain", "--untracked-files=all"]).strip())}
    if repo["dirty"]:
        raise mn004.ContractError("canonical v3 run requires a clean worktree")
    rows = select_rows(args.phase, definition)
    created = dt.datetime.now(dt.UTC)
    run_id = f"v3-{created:%Y%m%dT%H%M%SZ}-{args.phase}-{uuid.uuid4().hex[:8]}"
    run_dir, raw = mn004.RUNS / run_id, mn004.RUNS / run_id / "raw"
    raw.mkdir(parents=True)
    metadata = {"run_id": run_id, "created_at": created.isoformat(), "phase": args.phase, "v3_definition_fingerprint": mn004_v3.fingerprint(definition), "v1_inventory_fingerprint": definition["authority"]["v1_inventory_fingerprint"], "model": {"key": model_key, "file": model.name, "sha256": config["sha256"]}, "runtime": identity, "hardware": runtime.hardware_identity(), "inference": {**definition["runtime"], "chat_template_kwargs": config["chat_template_kwargs"]}, "selection": {"cases": len(rows), "levels": sorted({row["requested_input_tokens"] for row in rows}), "condition": condition}, "repository": repo}
    mn004.dump_json(run_dir / "metadata.json", metadata)
    process: subprocess.Popen[Any] | None = None
    records: list[dict[str, Any]] = []
    try:
        process = runtime.start_server(args.llama_server, model, definition, config["chat_template_kwargs"], args.port, raw / "llama-server.stdout.txt", raw / "llama-server.stderr.txt")
        url = f"http://127.0.0.1:{args.port}"
        runtime.wait_for_server(process, url)
        client = mn004.ServerClient(url, config["chat_template_kwargs"])
        for row in rows:
            prompt = row["natural_prompt" if condition == "natural_language" else "ledger_prompt"]
            preflight = preflight_pair(model_key, row, condition)
            started, response, error, raw_text, protocol_flags = time.perf_counter(), None, None, "", []
            try:
                _request, response = client.complete(prompt, definition["runtime"])
                raw_text = response["choices"][0]["message"].get("content") or ""
                if response.get("usage", {}).get("prompt_tokens") != preflight["actual_prompt_tokens"]:
                    protocol_flags.append("prompt_token_mismatch")
            except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError, mn004.ContractError) as exc:
                error = {"type": "request_error", "message": f"{type(exc).__name__}: {exc}"}
            outcome = mn004_v3.classify_response(row, raw_text, response, error)
            protocol_valid = not protocol_flags and outcome["validity"] != "infrastructure_failure"
            infrastructure_status = "complete" if outcome["validity"] != "infrastructure_failure" else "failed"
            record = {"v3_definition_fingerprint": mn004_v3.fingerprint(definition), "case_id": row["case_id"], "case_origin": row["origin"], "requested_input_tokens": row["requested_input_tokens"], "condition": condition, "structured_source_events": row["source_events"], "source_event_hash": row["source_event_hash"], "target": row["target"], "expected_answer": row["expected_answer"], "rendered_prompt": prompt, "prompt_hash": preflight["prompt_hash"], "actual_prompt_tokens": preflight["actual_prompt_tokens"], "content_tokens": preflight["content_tokens"], "prompt_overhead_tokens": preflight["prompt_overhead_tokens"], "event_count": len(row["source_events"]), "target_event_indexes": row["target_event_indexes"], "target_event_token_positions": preflight["target_event_token_positions"], "model": metadata["model"], "runtime": identity, "inference": metadata["inference"], "output": {"raw_text": raw_text, "normalized_text": outcome["normalized"], "response": response}, "evaluation": {"passed": outcome["passed"], "score": float(outcome["passed"])}, "failure_class": outcome["failure_class"], "diagnostic": outcome["diagnostic"], "protocol_valid": protocol_valid, "protocol_flags": protocol_flags, "infrastructure_status": infrastructure_status, "input_truncated": outcome["input_truncated"], "output_limit_reached": outcome["output_limit_reached"], "error": error, "validator_status": "valid" if protocol_valid and infrastructure_status == "complete" else "invalid", "timing": {"total_ms": round((time.perf_counter() - started) * 1000, 3)}}
            records.append(record)
            print(f"{row['case_id']}@{row['requested_input_tokens']}: {'PASS' if outcome['passed'] else outcome['failure_class']}", flush=True)
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=15)
        (run_dir / "results.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    if len(records) != len(rows) or any(row["infrastructure_status"] == "failed" for row in records):
        status = "infrastructure_failure"
    elif not all(mn004_v3.record_is_valid(row) for row in records):
        status = "invalid_comparison"
    else:
        status = "valid"
    summary = {"run_id": run_id, "phase": args.phase, "status": status, "expected_results": len(rows), "observed_results": len(records), "passes_by_level": {str(level): mn004_v3.passes(records, level) for level in sorted({row["requested_input_tokens"] for row in rows})}, "failure_classes": {name: sum(row["failure_class"] == name for row in records) for name in ("correct", "incorrect_state", "malformed_response", "output_token_limit_reached", "infrastructure_failure")}}
    mn004.dump_json(run_dir / "summary.json", summary)
    if status != "valid":
        raise mn004.ContractError(status)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    configs = mn004.load_json(mn004.CONFIGS / "models.json")
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--models-dir", type=Path, default=Path(configs["default_models_dir"]))
    parser.add_argument("--llama-server", type=Path, default=Path(configs["default_llama_server"]))
    parser.add_argument("--port", type=int, default=18634)
    run_phase(parser.parse_args())


if __name__ == "__main__":
    main()
