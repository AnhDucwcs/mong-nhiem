#!/usr/bin/env python3
"""Execute only the frozen MN-006 S1 direct-relation diagnostic without retries."""
from __future__ import annotations

import argparse
import subprocess
import time
import urllib.error
from pathlib import Path
from typing import Any

import run_mn006_baseline as baseline
from mn006 import output_selection_s1_execution as execution

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


def _pending_directory() -> Path:
    return RUNS / f".{execution.S1_RUN_ID}.pending"


def _invalid_directory() -> Path:
    return RUNS / f"{execution.S1_RUN_ID}.infrastructure-invalid"


def _require_preflight(
    model: Path, server: Path
) -> tuple[tuple[execution.S1Request, ...], dict[str, Any], dict[str, Any], str]:
    """Fail closed before a future first inference request or evidence staging."""
    requests = execution.build_s1_request_plan()
    if not model.is_file() or baseline.file_sha256(model) != baseline.EXPECTED_MODEL_SHA256:
        raise baseline.AttemptInfrastructureError("model file is missing or differs from the qualified Llama artifact")
    if not server.is_file():
        raise baseline.AttemptInfrastructureError("llama-server executable is unavailable")
    if subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, check=False).stdout.strip():
        raise baseline.AttemptInfrastructureError("S1 execution requires a clean repository worktree")
    base_url = f"http://{baseline.HOST}:{baseline.PORT}"
    pre_environment = baseline.environment_snapshot()
    baseline.require_clean_environment(pre_environment, base_url)
    runtime = baseline.runtime_identity(server)
    if execution.REQUEST_PARAMETERS != {
        "chat_template_kwargs": {},
        "max_tokens": baseline.INFERENCE["output_tokens"],
        "seed": baseline.INFERENCE["seed"],
        "temperature": baseline.INFERENCE["temperature"],
    }:
        raise baseline.AttemptInfrastructureError("S1 request parameters differ from the frozen qualified runtime")
    return requests, pre_environment, runtime, base_url


def _write_integrity_manifest(run_dir: Path) -> None:
    baseline.write_new_canonical_json(
        run_dir / "integrity.json",
        {
            "artifact_sha256": execution.artifact_hashes(run_dir),
            "binary_readback_verified": True,
            "contract_version": execution.CONTRACT_VERSION,
            "plan_sha256": execution.EXPECTED_PLAN_SHA256,
            "run_id": execution.S1_RUN_ID,
            "summary_recomputed_from_results": True,
        },
    )


def dry_construction() -> tuple[dict[str, object], ...]:
    """Construct the exact four future requests without server, network, or evidence writes."""
    return execution.dry_construction()


