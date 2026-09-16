#!/usr/bin/env python3
"""Execute the single frozen MN-006 Llama baseline attempt without retries."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from mn006.measurement import (
    ATTEMPT_ID,
    EVIDENCE_SCHEMA_VERSION,
    EXPECTED_INVENTORY_SHA256,
    append_canonical_jsonl,
    build_request_plan,
    evaluate_raw_output,
    summarize_attempt,
    validate_attempt_directory,
    write_new_canonical_json,
)
from mn006.response_channel import (
    FIXED_ANSWER_GRAMMAR,
    constrained_payload,
)

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
DEFAULT_MODEL = Path(r"D:\Code\mong-nhiem\artifacts\models\mn-002\Llama-3.2-3B-Instruct-Q4_K_M.gguf")
DEFAULT_SERVER = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")
EXPECTED_MODEL_SHA256 = "6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff"
EXPECTED_RUNTIME = {"version": "0.2.0-dev", "build": "10566", "commit": "bb4caa754"}
HOST = "127.0.0.1"
PORT = 18501
INFERENCE = {
    "configured_context_size": 16896,
    "temperature": 0.0,
    "seed": 42,
    "output_tokens": 16,
    "threads": 12,
    "batch_size": 2048,
    "parallel_slots": 1,
    "flash_attention": True,
    "prompt_cache": False,
    "prompt_formatting": "--jinja",
    "chat_template_kwargs": {},
    "request_timeout_seconds": 120,
    "health_deadline_seconds": 180,
}


class AttemptInfrastructureError(RuntimeError):
    """A frozen-policy infrastructure condition that invalidates the attempt."""


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def command_result(command: list[str], timeout: int = 20) -> dict[str, Any]:
    try:
        result = subprocess.run(command, capture_output=True, check=False, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"available": False, "error": f"{type(error).__name__}: {error}"}
    return {
        "available": result.returncode == 0,
        "returncode": result.returncode,
        "stderr": result.stderr.decode("utf-8", errors="replace"),
        "stdout": result.stdout.decode("utf-8", errors="replace"),
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def runtime_identity(server: Path) -> dict[str, Any]:
    version = command_result([str(server), "--version"])
    raw = version.get("stdout", "") + version.get("stderr", "")
    match = re.search(r"version:\s*(.*?)\s*\(build\s+(\d+),\s*commit\s+([0-9a-f]+)", raw, re.IGNORECASE)
    identity = {
        "backend": "llama.cpp",
        "executable": str(server),
        "raw_version_output": raw,
        "version": match.group(1).strip() if match else None,
        "build": match.group(2) if match else None,
        "commit": match.group(3) if match else None,
    }
    if not version["available"] or any(identity[key] != value for key, value in EXPECTED_RUNTIME.items()):
        raise AttemptInfrastructureError("available llama.cpp runtime differs from frozen ECC-006 identity")
    return identity


def gpu_snapshot() -> dict[str, Any]:
    gpu = command_result(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total,memory.used,memory.free,utilization.gpu,utilization.memory",
            "--format=csv,noheader,nounits",
        ]
    )
    compute = command_result(
        ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits"]
    )
    snapshot: dict[str, Any] = {
        "captured_at": utc_now(),
        "compute_processes": [],
        "compute_query": compute,
        "gpu_query": gpu,
        "gpus": [],
    }
    if gpu["available"]:
        for line in gpu["stdout"].splitlines():
            parts = [part.strip() for part in line.split(",")]
            if len(parts) == 7:
                snapshot["gpus"].append(
                    {
                        "driver": parts[1],
                        "memory_free_mib": int(parts[4]),
                        "memory_total_mib": int(parts[2]),
                        "memory_used_mib": int(parts[3]),
                        "name": parts[0],
                        "utilization_gpu_percent": int(parts[5]),
                        "utilization_memory_percent": int(parts[6]),
                    }
                )
    if compute["available"]:
        for line in compute["stdout"].splitlines():
            if not line.strip() or "no running" in line.casefold():
                continue
            parts = [part.strip() for part in line.split(",")]
            if len(parts) == 3 and parts[0].isdigit():
                snapshot["compute_processes"].append(
                    {"name": parts[1], "pid": int(parts[0]), "used_mib": int(parts[2]) if parts[2].isdigit() else None}
                )
    return snapshot


def environment_snapshot() -> dict[str, Any]:
    tasklist = command_result(["tasklist", "/FO", "CSV", "/NH"])
    local_model_processes = [
        line for line in tasklist.get("stdout", "").splitlines() if "llama" in line.casefold() or "ollama" in line.casefold()
    ]
    return {
        "captured_at": utc_now(),
        "cpu_count": os.cpu_count(),
        "gpu": gpu_snapshot(),
        "local_model_processes": local_model_processes,
        "os": platform.platform(),
        "tasklist": tasklist,
    }


def health(base_url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(base_url + "/health", timeout=2) as response:
            return {"captured_at": utc_now(), "reachable": response.status == 200, "status": response.status}
    except (OSError, TimeoutError, urllib.error.URLError) as error:
        return {"captured_at": utc_now(), "error": f"{type(error).__name__}: {error}", "reachable": False}


def require_clean_environment(snapshot: dict[str, Any], base_url: str) -> None:
    gpu = snapshot["gpu"]
    if not gpu["gpu_query"]["available"] or not gpu["compute_query"]["available"] or not gpu["gpus"]:
        raise AttemptInfrastructureError("mandatory nvidia-smi GPU telemetry is unavailable")
    if gpu["compute_processes"]:
        raise AttemptInfrastructureError("pre-run environment has an existing GPU compute process")
    if snapshot["local_model_processes"]:
        raise AttemptInfrastructureError("pre-run environment has an existing local model process")
    if health(base_url)["reachable"]:
        raise AttemptInfrastructureError("measurement port already serves a process")


def wait_for_server(process: subprocess.Popen[Any], base_url: str) -> dict[str, Any]:
    deadline = time.monotonic() + INFERENCE["health_deadline_seconds"]
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AttemptInfrastructureError(f"llama-server exited during startup: {process.returncode}")
        observed = health(base_url)
        if observed["reachable"]:
            return observed
        time.sleep(0.5)
    raise AttemptInfrastructureError("llama-server failed its frozen 180-second health deadline")


def post(base_url: str, path: str, payload: dict[str, Any], timeout: int) -> tuple[bytes, dict[str, Any]]:
    request = urllib.request.Request(
        base_url + path,
        data=json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
    return raw, json.loads(raw.decode("utf-8"))


def prompt_tokens(base_url: str, prompt: str) -> int:
    _, templated = post(
        base_url,
        "/apply-template",
        {"messages": [{"role": "user", "content": prompt}], "add_generation_prompt": True, "chat_template_kwargs": {}},
        timeout=INFERENCE["request_timeout_seconds"],
    )
    _, tokenized = post(base_url, "/tokenize", {"content": templated["prompt"], "add_special": True}, timeout=INFERENCE["request_timeout_seconds"])
    return len(tokenized["tokens"])


def server_command(server: Path, model: Path) -> list[str]:
    return [
        str(server), "-m", str(model), "--host", HOST, "--port", str(PORT),
        "-c", str(INFERENCE["configured_context_size"]), "-t", str(INFERENCE["threads"]),
        "-b", str(INFERENCE["batch_size"]), "-np", str(INFERENCE["parallel_slots"]),
        "-fa", "on", "--temp", "0", "--seed", str(INFERENCE["seed"]), "--jinja", "--no-webui",
        "--no-cache-prompt", "--metrics", "--chat-template-kwargs", "{}",
    ]


def build_request_payload(prompt_bytes: bytes, *, grammar: str | None = None) -> dict[str, Any]:
    """Build the frozen request mapping, optionally with its sole authorized grammar field."""
    baseline = {
        "messages": [{"role": "user", "content": prompt_bytes.decode("utf-8")}],
        "temperature": INFERENCE["temperature"],
        "seed": INFERENCE["seed"],
        "max_tokens": INFERENCE["output_tokens"],
        "chat_template_kwargs": {},
    }
    if grammar is None:
        return baseline
    if grammar != FIXED_ANSWER_GRAMMAR:
        raise AttemptInfrastructureError("attempt request grammar differs from the frozen response-channel contract")
    return constrained_payload(baseline)


def run_attempt(
    *,
    attempt_id: str,
    evidence_schema_version: str,
    response_channel_contract_version: str | None,
    grammar: str | None,
    contract_metadata: dict[str, Any] | None = None,
    model: Path = DEFAULT_MODEL,
    server: Path = DEFAULT_SERVER,
) -> Path:
    """Run one prospectively frozen MN-006 request contract without retries."""
    if not model.is_file() or file_sha256(model) != EXPECTED_MODEL_SHA256:
        raise AttemptInfrastructureError("model file is missing or differs from the qualified Llama artifact")
    if not server.is_file():
        raise AttemptInfrastructureError("llama-server executable is unavailable")
    if subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, check=False).stdout.strip():
        raise AttemptInfrastructureError("attempt requires a clean repository worktree")
    manifest, plan = build_request_plan()
    if manifest["aggregate_inventory_sha256"] != EXPECTED_INVENTORY_SHA256:
        raise AttemptInfrastructureError("inventory fingerprint differs from frozen attempt contract")
    base_url = f"http://{HOST}:{PORT}"
    pre_environment = environment_snapshot()
    require_clean_environment(pre_environment, base_url)
    runtime = runtime_identity(server)
    run_dir = RUNS / attempt_id
    if run_dir.exists():
        raise AttemptInfrastructureError(f"{attempt_id} evidence directory already exists")
    run_dir.mkdir(parents=True)
    raw_dir = run_dir / "raw"
    raw_dir.mkdir()
    command = server_command(server, model)
    metadata = {
        "attempt_id": attempt_id,
        "created_at": utc_now(),
        "evidence_schema_version": evidence_schema_version,
        "inventory_aggregate_sha256": manifest["aggregate_inventory_sha256"],
        "model": {"file": model.name, "path": str(model), "sha256": EXPECTED_MODEL_SHA256, "size_bytes": model.stat().st_size, "subject": "llama-3.2-3b"},
        "repository": {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(), "dirty": False},
        "request_order_contract": "level_1_then_level_2; ordinal_ascending; even=C_then_I; odd=I_then_C",
        "runtime": runtime,
        "runtime_parameters": INFERENCE,
        "server_command": command,
        "start_environment": pre_environment,
    }
    if response_channel_contract_version is not None:
        metadata["response_channel"] = {
            "contract_version": response_channel_contract_version,
            "grammar": grammar,
        }
    if contract_metadata is not None:
        metadata["attempt_contract"] = contract_metadata
    write_new_canonical_json(run_dir / "metadata.json", metadata)
    (run_dir / "results.jsonl").open("xb").close()
    stdout_path, stderr_path = raw_dir / "llama-server.stdout.txt", raw_dir / "llama-server.stderr.txt"
    process: subprocess.Popen[Any] | None = None
    stdout_handle: Any = None
    stderr_handle: Any = None
    records: list[dict[str, Any]] = []
    lifecycle: dict[str, Any] = {"command": command, "expected_termination": False, "pid": None, "started": False}
    try:
        stdout_handle = stdout_path.open("xb")
        stderr_handle = stderr_path.open("xb")
        process = subprocess.Popen(command, stdout=stdout_handle, stderr=stderr_handle)
        lifecycle.update({"pid": process.pid, "process_started_at": utc_now(), "started": True})
        lifecycle["health_at_ready"] = wait_for_server(process, base_url)
        ready_environment = environment_snapshot()
        lifecycle["environment_at_ready"] = ready_environment
        if not health(base_url)["reachable"]:
            raise AttemptInfrastructureError("server lost health before request 1")
        for entry in plan:
            prompt_path = ROOT / "definition" / "baseline-inventory-v1" / entry["public_prompt_path"]
            prompt_bytes = prompt_path.read_bytes()
            request_payload = build_request_payload(prompt_bytes, grammar=grammar)
            expected_tokens = None
            raw_response_bytes: bytes | None = None
            response: dict[str, Any] | None = None
            error: dict[str, str] | None = None
            started = time.perf_counter()
            try:
                expected_tokens = prompt_tokens(base_url, request_payload["messages"][0]["content"])
                raw_response_bytes, response = post(base_url, "/v1/chat/completions", request_payload, timeout=INFERENCE["request_timeout_seconds"])
                raw_text = response["choices"][0]["message"].get("content") or ""
                observed_tokens = response.get("usage", {}).get("prompt_tokens")
                if observed_tokens != expected_tokens:
                    raise AttemptInfrastructureError(f"prompt-token inconsistency: expected={expected_tokens}, observed={observed_tokens}")
            except (AttemptInfrastructureError, KeyError, OSError, TimeoutError, ValueError, urllib.error.URLError) as exc:
                raw_text = ""
                error = {"message": f"{type(exc).__name__}: {exc}", "type": "infrastructure_error"}
            evaluation = evaluate_raw_output(raw_text, entry["canonical_answer"])
            complete = error is None
            record = {
                **entry,
                "attempt_id": attempt_id,
                "evidence_schema_version": evidence_schema_version,
                "evaluation": evaluation,
                "expected_prompt_tokens": expected_tokens,
                "finish_reason": response.get("choices", [{}])[0].get("finish_reason") if response else None,
                "infrastructure_status": "complete" if complete else "failed",
                "model": metadata["model"],
                "raw_output": raw_text,
                "raw_request_payload": request_payload,
                "raw_response_payload_utf8": raw_response_bytes.decode("utf-8", errors="replace") if raw_response_bytes is not None else None,
                "response": response,
                "runtime": runtime,
                "timing": {"completed_at": utc_now(), "total_ms": round((time.perf_counter() - started) * 1000, 3)},
                "usage": response.get("usage") if response else None,
                "error": error,
            }
            append_canonical_jsonl(run_dir / "results.jsonl", record)
            records.append(record)
            print(f"{entry['request_ordinal']:03d}/128 {entry['case_id']}: {'OK' if complete else 'INFRASTRUCTURE_FAILURE'}", flush=True)
            if not complete:
                break
    except AttemptInfrastructureError as exc:
        if not records:
            records.append({"attempt_id": attempt_id, "error": {"message": str(exc), "type": "startup_infrastructure_error"}, "infrastructure_status": "failed", "request_ordinal": 0})
            append_canonical_jsonl(run_dir / "results.jsonl", records[-1])
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
            lifecycle.update({"exit_code": process.poll(), "process_exit_observed_at": utc_now(), "health_after_cleanup": health(base_url)})
        if stdout_handle is not None:
            stdout_handle.close()
        if stderr_handle is not None:
            stderr_handle.close()
        lifecycle["end_environment"] = environment_snapshot()
        write_new_canonical_json(run_dir / "server-lifecycle.json", lifecycle)
    if records and records[0].get("request_ordinal") == 0:
        summary = {"attempt_id": attempt_id, "completed_requests": 0, "expected_requests": len(plan), "infrastructure_failure_count": 1, "outcome": "infrastructure_invalid", "profiles": {}, "request_order_contract": metadata["request_order_contract"]}
    else:
        summary = summarize_attempt(records, plan, attempt_id=attempt_id)
    write_new_canonical_json(run_dir / "summary.json", summary)
    if summary["outcome"] == "protocol_valid":
        validate_attempt_directory(run_dir, attempt_id=attempt_id)
    return run_dir


def run(model: Path = DEFAULT_MODEL, server: Path = DEFAULT_SERVER) -> Path:
    """Run immutable `attempt-0001` with its original unconstrained contract."""
    return run_attempt(
        attempt_id=ATTEMPT_ID,
        evidence_schema_version=EVIDENCE_SCHEMA_VERSION,
        response_channel_contract_version=None,
        grammar=None,
        contract_metadata=None,
        model=model,
        server=server,
    )


def main() -> None:
    run_dir = run()
    print(run_dir)


if __name__ == "__main__":
    main()
