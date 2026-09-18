#!/usr/bin/env python3
"""Execute only the frozen 18-cell direct-state-vector qualification; no retries."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path
from typing import Any

import run_mn006_baseline as baseline
from mn006 import direct_state_vector_execution as execution

RUNS = execution.RUNS
EXECUTION_FAILURES = (
    OSError,
    ValueError,
    KeyError,
    TypeError,
    IndexError,
    RuntimeError,
    subprocess.SubprocessError,
    KeyboardInterrupt,
)


def _pending_directory() -> Path:
    return RUNS / f".{execution.RUN_ID}.pending"


def _invalid_directory() -> Path:
    return RUNS / f"{execution.RUN_ID}.infrastructure-invalid"


def dry_construction() -> tuple[dict[str, object], ...]:
    """Read and construct in memory; never start a process or access the network."""
    execution.require_no_evidence(RUNS)
    return execution.dry_construction()


def _git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=execution.REPOSITORY_ROOT, text=True
    ).strip()


def _require_preflight() -> dict[str, Any]:
    """All real-execution checks precede pending-state creation and server startup."""
    execution.verify_static_repository()
    execution.require_no_evidence(RUNS)
    requests = execution.build_request_plan()
    execution.request_parameters()
    if execution.CHAT_COMPLETIONS_ENDPOINT != "/v1/chat/completions":
        raise execution.DirectStateVectorExecutionError(
            "endpoint differs from frozen runtime"
        )
    if _git("status", "--porcelain", "--untracked-files=all"):
        raise execution.DirectStateVectorExecutionError(
            "execution requires a clean repository"
        )
    commit = _git("rev-parse", "HEAD")
    if (
        _git("rev-parse", "--abbrev-ref", "@{upstream}")
        != "origin/codex/mn-006-distributed-state-integration"
    ):
        raise execution.DirectStateVectorExecutionError("upstream differs")
    remote = _git(
        "ls-remote", "origin", "refs/heads/codex/mn-006-distributed-state-integration"
    )
    if not remote or remote.split()[0] != commit:
        raise execution.DirectStateVectorExecutionError(
            "branch is not synchronized with remote"
        )
    if (
        not baseline.DEFAULT_MODEL.is_file()
        or baseline.file_sha256(baseline.DEFAULT_MODEL)
        != baseline.EXPECTED_MODEL_SHA256
    ):
        raise execution.DirectStateVectorExecutionError(
            "qualified model is missing or hash differs"
        )
    if not baseline.DEFAULT_SERVER.is_file():
        raise execution.DirectStateVectorExecutionError(
            "qualified runtime executable is missing"
        )
    runtime = baseline.runtime_identity(baseline.DEFAULT_SERVER)
    base_url = f"http://{baseline.HOST}:{baseline.PORT}"
    environment = baseline.environment_snapshot()
    baseline.require_clean_environment(environment, base_url)
    metadata = {
        "contract": execution.contract_metadata(
            commit,
            redesign=execution.verify_redesign_prerequisite(),
            inventory=execution.verify_inventory_prerequisite(),
        ),
        "created_at": baseline.utc_now(),
        "evidence_schema_version": execution.EVIDENCE_SCHEMA_VERSION,
        "run_id": execution.RUN_ID,
        "repository": {"commit": commit, "dirty": False},
        "model": {
            "path": str(baseline.DEFAULT_MODEL),
            "file": baseline.DEFAULT_MODEL.name,
            "sha256": baseline.EXPECTED_MODEL_SHA256,
            "size_bytes": baseline.DEFAULT_MODEL.stat().st_size,
            "subject": "llama-3.2-3b",
        },
        "runtime": runtime,
        "runtime_parameters": dict(baseline.INFERENCE),
        "server_command": baseline.server_command(
            baseline.DEFAULT_SERVER, baseline.DEFAULT_MODEL
        ),
        "start_environment": environment,
    }
    execution.validate_runtime_metadata(metadata)
    return {"requests": requests, "metadata": metadata, "base_url": base_url}


def _ready_environment(process_id: int) -> dict[str, Any]:
    snapshot = baseline.environment_snapshot()
    gpu = snapshot["gpu"]
    if (
        not gpu["gpu_query"]["available"]
        or not gpu["compute_query"]["available"]
        or not gpu["gpus"]
    ):
        raise baseline.AttemptInfrastructureError(
            "ready-state telemetry is unavailable"
        )
    if any(item["pid"] != process_id for item in gpu["compute_processes"]):
        raise baseline.AttemptInfrastructureError(
            "competing GPU process appeared before request 1"
        )
    if any(f'"{process_id}"' not in line for line in snapshot["local_model_processes"]):
        raise baseline.AttemptInfrastructureError(
            "competing local model appeared before request 1"
        )
    return snapshot


def _write_integrity(run_dir: Path) -> None:
    baseline.write_new_canonical_json(
        run_dir / "integrity.json",
        {
            "artifact_sha256": execution.artifact_hashes(run_dir),
            "binary_readback_verified": True,
            "plan_sha256": execution.EXPECTED_PLAN_SHA256,
            "run_id": execution.RUN_ID,
            "summary_recomputed_from_results": True,
        },
    )


def run() -> Path:
    """Future separately authorized measurement. Every failure retains noncanonical evidence."""
    preflight = _require_preflight()
    requests = preflight["requests"]
    metadata = preflight["metadata"]
    base_url = preflight["base_url"]
    execution.require_no_evidence(RUNS)
    pending = _pending_directory()
    pending.mkdir()
    raw = pending / "raw"
    raw.mkdir()
    baseline.write_new_canonical_json(pending / "metadata.json", metadata)
    (pending / "results.jsonl").open("xb").close()
    records: list[dict[str, Any]] = []
    process = None
    failure: dict[str, str] | None = None
    lifecycle: dict[str, Any] = {
        "started": False,
        "expected_termination": False,
        "pid": None,
        "command": metadata["server_command"],
    }
    with (
        (raw / "llama-server.stdout.txt").open("xb") as stdout,
        (raw / "llama-server.stderr.txt").open("xb") as stderr,
    ):
        try:
            process = subprocess.Popen(
                metadata["server_command"],
                stdout=stdout,
                stderr=stderr,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            lifecycle.update(
                started=True, pid=process.pid, process_started_at=baseline.utc_now()
            )
            lifecycle["health_at_ready"] = baseline.wait_for_server(process, base_url)
            lifecycle["environment_at_ready"] = _ready_environment(process.pid)
            execution.build_request_plan()  # Recheck authority immediately before the first generation.
            for request in requests:
                if (
                    process.poll() is not None
                    or not baseline.health(base_url)["reachable"]
                ):
                    raise baseline.AttemptInfrastructureError(
                        "measurement server exited or lost health"
                    )
                payload = execution.build_request_payload(request)
                started = time.perf_counter()
                raw_response = None
                response = None
                expected_tokens = None
                raw_text = ""
                error = None
                try:
                    expected_tokens = baseline.prompt_tokens(
                        base_url, request.public_prompt
                    )
                    raw_response, response = baseline.post(
                        base_url,
                        execution.CHAT_COMPLETIONS_ENDPOINT,
                        payload,
                        timeout=baseline.INFERENCE["request_timeout_seconds"],
                    )
                    raw_text = response["choices"][0]["message"].get("content") or ""
                    if (
                        not isinstance(raw_text, str)
                        or response.get("usage", {}).get("prompt_tokens")
                        != expected_tokens
                    ):
                        raise baseline.AttemptInfrastructureError(
                            "response schema or prompt-token consistency failure"
                        )
                except EXECUTION_FAILURES as caught:
                    error = {"type": type(caught).__name__, "message": str(caught)}
                record = {
                    **execution.plan_entry(request),
                    "run_id": execution.RUN_ID,
                    "evidence_schema_version": execution.EVIDENCE_SCHEMA_VERSION,
                    "infrastructure_status": "complete" if error is None else "failed",
                    "error": error,
                    "raw_request_payload": payload,
                    "raw_response_payload_utf8": raw_response.decode("utf-8")
                    if raw_response is not None
                    else None,
                    "response": response,
                    "raw_output": raw_text,
                    "evaluation": execution.evaluate_raw_output(request, raw_text),
                    "expected_prompt_tokens": expected_tokens,
                    "finish_reason": response.get("choices", [{}])[0].get(
                        "finish_reason"
                    )
                    if response
                    else None,
                    "usage": response.get("usage") if response else None,
                    "timing": {
                        "completed_at": baseline.utc_now(),
                        "total_ms": round((time.perf_counter() - started) * 1000, 3),
                    },
                    "model": metadata["model"],
                    "runtime": metadata["runtime"],
                }
                baseline.append_canonical_jsonl(pending / "results.jsonl", record)
                records.append(record)
                if error is not None:
                    failure = error
                    break
            lifecycle["environment_before_cleanup"] = baseline.environment_snapshot()
            lifecycle["health_before_cleanup"] = baseline.health(base_url)
            if (
                process.poll() is not None
                or not lifecycle["health_before_cleanup"]["reachable"]
            ):
                raise baseline.AttemptInfrastructureError(
                    "server failed before controlled termination"
                )
        except EXECUTION_FAILURES as caught:
            failure = {"type": type(caught).__name__, "message": str(caught)}
        finally:
            try:
                if process is not None:
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=20)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=20)
                            raise baseline.AttemptInfrastructureError(
                                "server required forced cleanup"
                            )
                        lifecycle["expected_termination"] = True
                    lifecycle["exit_code"] = process.poll()
                lifecycle["end_environment"] = baseline.environment_snapshot()
                lifecycle["health_after_cleanup"] = baseline.health(base_url)
                baseline.require_clean_environment(
                    lifecycle["end_environment"], base_url
                )
            except EXECUTION_FAILURES as caught:
                failure = {"type": type(caught).__name__, "message": str(caught)}
            lifecycle["failure"] = failure
            baseline.write_new_canonical_json(
                pending / "server-lifecycle.json", lifecycle
            )
    if failure is not None:
        summary = {
            "outcome": "infrastructure_invalid",
            "classification": None,
            "error": failure,
            "completed_requests": sum(
                record["infrastructure_status"] == "complete" for record in records
            ),
            "expected_requests": execution.EXPECTED_REQUEST_COUNT,
        }
    else:
        try:
            summary = execution.summarize_records(records, requests)
        except EXECUTION_FAILURES as caught:
            summary = {
                "outcome": "infrastructure_invalid",
                "classification": None,
                "error": {"type": type(caught).__name__, "message": str(caught)},
            }
    baseline.write_new_canonical_json(pending / "summary.json", summary)
    if summary["outcome"] != "protocol_valid":
        pending.rename(_invalid_directory())
        return _invalid_directory()
    try:
        _write_integrity(pending)
        execution.validate_complete_artifacts(pending)
    except EXECUTION_FAILURES as caught:
        # Preserve the provisional derived summary; raw records remain append-only.
        (pending / "summary.json").rename(pending / "summary.provisional.json")
        baseline.write_new_canonical_json(
            pending / "summary.json",
            {
                "outcome": "infrastructure_invalid",
                "classification": None,
                "message": str(caught),
            },
        )
        pending.rename(_invalid_directory())
        return _invalid_directory()
    final = RUNS / execution.RUN_ID
    pending.rename(final)  # Same-volume atomic, destination must not exist.
    return final


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate authority and construct 18 payloads in memory without processes or network",
    )
    arguments = parser.parse_args()
    if arguments.dry_run:
        print(len(dry_construction()))
    else:
        print(run())


if __name__ == "__main__":
    main()
