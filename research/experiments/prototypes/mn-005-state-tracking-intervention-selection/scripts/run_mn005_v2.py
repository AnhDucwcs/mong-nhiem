#!/usr/bin/env python3
"""Execute Gate C v2 only under the frozen MN-005 Gate B v2 contract."""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import time
import urllib.error
from collections.abc import Callable
from pathlib import Path
from typing import Any

import mn005_v2 as mn005

DEFAULT_MODELS = Path(r"D:\Code\mong-nhiem\artifacts\models\mn-002")
DEFAULT_SERVER = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")


def append_jsonl_durable(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def wait_for_clean_port(url: str) -> None:
    if mn005.health(url)["reachable"]:
        raise mn005.ContractError("protocol invalid: requested port is already serving")


def start_server(definition: dict[str, Any], server: Path, model: Path, port: int, raw: Path, label: str, static_cpu: bool = False) -> tuple[subprocess.Popen[Any], Any, Any, mn005.Client, dict[str, Any]]:
    before = mn005.gpu_snapshot()
    mn005.require_clean_gpu(before)
    url = f"http://127.0.0.1:{port}"
    wait_for_clean_port(url)
    stdout_path, stderr_path = raw / f"{label}.stdout.txt", raw / f"{label}.stderr.txt"
    command = mn005.cpu_static_server_command(definition, server, model, port) if static_cpu else mn005.server_command(definition, server, model, port)
    stdout, stderr = stdout_path.open("w", encoding="utf-8"), stderr_path.open("w", encoding="utf-8")
    process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
    try:
        import run_ecc006
        run_ecc006.wait_for_server(process, url)
        ready = mn005.gpu_snapshot()
        mn005.require_clean_gpu(ready, {process.pid})
    except Exception:
        stdout.close()
        stderr.close()
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
        raise
    return process, stdout, stderr, mn005.Client(url), {"command": command, "pid": process.pid, "before": before, "ready": ready}


def stop_server(process: subprocess.Popen[Any] | None, stdout: Any, stderr: Any, url: str) -> dict[str, Any]:
    lifecycle: dict[str, Any] = {"expected_termination": False}
    try:
        if process and process.poll() is None:
            lifecycle["expected_termination"] = True
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=15)
        lifecycle.update({"exit_code": process.poll() if process else None, "alive_after_cleanup": process.poll() is None if process else False, "health_after_cleanup": mn005.health(url)})
    finally:
        if stdout:
            stdout.close()
        if stderr:
            stderr.close()
    return lifecycle


def request(client: mn005.Client, content: str, maximum: int, definition: dict[str, Any]) -> dict[str, Any]:
    started, timer = mn005.v1.now(), time.perf_counter()
    prompt_tokens = mn005.v1.checked_prompt_tokens(client, content, maximum, definition["runtime"]["configured_context_size"])
    payload, response = client.complete(content, maximum)
    usage = response.get("usage", {}) if isinstance(response, dict) else {}
    return {"request_payload": payload, "response": response, "finish_reason": mn005.finish_reason(response), "planned_prompt_tokens": prompt_tokens, "completion_tokens": usage.get("completion_tokens"), "total_tokens": usage.get("total_tokens"), "started_at": started, "ended_at": mn005.v1.now(), "latency_ms": round((time.perf_counter() - timer) * 1000, 3)}


def persist_response(raw_dir: Path, ordinal: int, case_id: str, arm: str, stage: str, exchange: dict[str, Any], server: dict[str, Any]) -> Path:
    path = raw_dir / f"{ordinal:02d}-{case_id}-{arm}-{stage}-response.json"
    mn005.write_json_atomic(path, {"request_ordinal": ordinal, "case_id": case_id, "arm": arm, "stage": stage, "server": {"pid": server["pid"], "command": server["command"]}, **exchange})
    try:
        exchange["raw_evidence_path"] = str(path.relative_to(mn005.ROOT))
    except ValueError:
        exchange["raw_evidence_path"] = str(path)
    return path


