#!/usr/bin/env python3
"""Run the canonical Qwen-only ECC-005 position-confirmation experiment."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
import urllib.error
import uuid
from pathlib import Path
from typing import Any

import ecc005

ECC002_SCRIPTS = ecc005.ROOT.parent / "ecc-002-confusable-context-retrieval" / "scripts"
sys.path.insert(0, str(ECC002_SCRIPTS))
from run_ecc002 import (
    DEFAULT_MODELS,
    DEFAULT_SERVER,
    command_output,
    file_digest,
    hardware_identity,
    parse_levels,
    runtime_identity,
    wait_for_server,
)


def parse_positions(values: list[str] | None, allowed: list[str]) -> list[str]:
    selected = values or allowed
    if len(selected) != len(set(selected)) or any(value not in allowed for value in selected):
        raise ecc005.ContractError(f"evidence positions must be unique members of {allowed}")
    return [position for position in allowed if position in selected]


def run(args: argparse.Namespace) -> Path:
    definition, cases = ecc005.load_definition()
    models = ecc005.load_json(ecc005.CONFIGS / "models.json")
    model_config = models[args.model]
    model = args.models_dir / model_config["file"]
    if not model.is_file() or not args.llama_server.is_file():
        raise ecc005.ContractError(
            f"missing model/runtime dependency: model={model.is_file()} server={args.llama_server.is_file()}"
        )
    all_levels = definition["independent_variables"]["requested_input_tokens"]["levels"]
    all_positions = [item["id"] for item in ecc005.positions(definition)]
    levels = parse_levels(args.context_level, all_levels)
    selected_positions = parse_positions(args.position, all_positions)
    selected_cases = cases[: args.case_limit] if args.case_limit else cases
    complete = (
        levels == all_levels
        and selected_positions == all_positions
        and [case["id"] for case in selected_cases] == [case["id"] for case in cases]
    )
    commit = command_output(["git", "rev-parse", "HEAD"]).strip()
    dirty = bool(command_output(["git", "status", "--porcelain", "--untracked-files=all"]).strip())
    created = dt.datetime.now(dt.UTC)
    run_id = f"{created:%Y%m%dT%H%M%SZ}-ecc-005-{args.model}-{uuid.uuid4().hex[:8]}"
    run_dir, raw_dir = args.output_dir / run_id, args.output_dir / run_id / "raw"
    raw_dir.mkdir(parents=True)
    inference = {
        **definition["inference"],
        "configured_context_size": definition["token_budget"]["configured_context_size"],
        "output_tokens": definition["token_budget"]["output_tokens"],
        "chat_template_kwargs": model_config["chat_template_kwargs"],
    }
    kwargs_json = json.dumps(model_config["chat_template_kwargs"], separators=(",", ":"))
    server_command = [
        str(args.llama_server), "-m", str(model), "--host", args.host, "--port", str(args.port),
        "-c", str(inference["configured_context_size"]), "-t", str(inference["threads"]),
        "-b", str(inference["batch_size"]), "-np", str(inference["parallel_slots"]),
        "-fa", "on" if inference["flash_attention"] else "off", "--temp", "0", "--seed",
        str(inference["seed"]), "--jinja", "--no-webui", "--no-cache-prompt", "--metrics",
        "--chat-template-kwargs", kwargs_json,
    ]
    runner_command = [
        "run_ecc005.py", "--model", args.model,
        *[part for level in levels for part in ("--context-level", str(level))],
        *[part for position in selected_positions for part in ("--position", position)],
        "--restart-server-per-position",
    ]
    metadata = {
        "run_id": run_id, "created_at": created.isoformat(),
        "experiment": {"id": definition["id"], "version": definition["version"]},
        "definition_fingerprint": ecc005.definition_fingerprint(),
        "repository": {"commit": commit, "dirty": dirty},
        "model": {"key": args.model, "name": model.stem, "file": model.name,
                  "size_bytes": model.stat().st_size, "sha256": file_digest(model),
                  "qualified_by": model_config["qualified_by"]},
        "runtime": runtime_identity(args.llama_server), "hardware": hardware_identity(),
        "inference": inference,
        "selection": {"context_levels": levels, "evidence_positions": selected_positions,
                      "case_ids": [case["id"] for case in selected_cases],
                      "complete_definition_coverage": complete},
        "command": {"server": server_command, "runner": runner_command},
    }
    ecc005.dump_json(run_dir / "metadata.json", metadata)
    stdout = (raw_dir / "llama-server.stdout.txt").open("w", encoding="utf-8")
    stderr = (raw_dir / "llama-server.stderr.txt").open("w", encoding="utf-8")
    process: subprocess.Popen[Any] | None = None
    records: list[dict[str, Any]] = []

    def start_server() -> ecc005.ServerClient:
        nonlocal process
        process = subprocess.Popen(server_command, stdout=stdout, stderr=stderr)
        client = ecc005.ServerClient(f"http://{args.host}:{args.port}", model_config["chat_template_kwargs"])
        wait_for_server(process, client.base_url)
        return client

    def stop_server() -> None:
        nonlocal process
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(20)
            except subprocess.TimeoutExpired:
                process.kill()
        process = None

    try:
        for level in levels:
            for position in selected_positions:
                client = start_server()
                for case in selected_cases:
                    built = ecc005.build_case(client, case, level, position, definition)
                    started, error = time.perf_counter(), None
                    try:
                        request, response = client.complete(built.content, inference)
                        raw_text = response["choices"][0]["message"].get("content") or ""
                        if response.get("usage", {}).get("prompt_tokens") != built.actual_input_tokens:
                            raise ecc005.ContractError(
                                f"{case['id']} {position}/{level}: preflight/API prompt-token disagreement"
                            )
                        passed, normalized = ecc005.ecc002.evaluate(case["answer"], raw_text)
                        failure = ecc005.classify_failure(
                            case, raw_text, built.distractor_pairs, position, definition
                        )
                    except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError, ecc005.ContractError) as exc:
                        request = {"messages": [{"role": "user", "content": built.content}],
                                   "temperature": inference["temperature"], "seed": inference["seed"],
                                   "max_tokens": inference["output_tokens"],
                                   "chat_template_kwargs": model_config["chat_template_kwargs"]}
                        response, raw_text, normalized, passed, failure = None, "", "", False, None
                        error = {"type": "model_request_error", "message": f"{type(exc).__name__}: {exc}"}
                    record = {
                        **{key: value for key, value in ecc005.built_case_dict(built).items() if key != "content"},
                        "configured_context_size": inference["configured_context_size"],
                        "output_token_budget": inference["output_tokens"], "request": request,
                        "output": {"raw_text": raw_text, "normalized_text": normalized, "response": response},
                        "evaluation": {"passed": passed, "score": float(passed)}, "failure": failure,
                        "truncated": False,
                        "timing": {"total_ms": round((time.perf_counter() - started) * 1000, 3)}, "error": error,
                    }
                    records.append(record)
                    print(f"{case['id']} {position} @ {level}: {'PASS' if passed else 'FAIL'} ({built.actual_input_tokens} tokens)", flush=True)
                stop_server()
    finally:
        stop_server()
        stdout.close()
        stderr.close()
        (run_dir / "results.jsonl").write_text(
            "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in records), encoding="utf-8"
        )
        ecc005.dump_json(
            run_dir / "summary.json",
            ecc005.summarize(run_id, records, levels, selected_positions,
                             [case["id"] for case in selected_cases], complete, definition),
        )
    ecc005.validate_run(run_dir)
    print(f"Validated run: {run_dir}")
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="qwen3-4b", choices=["qwen3-4b"])
    parser.add_argument("--context-level", action="append", type=int)
    parser.add_argument("--position", action="append")
    parser.add_argument("--case-limit", type=int)
    parser.add_argument("--models-dir", type=Path, default=DEFAULT_MODELS)
    parser.add_argument("--llama-server", type=Path, default=DEFAULT_SERVER)
    parser.add_argument("--output-dir", type=Path, default=ecc005.RUNS)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18505)
    parser.add_argument("--restart-server-per-position", action="store_true", help=argparse.SUPPRESS)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