def run(model: Path = baseline.DEFAULT_MODEL, server: Path = baseline.DEFAULT_SERVER) -> Path:
    """Execute future S1 atomically; incomplete evidence stays noncanonical."""
    requests, pre_environment, runtime, base_url = _require_preflight(model, server)
    s0_prerequisite = execution.verify_s0_prerequisite()
    final_dir = RUNS / execution.S1_RUN_ID
    pending_dir = _pending_directory()
    invalid_dir = _invalid_directory()
    if final_dir.exists() or pending_dir.exists() or invalid_dir.exists():
        raise baseline.AttemptInfrastructureError("an S1 evidence directory already exists for this frozen run identity")

    executor_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    command = baseline.server_command(server, model)
    pending_dir.mkdir(parents=True)
    raw_dir = pending_dir / "raw"
    raw_dir.mkdir()
    metadata = {
        "contract": execution.contract_metadata(executor_commit),
        "created_at": baseline.utc_now(),
        "evidence_schema_version": execution.EVIDENCE_SCHEMA_VERSION,
        "model": {
            "file": model.name,
            "path": str(model),
            "sha256": baseline.EXPECTED_MODEL_SHA256,
            "size_bytes": model.stat().st_size,
            "subject": "llama-3.2-3b",
        },
        "repository": {"commit": executor_commit, "dirty": False},
        "run_id": execution.S1_RUN_ID,
        "runtime": runtime,
        "s0_prerequisite": s0_prerequisite,
        "runtime_parameters": baseline.INFERENCE,
        "server_command": command,
        "start_environment": pre_environment,
    }
    baseline.write_new_canonical_json(pending_dir / "metadata.json", metadata)
    (pending_dir / "results.jsonl").open("xb").close()
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
            raise baseline.AttemptInfrastructureError("server lost health before S1 request 1")
        for request in requests:
            entry = execution.plan_entry(request)
            request_payload = execution.build_request_payload(request)
            expected_tokens = None
            raw_response_bytes: bytes | None = None
            response: dict[str, Any] | None = None
            error: dict[str, str] | None = None
            started = time.perf_counter()
            try:
                expected_tokens = baseline.prompt_tokens(base_url, request.public_prompt)
                raw_response_bytes, response = baseline.post(
                    base_url,
                    execution.CHAT_COMPLETIONS_ENDPOINT,
                    request_payload,
                    timeout=baseline.INFERENCE["request_timeout_seconds"],
                )
                raw_text = response["choices"][0]["message"].get("content") or ""
                observed_tokens = response.get("usage", {}).get("prompt_tokens")
                if observed_tokens != expected_tokens:
                    raise baseline.AttemptInfrastructureError(
                        f"prompt-token inconsistency: expected={expected_tokens}, observed={observed_tokens}"
                    )
            except (baseline.AttemptInfrastructureError, KeyError, OSError, TimeoutError, ValueError, urllib.error.URLError) as error_value:
                raw_text = ""
                error = {"message": f"{type(error_value).__name__}: {error_value}", "type": "infrastructure_error"}
            evaluation = execution.evaluate_raw_output(request, raw_text)
            complete = error is None
            record = {
                **entry,
                "evidence_schema_version": execution.EVIDENCE_SCHEMA_VERSION,
                "evaluation": evaluation,
                "expected_prompt_tokens": expected_tokens,
                "finish_reason": response.get("choices", [{}])[0].get("finish_reason") if response else None,
                "infrastructure_status": "complete" if complete else "failed",
                "model": metadata["model"],
                "raw_output": raw_text,
                "raw_request_payload": request_payload,
                "raw_response_payload_utf8": raw_response_bytes.decode("utf-8", errors="replace") if raw_response_bytes is not None else None,
                "response": response,
                "run_id": execution.S1_RUN_ID,
                "runtime": runtime,
                "timing": {"completed_at": baseline.utc_now(), "total_ms": round((time.perf_counter() - started) * 1000, 3)},
                "usage": response.get("usage") if response else None,
                "error": error,
            }
            baseline.append_canonical_jsonl(pending_dir / "results.jsonl", record)
            records.append(record)
            if not complete:
                break
    except baseline.AttemptInfrastructureError as error:
        records.append(
            {
                "run_id": execution.S1_RUN_ID,
                "error": {"message": str(error), "type": "startup_infrastructure_error"},
                "infrastructure_status": "failed",
                "request_ordinal": 0,
            }
        )
        baseline.append_canonical_jsonl(pending_dir / "results.jsonl", records[-1])
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
        baseline.write_new_canonical_json(pending_dir / "server-lifecycle.json", lifecycle)

    summary = execution.summarize_s1_records(records, requests)
    baseline.write_new_canonical_json(pending_dir / "summary.json", summary)
    if summary["outcome"] != "protocol_valid":
        pending_dir.replace(invalid_dir)
        return invalid_dir
    _write_integrity_manifest(pending_dir)
    execution.validate_s1_run_directory(pending_dir)
    pending_dir.replace(final_dir)
    return final_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="construct the frozen S1 payloads without server, network, or evidence writes")
    arguments = parser.parse_args()
    if arguments.dry_run:
        print(len(dry_construction()))
        return
    print(run())


if __name__ == "__main__":
    main()