def validate_received_response(exchange: dict[str, Any]) -> str:
    usage = exchange["response"].get("usage", {})
    if usage.get("prompt_tokens") != exchange["planned_prompt_tokens"]:
        raise mn005.ContractError("protocol invalid: runtime prompt token count differs from pre-request count")
    raw = mn005.response_content(exchange["response"])
    exchange["raw_text"] = raw
    exchange["prompt_tokens"] = usage.get("prompt_tokens")
    return raw


def source_for_execution(client: mn005.Client, case: dict[str, Any], ecc_definition: dict[str, Any], preflight_row: dict[str, Any]) -> dict[str, Any]:
    source = mn005.v1.source_for(client, case, ecc_definition)
    if source["source_sha256"] != preflight_row["source_sha256"]:
        raise mn005.ContractError("protocol invalid: source rendering differs from tokenizer preflight")
    return source


def arm_a_record(client: mn005.Client, definition: dict[str, Any], case: dict[str, Any], ecc_definition: dict[str, Any], preflight_row: dict[str, Any], ordinal: int, raw_dir: Path, server: dict[str, Any]) -> dict[str, Any]:
    source = source_for_execution(client, case, ecc_definition, preflight_row)
    stage_b = request(client, source["arm_a"], definition["budgets"]["arm_a"], definition)
    persist_response(raw_dir, ordinal, case["id"], "A", "final", stage_b, server)
    raw = validate_received_response(stage_b)
    evaluation = mn005.final_evaluation(case, raw, stage_b["finish_reason"])
    return {"request_ordinal": ordinal, "arm": "A", "case_id": case["id"], "source_sha256": source["source_sha256"], "source": source["context"], "expected_answer": case["answer"], "stage_b": stage_b, "evaluation": evaluation, "protocol_valid": True, "infrastructure_status": "complete", "stage_a_diagnostic": None}


def two_call_record(client: mn005.Client, definition: dict[str, Any], case: dict[str, Any], ecc_definition: dict[str, Any], preflight_row: dict[str, Any], arm: str, ordinal: int, artifact_dir: Path, raw_dir: Path, server: dict[str, Any]) -> dict[str, Any]:
    source = source_for_execution(client, case, ecc_definition, preflight_row)
    stage_a = request(client, mn005.stage_a_prompt(source, arm), definition["budgets"]["stage_a"], definition)
    persist_response(raw_dir, ordinal, case["id"], arm, "stage-a", stage_a, server)
    artifact = validate_received_response(stage_a).encode("utf-8")
    artifact_path = artifact_dir / f"{ordinal:02d}-{case['id']}-{arm}-stage-a.bin"
    if arm == "B":
        artifact_info = mn005.artifact_record(artifact_path, artifact)
        diagnostic = mn005.require_exact_control_artifact(artifact, stage_a["finish_reason"])
    else:
        diagnostic = None
        artifact_info = None
    stage_b_content, slot, rendered = mn005.stage_b_prompt(source, case, artifact)
    if arm == "B":
        artifact_info.update({"artifact_slot_sha256": mn005.v1.sha256_bytes(slot), "literal_equal": artifact == slot})
    if arm == "C":
        artifact_info = mn005.artifact_record(artifact_path, artifact, slot)
    if not artifact_info or not artifact_info.get("literal_equal", artifact == slot):
        raise mn005.ContractError("protocol invalid: literal Stage A transport failed")
    stage_b = request(client, stage_b_content, definition["budgets"]["stage_b"], definition)
    stage_b["artifact_slot_sha256"] = mn005.v1.sha256_bytes(slot)
    stage_b["artifact_slot_base64"] = base64.b64encode(slot).decode("ascii")
    stage_b["rendered_prompt_sha256"] = mn005.v1.sha256_bytes(rendered)
    persist_response(raw_dir, ordinal, case["id"], arm, "stage-b", stage_b, server)
    raw = validate_received_response(stage_b)
    if arm == "C":
        diagnostic = mn005.reconstruction_diagnostic(case, artifact, stage_a["finish_reason"])
    evaluation = mn005.final_evaluation(case, raw, stage_b["finish_reason"])
    return {"request_ordinal": ordinal, "arm": arm, "case_id": case["id"], "source_sha256": source["source_sha256"], "source": source["context"], "expected_answer": case["answer"], "stage_a": stage_a, "stage_b": stage_b, "artifact": artifact_info, "stage_a_diagnostic": diagnostic, "evaluation": evaluation, "protocol_valid": True, "infrastructure_status": "complete", "pair_latency_ms": round(stage_a["latency_ms"] + stage_b["latency_ms"], 3)}


