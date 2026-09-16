#!/usr/bin/env python3
"""Execute only the prospectively frozen MN-006 label-selection D1 diagnostic."""
from __future__ import annotations

import argparse
import subprocess
import time
import urllib.error
from pathlib import Path
from typing import Any

import run_mn006_baseline as baseline
from mn006.label_selection_execution import (
    D1_RUN_ID,
    EVALUATOR_VERSION,
    EVIDENCE_SCHEMA_VERSION,
    EXPECTED_DIAGNOSTIC_PLAN_SHA256,
    PARSER_VERSION,
    REQUEST_ORDER_CONTRACT,
    RUNTIME_CONTRACT_VERSION,
    build_d1_request_plan,
    build_request_payload,
    evaluate_raw_output,
    plan_entry,
    summarize_d1_records,
    validate_d1_run_directory,
)

RUNS = Path(__file__).resolve().parents[1] / "runs"
DIAGNOSTIC_CONTRACT_VERSION = "mn006-label-selection-diagnostic-v1"


def contract_metadata(executor_commit: str) -> dict[str, object]:
    """Return future-run identity without creating evidence or contacting a model."""
    return {
        "diagnostic_contract_version": DIAGNOSTIC_CONTRACT_VERSION,
        "diagnostic_plan_sha256": EXPECTED_DIAGNOSTIC_PLAN_SHA256,
        "d1_stage": "D1_direct_mapping",
        "evaluator_version": EVALUATOR_VERSION,
        "executor_commit": executor_commit,
        "grammar_ids": ["A_then_B", "B_then_A"],
        "mappings": ["M1_equal_A", "M2_equal_B"],
        "parser_version": PARSER_VERSION,
        "run_id": D1_RUN_ID,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "source_ordinals": [0, 1, 2, 3],
    }


def dry_construction() -> tuple[dict[str, object], ...]:
    """Build and validate all D1 payloads without network, server, or evidence writes."""
    cases = build_d1_request_plan()
    entries: list[dict[str, object]] = []
    for case in cases:
        entry = plan_entry(case)
        payload = build_request_payload(case)
        if payload["messages"][0]["content"] != entry["public_prompt"]:
            raise baseline.AttemptInfrastructureError("D1 payload prompt differs from frozen planner")
        if payload["grammar"] != entry["grammar"]:
            raise baseline.AttemptInfrastructureError("D1 payload grammar differs from frozen planner")
        entries.append({**entry, "payload": payload})
    if len(entries) != 16:
        raise baseline.AttemptInfrastructureError("D1 dry construction differs from frozen 16-request boundary")
    return tuple(entries)


def _require_preflight(model: Path, server: Path) -> tuple[tuple[Any, ...], dict[str, Any], dict[str, Any], str]:
    cases = build_d1_request_plan()
    if not model.is_file() or baseline.file_sha256(model) != baseline.EXPECTED_MODEL_SHA256:
        raise baseline.AttemptInfrastructureError("model file is missing or differs from the qualified Llama artifact")
    if not server.is_file():
        raise baseline.AttemptInfrastructureError("llama-server executable is unavailable")
    if subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, check=False).stdout.strip():
        raise baseline.AttemptInfrastructureError("D1 execution requires a clean repository worktree")
    base_url = f"http://{baseline.HOST}:{baseline.PORT}"
    pre_environment = baseline.environment_snapshot()
    baseline.require_clean_environment(pre_environment, base_url)
    runtime = baseline.runtime_identity(server)
    return cases, pre_environment, runtime, base_url


