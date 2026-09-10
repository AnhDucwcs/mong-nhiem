#!/usr/bin/env python3
"""Execute exactly one frozen MN-004 v2 phase; never changes its contract."""
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
import run_mn004 as runtime

PHASES = ("llama_8k_reproduction", "llama_untreated", "llama_ledger", "qwen_8k_untreated", "qwen_8k_ledger")


def phase_spec(phase: str) -> tuple[str, str, list[int], bool]:
    if phase == "llama_8k_reproduction": return "llama-3.2-3b", "natural_language", [8192], True
    if phase == "llama_untreated": return "llama-3.2-3b", "natural_language", [2048, 8192], False
    if phase == "llama_ledger": return "llama-3.2-3b", "ledger", [2048, 8192], False
    if phase == "qwen_8k_untreated": return "qwen3-4b", "natural_language", [8192], False
    if phase == "qwen_8k_ledger": return "qwen3-4b", "ledger", [8192], False
    raise mn004.ContractError(f"unknown v2 phase: {phase}")


def phase_runs(phase: str) -> list[Path]:
    return sorted(path for path in mn004.RUNS.glob("v2-*") if (path / "metadata.json").is_file() and mn004.load_json(path / "metadata.json").get("phase") == phase)


def valid_records(phase: str) -> list[dict[str, Any]] | None:
    runs = phase_runs(phase)
    if not runs: return None
    records = [json.loads(line) for line in (runs[-1] / "results.jsonl").read_text(encoding="utf-8").splitlines() if line]
    return records if records and all(row.get("validator_status") == "valid" and not row.get("truncated") and not row.get("error") for row in records) else None


def enforce_order(phase: str, value: dict[str, Any]) -> None:
    reproduction = valid_records("llama_8k_reproduction")
    if phase == "llama_8k_reproduction":
        if phase_runs(phase): raise mn004.ContractError("v2 reproduction already has retained attempt; no selective rerun")
        return
    if not reproduction: raise mn004.ContractError("execution order blocks phase until valid v2 Llama reproduction")
    reproduction_result = mn004_v2.reproduction_verdict(reproduction, value)
    if reproduction_result != "compatible": raise mn004.ContractError(f"{reproduction_result}: treatment is forbidden")
    if phase == "llama_untreated": return
    untreated = valid_records("llama_untreated")
    if not untreated: raise mn004.ContractError("execution order requires valid v2 Llama untreated evidence")
    if phase == "llama_ledger": return
    ledger = valid_records("llama_ledger")
    if not ledger: raise mn004.ContractError("execution order requires valid v2 Llama ledger evidence")
    if phase == "qwen_8k_untreated": return
    qwen = valid_records("qwen_8k_untreated")
    if not qwen: raise mn004.ContractError("execution order requires valid Qwen untreated evidence")
    if mn004_v2.qwen_verdict(qwen, None, value)["verdict"] != "eligible_pending_ledger":
        raise mn004.ContractError("control_not_qualified: Qwen ledger is forbidden")


def selected_rows(phase: str, value: dict[str, Any]) -> list[dict[str, Any]]:
    _model, _condition, levels, frozen_only = phase_spec(phase)
    rows = [row for row in mn004_v2.authorized_inventory(value) if row["requested_input_tokens"] in levels]
    if frozen_only: rows = [row for row in rows if row["origin"] == "frozen"]
    expected = 6 if frozen_only else 24 if levels == [8192] else 48
    if len(rows) != expected: raise mn004.ContractError("v2 phase selection mismatch")
    return rows


def preflight_pair(value: dict[str, Any], model: str, row: dict[str, Any], condition: str) -> dict[str, Any]:
    filename = value["authority"]["v1_llama_preflight_path"] if model == "llama-3.2-3b" else value["authority"]["v1_qwen_preflight_path"]
    preflight = mn004.load_json(mn004.DEFINITION / filename)
    return mn004_v2.preflight_record(preflight, row)["conditions"][condition]


