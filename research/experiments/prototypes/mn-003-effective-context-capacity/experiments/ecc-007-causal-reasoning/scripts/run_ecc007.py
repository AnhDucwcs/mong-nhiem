#!/usr/bin/env python3
"""Run the frozen ECC-007 direct-context causal-reasoning experiment."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

import ecc007

sys.path.insert(0, str(ecc007.ECC006))
import run_ecc006 as common

DEFAULT_MODELS, DEFAULT_SERVER = common.DEFAULT_MODELS, common.DEFAULT_SERVER


def wait_for_server(process: subprocess.Popen[Any], base_url: str) -> None:
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise ecc007.ContractError(f"llama-server exited during startup: {process.returncode}")
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=2) as response:
                if response.status == 200:
                    return
        except (TimeoutError, urllib.error.URLError):
            time.sleep(.5)
    raise ecc007.ContractError("llama-server did not become healthy within 180 seconds")


def parse_levels(values: list[int] | None, allowed: list[int]) -> list[int]:
    selected = values or allowed
    if len(selected) != len(set(selected)) or any(value not in allowed for value in selected):
        raise ecc007.ContractError(f"context levels must be unique members of {allowed}")
    return sorted(selected)


def run(args: argparse.Namespace) -> Path:
    definition, cases = ecc007.load_definition()
    model_configs = ecc007.load_json(ecc007.CONFIGS / "models.json")
    model_config = model_configs[args.model]
    model = args.models_dir / model_config["file"]
    if not model.is_file() or not args.llama_server.is_file():
        raise ecc007.ContractError(f"missing model/runtime dependency: model={model.is_file()} server={args.llama_server.is_file()}")
    levels = parse_levels(args.context_level, definition["independent_variable"]["requested_input_tokens"]["levels"])
    selected_cases = cases[:args.case_limit] if args.case_limit else cases
    complete = levels == definition["independent_variable"]["requested_input_tokens"]["levels"] and selected_cases == cases
    created = dt.datetime.now(dt.UTC)
    run_id = f"{created:%Y%m%dT%H%M%SZ}-ecc-007-{args.model}-{uuid.uuid4().hex[:8]}"
    run_dir, raw_dir = args.output_dir / run_id, args.output_dir / run_id / "raw"
    raw_dir.mkdir(parents=True)
    inference = {**definition["inference"], "configured_context_size": definition["token_budget"]["configured_context_size"], "output_tokens": definition["token_budget"]["output_tokens"], "chat_template_kwargs": model_config["chat_template_kwargs"]}
    template_json = json.dumps(model_config["chat_template_kwargs"], separators=(",", ":"))
    server_command = [str(args.llama_server), "-m", str(model), "--host", args.host, "--port", str(args.port), "-c", str(inference["configured_context_size"]), "-t", str(inference["threads"]), "-b", str(inference["batch_size"]), "-np", str(inference["parallel_slots"]), "-fa", "on" if inference["flash_attention"] else "off", "--temp", "0", "--seed", str(inference["seed"]), "--jinja", "--no-webui", "--no-cache-prompt", "--metrics", "--chat-template-kwargs", template_json]
    metadata = {
        "run_id": run_id, "created_at": created.isoformat(), "experiment": {"id": definition["id"], "version": definition["version"]}, "definition_fingerprint": ecc007.definition_fingerprint(),
        "repository": {"commit": common.command_output(["git", "rev-parse", "HEAD"]).strip(), "dirty": bool(common.command_output(["git", "status", "--porcelain", "--untracked-files=all"]).strip())},
        "model": {"key": args.model, "name": model.stem, "file": model.name, "size_bytes": model.stat().st_size, "sha256": common.file_digest(model), "qualified_by": model_config["qualified_by"]},
        "runtime": common.runtime_identity(args.llama_server), "hardware": common.hardware_identity(), "inference": inference,
        "selection": {"context_levels": levels, "case_ids": [case["id"] for case in selected_cases], "complete_definition_coverage": complete},
        "command": {"server": server_command, "runner": ["run_ecc007.py", "--model", args.model]},
    }
    ecc007.dump_json(run_dir / "metadata.json", metadata)
    stdout = (raw_dir / "llama-server.stdout.txt").open("w", encoding="utf-8")
    stderr = (raw_dir / "llama-server.stderr.txt").open("w", encoding="utf-8")
    process: subprocess.Popen[Any] | None = None
    records: list[dict[str, Any]] = []
    try:
        process = subprocess.Popen(server_command, stdout=stdout, stderr=stderr)
        base_url = f"http://{args.host}:{args.port}"
        wait_for_server(process, base_url)
        client = ecc007.ServerClient(base_url, model_config["chat_template_kwargs"])
        for level in levels:
            for case in selected_cases:
                built = ecc007.build_case(client, case, level, definition)
                started, error = time.perf_counter(), None
                try:
                    request, response = client.complete(built.content, inference)
                    raw = response["choices"][0]["message"].get("content") or ""
                    observed = response.get("usage", {}).get("prompt_tokens")
                    if observed != built.actual_input_tokens:
                        raise ecc007.ContractError(f"{case['id']} target {level}: preflight={built.actual_input_tokens}, API={observed}")
                    passed, normalized = ecc007.evaluate(case, raw)
                except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError, ecc007.ContractError) as exc:
                    request = {"messages": [{"role": "user", "content": built.content}], "temperature": inference["temperature"], "seed": inference["seed"], "max_tokens": inference["output_tokens"], "chat_template_kwargs": model_config["chat_template_kwargs"]}
                    response, raw, normalized, passed = None, "", "", False
                    error = {"type": "model_request_error", "message": f"{type(exc).__name__}: {exc}"}
                record = {**{key: value for key, value in ecc007.built_case_dict(built).items() if key != "content"}, "configured_context_size": inference["configured_context_size"], "output_token_budget": inference["output_tokens"], "request": request, "output": {"raw_text": raw, "normalized_text": normalized, "response": response}, "evaluation": {"passed": passed, "score": float(passed)}, "failure": ecc007.failure(case, raw, error), "truncated": False, "timing": {"total_ms": round((time.perf_counter() - started) * 1000, 3)}, "error": error}
                records.append(record)
                print(f"{case['id']} @ {level}: {'PASS' if passed else 'FAIL'} ({built.actual_input_tokens} tokens)", flush=True)
    finally:
        if process and process.poll() is None:
            process.terminate()
            try: process.wait(20)
            except subprocess.TimeoutExpired: process.kill()
        stdout.close(); stderr.close()
        (run_dir / "results.jsonl").write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
        ecc007.dump_json(run_dir / "summary.json", ecc007.summarize(run_id, records, levels, [case["id"] for case in selected_cases], complete))
    ecc007.validate_run(run_dir)
    print(f"Validated run: {run_dir}")
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, choices=sorted(ecc007.load_json(ecc007.CONFIGS / "models.json")))
    parser.add_argument("--context-level", action="append", type=int)
    parser.add_argument("--case-limit", type=int)
    parser.add_argument("--models-dir", type=Path, default=DEFAULT_MODELS)
    parser.add_argument("--llama-server", type=Path, default=DEFAULT_SERVER)
    parser.add_argument("--output-dir", type=Path, default=ecc007.RUNS)
    parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=18508)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