def preflight(args: argparse.Namespace) -> Path:
    definition, cases, ecc_definition = mn005.load_definition()
    model = args.models_dir / definition["model"]["file"]
    identity = mn005.validate_runtime(definition, args.llama_server, model)
    snapshot = mn005.gpu_snapshot()
    mn005.require_clean_gpu(snapshot)
    raw = mn005.PREFLIGHT / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    process = stdout = stderr = None
    url = f"http://127.0.0.1:{args.port}"
    try:
        process, stdout, stderr, client, lifecycle = start_server(definition, args.llama_server, model, args.port, raw, "tokenizer-preflight-v2", static_cpu=True)
        value = mn005.preflight(client, definition, cases, ecc_definition)
        value.update({"runtime": identity, "environment_before": snapshot, "server": lifecycle, "repository_commit": mn005.command_result(["git", "rev-parse", "HEAD"])["stdout"].strip()})
    finally:
        lifecycle_end = stop_server(process, stdout, stderr, url)
    value["server_lifecycle_end"] = lifecycle_end
    path = mn005.PREFLIGHT / "preflight-v2.json"
    mn005.write_json_atomic(path, value)
    return path


def execute(args: argparse.Namespace) -> Path:
    definition, cases, ecc_definition = mn005.load_definition()
    if mn005.has_canonical_attempt():
        raise mn005.ContractError("a canonical valid attempt already exists; replication needs separate authorization")
    if mn005.command_result(["git", "status", "--porcelain", "--untracked-files=all"])["stdout"].strip():
        raise mn005.ContractError("canonical attempt requires a clean committed implementation checkpoint")
    preflight_value = mn005.load_json(mn005.PREFLIGHT / "preflight-v2.json")
    if not preflight_value.get("passed") or preflight_value.get("definition_fingerprint") != mn005.definition_fingerprint(definition):
        raise mn005.ContractError("missing or mismatched Gate B v2 tokenizer preflight")
    model = args.models_dir / definition["model"]["file"]
    identity = mn005.validate_runtime(definition, args.llama_server, model)
    initial_environment = mn005.gpu_snapshot()
    mn005.require_clean_gpu(initial_environment)
    attempt_id = mn005.next_attempt_id()
    if attempt_id != "attempt-0002":
        raise mn005.ContractError(f"unexpected next attempt identity: {attempt_id}")
    attempt = mn005.RUNS / attempt_id
    raw, artifacts = attempt / "raw", attempt / "artifacts"
    raw.mkdir(parents=True)
    artifacts.mkdir()
    metadata = {"attempt_id": attempt_id, "attempt_started_at": mn005.v1.now(), "contract_version": "gate_b_v2", "definition_fingerprint": mn005.definition_fingerprint(definition), "gate_a_sha256": definition["authority"]["gate_a_sha256"], "gate_b_v1_sha256": definition["authority"]["gate_b_v1_sha256"], "gate_b_v2_sha256": definition["authority"]["gate_b_v2_sha256"], "ecc006_fingerprint": definition["authority"]["ecc006_definition_fingerprint"], "model": definition["model"], "runtime": identity, "environment_before": initial_environment, "repository_commit": mn005.command_result(["git", "rev-parse", "HEAD"])["stdout"].strip(), "scheduled_order": ["A:ecc006-001", "A:ecc006-002", "A:ecc006-003", "A:ecc006-004", "A:ecc006-005", "A:ecc006-006", "B,C alternating by ECC-006 case order"]}
    mn005.write_json_atomic(attempt / "metadata.json", metadata)
    records_path = attempt / "results.jsonl"
    records: list[dict[str, Any]] = []
    arm_a: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    failure: dict[str, Any] | None = None
    ordinal = 0
    lookup = {row["case_id"]: row for row in preflight_value["cases"]}
    url = f"http://127.0.0.1:{args.port}"

    def run_server_unit(label: str, callback: Callable[[mn005.Client, dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
        process = stdout = stderr = None
        result: dict[str, Any] | None = None
        try:
            process, stdout, stderr, client, lifecycle = start_server(definition, args.llama_server, model, args.port, raw, label)
            result = callback(client, lifecycle)
            result["server_lifecycle_start"] = lifecycle
            return result
        finally:
            end = stop_server(process, stdout, stderr, url)
            if result is not None:
                result["server_lifecycle_end"] = end

    try:
        def arm_a_phase(client: mn005.Client, server: dict[str, Any]) -> dict[str, Any]:
            nonlocal ordinal
            for case in cases:
                ordinal += 1
                row = arm_a_record(client, definition, case, ecc_definition, lookup[case["id"]], ordinal, raw, server)
                arm_a.append(row)
                records.append(row)
                append_jsonl_durable(records_path, row)
            return {"arm": "A"}

        run_server_unit("arm-a-v2", arm_a_phase)
        for index, case in enumerate(cases):
            order = ("B", "C") if index % 2 == 0 else ("C", "B")
            pair: dict[str, Any] = {"case_id": case["id"]}
            for arm in order:
                ordinal += 1
                record = run_server_unit(f"{case['id']}-{arm}-v2", lambda client, server, arm=arm, ordinal=ordinal, case=case: two_call_record(client, definition, case, ecc_definition, lookup[case["id"]], arm, ordinal, artifacts, raw, server))
                records.append(record)
                append_jsonl_durable(records_path, record)
                pair[arm] = record
            pairs.append(pair)
    except mn005.ContractError as error:
        failure = {"classification": "environment_contaminated" if "environment_contaminated" in str(error) else "protocol_invalid" if "protocol invalid" in str(error) else "infrastructure_failure", "message": str(error), "captured_at": mn005.v1.now(), "environment": mn005.gpu_snapshot()}
    except (OSError, TimeoutError, urllib.error.URLError, ValueError, subprocess.SubprocessError) as error:
        failure = {"classification": "infrastructure_failure", "message": f"{type(error).__name__}: {error}", "captured_at": mn005.v1.now(), "environment": mn005.gpu_snapshot()}
    if failure:
        summary = {"attempt_id": attempt_id, "attempt_status": "experiment_invalid", "first_failure": failure, "completed_outcomes": len(records), "expected_outcomes": 18, "efficacy_classification": "not_applicable_due_to_invalid_experiment"}
    else:
        result = mn005.classify(arm_a, pairs, definition)
        summary = {"attempt_id": attempt_id, "attempt_status": "canonical_valid", "completed_outcomes": len(records), "expected_outcomes": 18, "efficacy_classification": result.pop("classification"), "analysis": result, "environment_after": mn005.gpu_snapshot()}
    mn005.write_json_atomic(attempt / "summary.json", summary)
    return attempt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "execute"))
    parser.add_argument("--models-dir", type=Path, default=DEFAULT_MODELS)
    parser.add_argument("--llama-server", type=Path, default=DEFAULT_SERVER)
    parser.add_argument("--port", type=int, default=18655)
    args = parser.parse_args()
    print(preflight(args) if args.command == "preflight" else execute(args))


if __name__ == "__main__":
    main()