def run(model: Path = baseline.DEFAULT_MODEL, server: Path = baseline.DEFAULT_SERVER) -> Path:
    """Run D1 once with no retries; D2 is intentionally unreachable from this executor."""
    cases, pre_environment, runtime, base_url = _require_preflight(model, server)
    run_dir = RUNS / D1_RUN_ID
    if run_dir.exists():
        raise baseline.AttemptInfrastructureError(f"{D1_RUN_ID} evidence directory already exists")
    executor_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    command = baseline.server_command(server, model)
    run_dir.mkdir(parents=True)
    raw_dir = run_dir / "raw"
    raw_dir.mkdir()
    metadata = {
        **contract_metadata(executor_commit),
        "created_at": baseline.utc_now(),
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "model": {
            "file": model.name,
            "path": str(model),
            "sha256": baseline.EXPECTED_MODEL_SHA256,
            "size_bytes": model.stat().st_size,
            "subject": "llama-3.2-3b",
        },
        "repository": {"commit": executor_commit, "dirty": False},
        "request_order_contract": REQUEST_ORDER_CONTRACT,
        "runtime": runtime,
        "runtime_parameters": baseline.INFERENCE,
        "server_command": command,
        "start_environment": pre_environment,
    }
    baseline.write_new_canonical_json(run_dir / "metadata.json", metadata)
    (run_dir / "results.jsonl").open("xb").close()
    stdout_path = raw_dir / "llama-server.stdout.txt"
    stderr_path = raw_dir / "llama-server.stderr.txt"
    process: subprocess.Popen[Any] | None = None
    stdout_handle: Any = None
    stderr_handle: Any = None
    records: list[dict[str, Any]] = []
    lifecycle: dict[str, Any] = {"command": command, "expected_termination": False, "pid": None, "started": False}
    try:
        stdout_handle = stdout_path.open("xb")
        stderr_handle = stderr_path.open("xb")
        process = subprocess.Popen(command, stdout=stdout_handle, stderr=stderr_handle)
        lifecycle.update({"pid": process.pid, "process_started_at": baseline.utc_now(), "started": True})
        lifecycle["health_at_ready"] = baseline.wait_for_server(process, base_url)
        lifecycle["environment_at_ready"] = baseline.environment_snapshot()
        if not baseline.health(base_url)["reachable"]:
            raise baseline.AttemptInfrastructureError("server lost health before D1 request 1")
        for case in cases:
            entry = plan_entry(case)
            request_payload = build_request_payload(case)
            expected_tokens = None
            raw_response_bytes: bytes | None = None
            response: dict[str, Any] | None = None
            error: dict[str, str] | None = None
            started = time.perf_counter()
            try:
                expected_tokens = baseline.prompt_tokens(base_url, request_payload["messages"][0]["content"])
                raw_response_bytes, response = baseline.post(
                    base_url,
                    "/v1/chat/completions",
                    request_payload,
                    timeout=baseline.INFERENCE["request_timeout_seconds"],
                )
                raw_text = response["choices"][0]["message"].get("content") or ""
                observed_tokens = response.get("usage", {}).get("prompt_tokens")
                if observed_tokens != expected_tokens:
                    raise baseline.AttemptInfrastructureError(
                        f"prompt-token inconsistency: expected={expected_tokens}, observed={observed_tokens}"
                    )
            except (baseline.AttemptInfrastructureError, KeyError, OSError, TimeoutError, ValueError, urllib.error.URLError) as exc:
                raw_text = ""
                error = {"message": f"{type(exc).__name__}: {exc}", "type": "infrastructure_error"}
            evaluation = evaluate_raw_output(case, raw_text)
            complete = error is None
            record = {
                **entry,
                "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
                "evaluation": evaluation,
                "expected_prompt_tokens": expected_tokens,
                "finish_reason": response.get("choices", [{}])[0].get("finish_reason") if response else None,
                "infrastructure_status": "complete" if complete else "failed",
                "model": metadata["model"],
                "raw_output": raw_text,
                "raw_request_payload": request_payload,
                "raw_response_payload_utf8": raw_response_bytes.decode("utf-8", errors="replace") if raw_response_bytes is not None else None,
                "response": response,
                "run_id": D1_RUN_ID,
                "runtime": runtime,
                "timing": {"completed_at": baseline.utc_now(), "total_ms": round((time.perf_counter() - started) * 1000, 3)},
                "usage": response.get("usage") if response else None,
                "error": error,
            }
            baseline.append_canonical_jsonl(run_dir / "results.jsonl", record)
            records.append(record)
            print(f"{case.request_ordinal:02d}/16 {case.record_id}: {'OK' if complete else 'INFRASTRUCTURE_FAILURE'}", flush=True)
            if not complete:
                break
    except baseline.AttemptInfrastructureError as exc:
        if not records:
            records.append({"run_id": D1_RUN_ID, "error": {"message": str(exc), "type": "startup_infrastructure_error"}, "infrastructure_status": "failed", "request_ordinal": 0})
            baseline.append_canonical_jsonl(run_dir / "results.jsonl", records[-1])
    finally:
        if process is not None:
            if process.poll() is None:
                lifecycle["expected_termination"] = True
                process.terminate()
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=20)
            lifecycle.update({"exit_code": process.poll(), "process_exit_observed_at": baseline.utc_now(), "health_after_cleanup": baseline.health(base_url)})
        if stdout_handle is not None:
            stdout_handle.close()
        if stderr_handle is not None:
            stderr_handle.close()
        lifecycle["end_environment"] = baseline.environment_snapshot()
        baseline.write_new_canonical_json(run_dir / "server-lifecycle.json", lifecycle)
    if records and records[0].get("request_ordinal") == 0:
        summary = {"classification": "infrastructure_invalid", "completed_requests": 0, "expected_requests": len(cases), "infrastructure_failure_count": 1, "outcome": "infrastructure_invalid"}
    else:
        summary = summarize_d1_records(records, cases)
    baseline.write_new_canonical_json(run_dir / "summary.json", summary)
    if summary["outcome"] == "protocol_valid":
        validate_d1_run_directory(run_dir)
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="construct the frozen D1 payloads without server, network, or evidence writes")
    arguments = parser.parse_args()
    if arguments.dry_run:
        print(len(dry_construction()))
        return
    print(run())


if __name__ == "__main__":
    main()