def git_snapshot() -> dict[str, Any]:
    return {"commit": runtime.command_output(["git", "rev-parse", "HEAD"]).strip(), "dirty": bool(runtime.command_output(["git", "status", "--porcelain", "--untracked-files=all"]).strip())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    configs = mn004.load_json(mn004.CONFIGS / "models.json")
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--models-dir", type=Path, default=Path(configs["default_models_dir"]))
    parser.add_argument("--llama-server", type=Path, default=Path(configs["default_llama_server"]))
    parser.add_argument("--port", type=int, default=18624)
    args = parser.parse_args()
    value = mn004_v2.validate_authority(); mn004_v2.validate_retained_preflight(value); enforce_order(args.phase, value)
    repo = git_snapshot()
    if repo["dirty"]: raise mn004.ContractError("canonical v2 run requires clean worktree before evidence creation")
    model_key, condition, _levels, _frozen = phase_spec(args.phase)
    config, model = value["models"][model_key], args.models_dir / value["models"][model_key]["file"]
    if not model.is_file() or not args.llama_server.is_file() or runtime.file_digest(model) != config["sha256"]:
        raise mn004.ContractError("model/runtime dependency mismatch")
    identity = runtime.runtime_identity(args.llama_server)
    if any(identity[field] != value["runtime"][field] for field in ("backend", "version", "build", "commit")):
        raise mn004.ContractError("runtime identity mismatch")
    rows = selected_rows(args.phase, value)
    created = dt.datetime.now(dt.UTC); run_id = f"v2-{created:%Y%m%dT%H%M%SZ}-{args.phase}-{uuid.uuid4().hex[:8]}"; run_dir = mn004.RUNS / run_id; raw = run_dir / "raw"; raw.mkdir(parents=True)
    metadata = {"run_id": run_id, "created_at": created.isoformat(), "phase": args.phase, "v2_definition_fingerprint": mn004_v2.definition_fingerprint(value), "v1_inventory_fingerprint": value["authority"]["v1_inventory_fingerprint"], "model": {"key": model_key, "file": model.name, "sha256": config["sha256"]}, "runtime": identity, "hardware": runtime.hardware_identity(), "inference": {**value["runtime"], "chat_template_kwargs": config["chat_template_kwargs"]}, "selection": {"cases": len(rows), "levels": sorted({row["requested_input_tokens"] for row in rows}), "condition": condition}, "repository": repo}
    mn004.dump_json(run_dir / "metadata.json", metadata)
    records: list[dict[str, Any]] = []; process: subprocess.Popen[Any] | None = None
    try:
        process = runtime.start_server(args.llama_server, model, value, config["chat_template_kwargs"], args.port, raw / "llama-server.stdout.txt", raw / "llama-server.stderr.txt")
        client = mn004.ServerClient(f"http://127.0.0.1:{args.port}", config["chat_template_kwargs"]); runtime.wait_for_server(process, f"http://127.0.0.1:{args.port}")
        for row in rows:
            prompt = row["natural_prompt" if condition == "natural_language" else "ledger_prompt"]; pair = preflight_pair(value, model_key, row, condition); started = time.perf_counter(); response: dict[str, Any] | None = None; error = None; raw_text = ""
            try:
                _request, response = client.complete(prompt, value["runtime"]); raw_text = response["choices"][0]["message"].get("content") or ""
                if response.get("usage", {}).get("prompt_tokens") != pair["actual_prompt_tokens"]: raise mn004.ContractError("completion token accounting differs from retained preflight")
            except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError, mn004.ContractError) as exc:
                error = {"type": "model_request_error", "message": f"{type(exc).__name__}: {exc}"}
            truncated = bool(response and response.get("choices") and response["choices"][0].get("finish_reason") == "length")
            failure, diagnostic, normalized = mn004.classify_output(row["target"], row["expected_answer"], row["source_events"], raw_text, error)
            if truncated: failure, diagnostic = "truncation", None
            passed, _ = mn004.evaluate(row["target"], row["expected_answer"], raw_text)
            record = {"evidence_schema_version": value["evidence_schema_version"], "definition_fingerprint": mn004_v2.definition_fingerprint(value), "inventory_fingerprint": value["authority"]["v1_inventory_fingerprint"], "case_id": row["case_id"], "case_origin": row["origin"], "requested_input_tokens": row["requested_input_tokens"], "condition": condition, "structured_source_events": row["source_events"], "source_event_hash": row["source_event_hash"], "target": row["target"], "expected_answer": row["expected_answer"], "rendered_prompt": prompt, "prompt_hash": pair["prompt_hash"], "actual_prompt_tokens": pair["actual_prompt_tokens"], "content_tokens": pair["content_tokens"], "prompt_overhead_tokens": pair["prompt_overhead_tokens"], "event_count": len(row["source_events"]), "target_event_indexes": row["target_event_indexes"], "target_event_token_positions": pair["target_event_token_positions"], "target_update_count": 4, "distractor_event_count": len(row["source_events"])-4, "model": metadata["model"], "runtime": identity, "inference": metadata["inference"], "output": {"raw_text": raw_text, "normalized_text": normalized, "response": response}, "evaluation": {"passed": bool(passed and not error and not truncated), "score": float(bool(passed and not error and not truncated))}, "failure_class": failure, "diagnostic": diagnostic, "truncated": truncated, "protocol_flags": [], "timing": {"total_ms": round((time.perf_counter()-started)*1000, 3)}, "error": error, "validator_status": "valid" if not error and not truncated else "invalid"}
            mn004.validate_request_record(record); records.append(record); print(f"{row['case_id']}@{row['requested_input_tokens']}: {'PASS' if record['evaluation']['passed'] else failure}", flush=True)
    finally:
        if process and process.poll() is None:
            process.terminate()
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=10)
        (run_dir / "results.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False)+"\n" for row in records), encoding="utf-8")
    valid = len(records) == len(rows) and all(row["validator_status"] == "valid" for row in records)
    summary = {"run_id": run_id, "phase": args.phase, "status": "valid" if valid else "invalid", "expected_results": len(rows), "observed_results": len(records), "passes_by_level": {str(level): mn004_v2.passes(records, level) for level in sorted({row['requested_input_tokens'] for row in rows})}, "failure_classes": {kind: sum(row["failure_class"] == kind for row in records) for kind in ("correct", "incorrect_state", "malformed_response", "truncation", "runtime_or_infrastructure_error")}}
    mn004.dump_json(run_dir / "summary.json", summary)
    if not valid: raise mn004.ContractError(f"infrastructure_failure: invalid run retained at {run_dir}")
    print(f"Validated v2 phase run: {run_dir}")


if __name__ == "__main__": main()
