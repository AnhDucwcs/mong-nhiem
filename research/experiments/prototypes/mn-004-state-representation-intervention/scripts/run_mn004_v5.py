#!/usr/bin/env python3
"""Execute one frozen MN-004 v5 canonical phase with v4 telemetry safeguards."""
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
import mn004_v3
import mn004_v4
import mn004_v5
import run_mn004 as runtime
import run_mn004_v4 as telemetry


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def _records_path(run_dir: Path) -> Path:
    return run_dir / "results.jsonl"


def _write_records(run_dir: Path, records: list[dict[str, Any]]) -> None:
    _records_path(run_dir).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")


def _first_failure(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((row for row in records if row["completion_status"] in {"protocol_invalid", "infrastructure_failure"}), None)


def _phase_outcome(phase: str, records: list[dict[str, Any],], expected: int, definition: dict[str, Any]) -> str:
    failure = _first_failure(records)
    if failure:
        return failure["completion_status"]
    if len(records) != expected:
        return "infrastructure_failure"
    if phase == "llama_8k_reproduction": return mn004_v5.reproduction_verdict(records, definition)
    return "phase_completed"


def run_phase(args: argparse.Namespace) -> dict[str, Any]:
    definition = mn004_v5.validate_authority(); mn004_v5.validate_offline()
    if not mn004_v5.phase_allowed(args.phase):
        raise mn004.ContractError(f"v5 execution order blocks {args.phase}")
    if runtime.command_output(["git", "status", "--porcelain", "--untracked-files=all"]).strip():
        raise mn004.ContractError("canonical v5 phase requires a clean worktree")
    rows, condition, model_key = mn004_v5.phase_rows(args.phase, definition), mn004_v5.condition_for(args.phase), mn004_v5.model_for(args.phase)
    model_config = definition["models"][model_key]; model = args.models_dir / model_config["file"]
    if not model.is_file() or runtime.file_digest(model) != model_config["sha256"]:
        raise mn004.ContractError("v5 model artifact mismatch")
    identity = runtime.runtime_identity(args.llama_server)
    if any(identity[key] != definition["runtime"][key] for key in ("backend", "version", "build", "commit")):
        raise mn004.ContractError("v5 runtime identity mismatch")
    baseline = telemetry.gpu_snapshot(); telemetry.require_telemetry(baseline)
    created = dt.datetime.now(dt.UTC); run_id = f"v5-{created:%Y%m%dT%H%M%SZ}-{args.phase}-{uuid.uuid4().hex[:8]}"
    run_dir, raw = mn004.RUNS / run_id, mn004.RUNS / run_id / "raw"; raw.mkdir(parents=True)
    metadata: dict[str, Any] = {
        "run_id": run_id, "created_at": created.isoformat(), "phase": args.phase,
        "v5_definition_fingerprint": mn004_v5.fingerprint(definition), "v1_inventory_fingerprint": definition["authority"]["v1_inventory_fingerprint"],
        "model": {"key": model_key, "file": model.name, "sha256": model_config["sha256"]}, "runtime": identity,
        "inference": {**definition["runtime"], "chat_template_kwargs": model_config["chat_template_kwargs"]},
        "repository": {"commit": runtime.command_output(["git", "rev-parse", "HEAD"]).strip(), "dirty": False},
        "selection": {"condition": condition, "case_ids": [row["case_id"] for row in rows], "levels": [row["requested_input_tokens"] for row in rows]},
        "telemetry": {"before_phase": baseline},
    }
    mn004.dump_json(run_dir / "metadata.json", metadata)
    if baseline["compute_processes"]:
        summary = {"run_id": run_id, "phase": args.phase, "expected_results": len(rows), "observed_results": 0, "completed_requests": 0, "outcome": "environment_contaminated", "server_lifecycle": {"started": False}, "telemetry": {"before_phase": baseline}}
        mn004.dump_json(run_dir / "summary.json", summary); return summary
    url = f"http://127.0.0.1:{args.port}"
    if telemetry.health(url)["reachable"]:
        summary = {"run_id": run_id, "phase": args.phase, "expected_results": len(rows), "observed_results": 0, "completed_requests": 0, "outcome": "protocol_invalid", "server_lifecycle": {"started": False, "reason": "port_already_serving"}}
        mn004.dump_json(run_dir / "summary.json", summary); return summary
    command = telemetry.build_server_command(args.llama_server, model, {"runtime": definition["runtime"], "model": model_config}, args.port)
    stdout, stderr = raw / "llama-server.stdout.txt", raw / "llama-server.stderr.txt"
    process: subprocess.Popen[Any] | None = None; stdout_handle: Any = None; stderr_handle: Any = None; records: list[dict[str, Any]] = []
    lifecycle: dict[str, Any] = {"started": False, "command": command, "pid": None, "process_started_at": None, "health_at_ready": None, "expected_termination": False}
    try:
        process, stdout_handle, stderr_handle = telemetry.start_server(command, stdout, stderr)
        lifecycle.update({"started": True, "pid": process.pid, "process_started_at": utc_now()})
        runtime.wait_for_server(process, url); lifecycle["health_at_ready"] = telemetry.health(url)
        ready = telemetry.gpu_snapshot(); telemetry.require_telemetry(ready); metadata["telemetry"]["server_ready"] = ready; mn004.dump_json(run_dir / "metadata.json", metadata)
        client = mn004.ServerClient(url, model_config["chat_template_kwargs"])

        def request(ordinal: int, row: dict[str, Any]) -> dict[str, Any]:
            pair = mn004_v5.preflight_pair(row, model_key, condition, definition)
            prompt = row["natural_prompt" if condition == "natural_language" else "ledger_prompt"]
            before = telemetry.gpu_snapshot(); telemetry.require_telemetry(before)
            started, timer = utc_now(), time.perf_counter(); response: dict[str, Any] | None = None; infra: dict[str, Any] | None = None; flags: list[str] = []
            try:
                _request, response = client.complete(prompt, definition["runtime"])
                if response.get("usage", {}).get("prompt_tokens") != pair["actual_prompt_tokens"]: flags.append("prompt_token_mismatch")
            except mn004.ContractError as exc:
                flags.append(f"contract_error:{exc}")
            except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError) as exc:
                infra = {"type": "request_error", "message": f"{type(exc).__name__}: {exc}"}
            ended = utc_now(); raw_text = response.get("choices", [{}])[0].get("message", {}).get("content") if response else ""
            classification = mn004_v3.classify_response(row, raw_text or "", response, infra)
            record: dict[str, Any] = {
                "evidence_schema_version": definition["evidence_schema_version"], "v5_definition_fingerprint": mn004_v5.fingerprint(definition), "v1_inventory_fingerprint": definition["authority"]["v1_inventory_fingerprint"],
                "request_ordinal": ordinal, "case_id": row["case_id"], "case_origin": row["origin"], "requested_input_tokens": row["requested_input_tokens"], "condition": condition,
                "structured_source_events": row["source_events"], "source_event_hash": row["source_event_hash"], "target": row["target"], "expected_answer": row["expected_answer"],
                "rendered_prompt": prompt, "prompt_hash": pair["prompt_hash"], "actual_prompt_tokens": pair["actual_prompt_tokens"], "content_tokens": pair["content_tokens"], "prompt_overhead_tokens": pair["prompt_overhead_tokens"],
                "event_count": len(row["source_events"]), "target_event_indexes": row["target_event_indexes"], "target_event_token_positions": pair["target_event_token_positions"], "target_update_count": 4, "distractor_event_count": len(row["source_events"]) - 4,
                "model": metadata["model"], "runtime": identity, "inference": metadata["inference"], "response": response, "raw_output": raw_text, "finish_reason": response.get("choices", [{}])[0].get("finish_reason") if response else None,
                "protocol_valid": not flags and not infra, "infrastructure_status": "complete" if not infra else "failed", "validator_status": "valid" if not flags and not infra else "invalid", "input_truncated": False,
                "output_limit_reached": classification["output_limit_reached"], "evaluation": {"passed": classification["passed"], "score": float(classification["passed"])}, "failure_class": classification["failure_class"], "diagnostic": classification["diagnostic"], "normalized_output": classification["normalized"],
                "protocol_flags": flags, "error": infra, "request_started_at": started, "request_ended_at": ended, "latency_ms": round((time.perf_counter() - timer) * 1000, 3), "gpu_before_request": before, "completion_status": "complete", "failure_attachment": None,
            }
            if infra:
                record["completion_status"] = "infrastructure_failure"; record["failure_attachment"] = {"captured_at": utc_now(), "error": infra, "stderr_tail": telemetry.stderr_tail(stderr, definition["operational"]["stderr_tail_bytes"]), "process": telemetry.poll_after_failure(process, definition["operational"]["post_failure_process_poll_seconds"]), "health": telemetry.health(url), "gpu": telemetry.gpu_snapshot()}
            elif flags:
                record["completion_status"] = "protocol_invalid"; record["failure_attachment"] = {"captured_at": utc_now(), "protocol_flags": flags, "health": telemetry.health(url), "gpu": telemetry.gpu_snapshot()}
            else:
                record["gpu_after_request"] = telemetry.gpu_snapshot(); telemetry.require_telemetry(record["gpu_after_request"])
            return record

        records = mn004_v5.execute_fail_fast(rows, request)
    except mn004.ContractError as exc:
        records.append({"request_ordinal": 0, "case_id": None, "requested_input_tokens": None, "completion_status": "infrastructure_failure" if "llama-server" in str(exc) else "protocol_invalid", "protocol_valid": False, "infrastructure_status": "failed", "validator_status": "invalid", "input_truncated": False, "error": {"type": "contract_error", "message": str(exc)}, "failure_attachment": {"captured_at": utc_now(), "stderr_tail": telemetry.stderr_tail(stderr, definition["operational"]["stderr_tail_bytes"]), "gpu": telemetry.gpu_snapshot()}})
    finally:
        if process:
            if process.poll() is None:
                lifecycle["expected_termination"] = True; process.terminate()
                try: process.wait(timeout=15)
                except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=15)
            lifecycle.update({"process_exit_observed_at": utc_now(), "exit_code": process.poll(), "alive_after_cleanup": process.poll() is None, "health_after_cleanup": telemetry.health(url)})
        if stdout_handle: stdout_handle.close()
        if stderr_handle: stderr_handle.close()
        _write_records(run_dir, records)
    outcome = _phase_outcome(args.phase, records, len(rows), definition); failure = _first_failure(records); last = records[records.index(failure)-1]["case_id"] if failure and records.index(failure) else None
    summary = {"run_id": run_id, "phase": args.phase, "expected_results": len(rows), "observed_results": len(records), "completed_requests": sum(row["completion_status"] == "complete" for row in records), "outcome": outcome, "first_failure": failure, "last_successful_case_id": last, "server_lifecycle": lifecycle, "failure_classes": {kind: sum(row.get("failure_class") == kind for row in records) for kind in ("correct", "incorrect_state", "malformed_response", "output_token_limit_reached", "infrastructure_failure")}}
    mn004.dump_json(run_dir / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); configs = mn004.load_json(mn004.CONFIGS / "models.json")
    parser.add_argument("--phase", choices=mn004_v5.PHASES, required=True); parser.add_argument("--models-dir", type=Path, default=Path(configs["default_models_dir"])); parser.add_argument("--llama-server", type=Path, default=Path(configs["default_llama_server"])); parser.add_argument("--port", type=int, default=18654)
    print(json.dumps(run_phase(parser.parse_args()), indent=2))


if __name__ == "__main__": main()
