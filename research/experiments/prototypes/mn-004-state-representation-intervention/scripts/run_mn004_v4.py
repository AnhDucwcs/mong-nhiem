"""Execute one predeclared MN-004 v4 operational-feasibility stage."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

import mn004
import mn004_v4
import run_mn004 as runtime

STAGES = ("stage_a_untreated", "stage_b_ledger", "stage_c1_failed_case", "stage_c2_predecessor_then_failed_case")


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def command_result(command: list[str]) -> dict[str, Any]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    return {"available": result.returncode == 0, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def gpu_snapshot() -> dict[str, Any]:
    gpu = command_result(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"])
    processes = command_result(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits"])
    snapshot: dict[str, Any] = {"captured_at": utc_now(), "gpu_query": gpu, "compute_query": processes, "gpus": [], "compute_processes": []}
    if gpu["available"]:
        for line in gpu["stdout"].splitlines():
            fields = [field.strip() for field in line.split(",")]
            if len(fields) == 5:
                snapshot["gpus"].append({"name": fields[0], "driver": fields[1], "total_mib": int(fields[2]), "used_mib": int(fields[3]), "free_mib": int(fields[4])})
    if processes["available"]:
        for line in processes["stdout"].splitlines():
            if not line.strip() or "no running" in line.casefold():
                continue
            fields = [field.strip() for field in line.split(",")]
            if len(fields) == 3 and fields[0].isdigit():
                snapshot["compute_processes"].append({"pid": int(fields[0]), "name": fields[1], "used_mib": int(fields[2]) if fields[2].isdigit() else None})
    return snapshot


def require_telemetry(snapshot: dict[str, Any]) -> None:
    if not snapshot["gpu_query"]["available"] or not snapshot["compute_query"]["available"] or not snapshot["gpus"]:
        raise mn004.ContractError("v4 mandatory nvidia-smi telemetry unavailable")


def health(url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url + "/health", timeout=2) as response:
            return {"observed_at": utc_now(), "reachable": response.status == 200, "status": response.status}
    except (OSError, TimeoutError, urllib.error.URLError) as exc:
        return {"observed_at": utc_now(), "reachable": False, "error": f"{type(exc).__name__}: {exc}"}


def stderr_tail(path: Path, maximum: int) -> str:
    if not path.is_file():
        return ""
    return path.read_bytes()[-maximum:].decode("utf-8", errors="replace")


def build_server_command(server: Path, model: Path, definition: dict[str, Any], port: int) -> list[str]:
    value = definition["runtime"]
    return [str(server), "-m", str(model), "--host", "127.0.0.1", "--port", str(port), "-c", str(value["configured_context_size"]), "-t", str(value["threads"]), "-b", str(value["batch_size"]), "-np", str(value["parallel_slots"]), "-fa", "on" if value["flash_attention"] else "off", "--temp", "0", "--seed", str(value["seed"]), "--jinja", "--no-webui", "--no-cache-prompt", "--metrics", "--chat-template-kwargs", json.dumps(definition["model"]["chat_template_kwargs"], separators=(",", ":"))]


def start_server(command: list[str], stdout: Path, stderr: Path) -> tuple[subprocess.Popen[Any], Any, Any]:
    stdout_handle, stderr_handle = stdout.open("w", encoding="utf-8"), stderr.open("w", encoding="utf-8")
    return subprocess.Popen(command, stdout=stdout_handle, stderr=stderr_handle), stdout_handle, stderr_handle


def poll_after_failure(process: subprocess.Popen[Any], seconds: int) -> dict[str, Any]:
    deadline = time.monotonic() + seconds
    while process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.2)
    return {"observed_at": utc_now(), "pid": process.pid, "returncode": process.poll(), "alive": process.poll() is None}


def selected_rows(stage: str) -> list[dict[str, Any]]:
    if stage in {"stage_a_untreated", "stage_b_ledger"}:
        return mn004_v4.inventory()
    failed, predecessor = mn004_v4.selected_diagnostic_rows()
    return [failed] if stage == "stage_c1_failed_case" else [predecessor, failed] if predecessor else []


def condition_for(stage: str) -> str:
    return "natural_language" if stage == "stage_a_untreated" else "ledger"


def run_stage(args: argparse.Namespace) -> dict[str, Any]:
    definition = mn004_v4.validate_authority()
    mn004_v4.validate_offline()
    if not mn004_v4.stage_allowed(args.stage):
        raise mn004.ContractError(f"v4 execution order blocks {args.stage}")
    if runtime.command_output(["git", "status", "--porcelain", "--untracked-files=all"]).strip():
        raise mn004.ContractError("canonical v4 stage requires a clean worktree")
    model = args.models_dir / definition["model"]["file"]
    if not model.is_file() or runtime.file_digest(model) != definition["model"]["sha256"]:
        raise mn004.ContractError("v4 model artifact mismatch")
    identity = runtime.runtime_identity(args.llama_server)
    if any(identity[key] != definition["runtime"][key] for key in ("backend", "version", "build", "commit")):
        raise mn004.ContractError("v4 runtime identity mismatch")
    baseline = gpu_snapshot()
    require_telemetry(baseline)
    created = dt.datetime.now(dt.UTC)
    run_id = f"v4-{created:%Y%m%dT%H%M%SZ}-{args.stage}-{uuid.uuid4().hex[:8]}"
    run_dir, raw = mn004.RUNS / run_id, mn004.RUNS / run_id / "raw"
    raw.mkdir(parents=True)
    rows, condition = selected_rows(args.stage), condition_for(args.stage)
    metadata = {"run_id": run_id, "created_at": created.isoformat(), "stage": args.stage, "v4_definition_fingerprint": mn004_v4.fingerprint(definition), "v1_inventory_fingerprint": definition["authority"]["v1_inventory_fingerprint"], "model": definition["model"], "runtime": identity, "inference": definition["runtime"], "repository": {"commit": runtime.command_output(["git", "rev-parse", "HEAD"]).strip(), "dirty": False}, "selection": {"condition": condition, "case_ids": [row["case_id"] for row in rows], "requested_input_tokens": 8192}, "telemetry": {"before_phase": baseline}}
    mn004.dump_json(run_dir / "metadata.json", metadata)
    if baseline["compute_processes"]:
        summary = {"run_id": run_id, "stage": args.stage, "expected_results": len(rows), "observed_results": 0, "operational_outcome": "environment_contaminated", "telemetry": {"before_phase": baseline}, "server_lifecycle": {"started": False}}
        mn004.dump_json(run_dir / "summary.json", summary)
        return summary
    url = f"http://127.0.0.1:{args.port}"
    if health(url)["reachable"]:
        summary = {"run_id": run_id, "stage": args.stage, "expected_results": len(rows), "observed_results": 0, "operational_outcome": "protocol_invalid", "server_lifecycle": {"started": False, "reason": "port_already_serving"}}
        mn004.dump_json(run_dir / "summary.json", summary)
        return summary
    command = build_server_command(args.llama_server, model, definition, args.port)
    stdout, stderr = raw / "llama-server.stdout.txt", raw / "llama-server.stderr.txt"
    process: subprocess.Popen[Any] | None = None
    stdout_handle: Any = None
    stderr_handle: Any = None
    records: list[dict[str, Any]] = []
    lifecycle: dict[str, Any] = {"command": command, "process_started_at": None, "pid": None, "health_at_ready": None, "expected_termination": False}
    try:
        process, stdout_handle, stderr_handle = start_server(command, stdout, stderr)
        lifecycle.update({"process_started_at": utc_now(), "pid": process.pid})
        runtime.wait_for_server(process, url)
        lifecycle["health_at_ready"] = health(url)
        phase_ready = gpu_snapshot(); require_telemetry(phase_ready)
        metadata["telemetry"]["server_ready"] = phase_ready
        mn004.dump_json(run_dir / "metadata.json", metadata)
        client = mn004.ServerClient(url, definition["model"]["chat_template_kwargs"])

        def request(ordinal: int, row: dict[str, Any]) -> dict[str, Any]:
            pair = mn004_v4.preflight_pair(row, condition)
            prompt = row["natural_prompt" if condition == "natural_language" else "ledger_prompt"]
            before = gpu_snapshot(); require_telemetry(before)
            started, started_monotonic = utc_now(), time.perf_counter()
            response: dict[str, Any] | None = None
            error: dict[str, Any] | None = None
            protocol_flags: list[str] = []
            try:
                _request, response = client.complete(prompt, definition["runtime"])
                if response.get("usage", {}).get("prompt_tokens") != pair["actual_prompt_tokens"]:
                    protocol_flags.append("prompt_token_mismatch")
            except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError, mn004.ContractError) as exc:
                error = {"type": "request_error", "message": f"{type(exc).__name__}: {exc}"}
            ended = utc_now()
            record: dict[str, Any] = {"request_ordinal": ordinal, "case_id": row["case_id"], "case_origin": row["origin"], "requested_input_tokens": row["requested_input_tokens"], "condition": condition, "source_event_hash": row["source_event_hash"], "prompt_hash": pair["prompt_hash"], "actual_prompt_tokens": pair["actual_prompt_tokens"], "event_count": len(row["source_events"]), "target_event_indexes": row["target_event_indexes"], "target_event_token_positions": pair["target_event_token_positions"], "request_started_at": started, "request_ended_at": ended, "latency_ms": round((time.perf_counter() - started_monotonic) * 1000, 3), "gpu_before_request": before, "response": response, "raw_output": response.get("choices", [{}])[0].get("message", {}).get("content") if response else None, "finish_reason": response.get("choices", [{}])[0].get("finish_reason") if response else None, "error": error, "protocol_flags": protocol_flags, "completion_status": "complete", "failure_attachment": None}
            if error:
                record["completion_status"] = "infrastructure_failure"
                record["failure_attachment"] = {"captured_at": utc_now(), "error": error, "stderr_tail": stderr_tail(stderr, definition["telemetry"]["stderr_tail_bytes"]), "process": poll_after_failure(process, definition["telemetry"]["post_failure_process_poll_seconds"]), "health": health(url), "gpu": gpu_snapshot()}
            elif protocol_flags:
                record["completion_status"] = "protocol_invalid"
                record["failure_attachment"] = {"captured_at": utc_now(), "protocol_flags": protocol_flags, "health": health(url), "gpu": gpu_snapshot()}
            else:
                record["gpu_after_request"] = gpu_snapshot(); require_telemetry(record["gpu_after_request"])
            return record

        records = mn004_v4.execute_fail_fast(rows, request)
    except mn004.ContractError as exc:
        startup_failure = "llama-server" in str(exc)
        records.append({"request_ordinal": 0, "case_id": None, "completion_status": "infrastructure_failure" if startup_failure else "protocol_invalid", "error": {"type": "contract_error", "message": str(exc)}, "failure_attachment": {"captured_at": utc_now(), "stderr_tail": stderr_tail(stderr, definition["telemetry"]["stderr_tail_bytes"]), "gpu": gpu_snapshot()}})
    finally:
        if process:
            if process.poll() is None:
                lifecycle["expected_termination"] = True
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=15)
            lifecycle.update({"process_exit_observed_at": utc_now(), "exit_code": process.poll(), "alive_after_cleanup": process.poll() is None, "health_after_cleanup": health(url)})
        if stdout_handle: stdout_handle.close()
        if stderr_handle: stderr_handle.close()
        (run_dir / "results.jsonl").write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    outcome = mn004_v4.phase_outcome(args.stage, records, len(rows))
    failure = mn004_v4.first_failure(records)
    predecessor = records[records.index(failure) - 1]["case_id"] if failure and records.index(failure) else None
    summary = {"run_id": run_id, "stage": args.stage, "expected_results": len(rows), "observed_results": len(records), "completed_requests": sum(record["completion_status"] == "complete" for record in records), "operational_outcome": outcome, "first_failure": failure, "last_successful_case_id": predecessor, "server_lifecycle": lifecycle, "resource_signature": mn004_v4.has_resource_signature(failure)}
    if args.stage == "stage_c1_failed_case": summary["predecessor_case_id"] = mn004_v4.selected_diagnostic_rows()[1]["case_id"] if mn004_v4.selected_diagnostic_rows()[1] else None
    mn004.dump_json(run_dir / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    configs = mn004.load_json(mn004.CONFIGS / "models.json")
    parser.add_argument("--stage", choices=STAGES, required=True)
    parser.add_argument("--models-dir", type=Path, default=Path(configs["default_models_dir"]))
    parser.add_argument("--llama-server", type=Path, default=Path(configs["default_llama_server"]))
    parser.add_argument("--port", type=int, default=18644)
    print(json.dumps(run_stage(parser.parse_args()), indent=2))


if __name__ == "__main__":
    main()
