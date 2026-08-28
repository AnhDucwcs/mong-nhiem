#!/usr/bin/env python3
"""Run the canonical ECC-002 direct-context confusable retrieval experiment."""
from __future__ import annotations

import argparse
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
import uuid
from pathlib import Path
from typing import Any

import ecc002

DEFAULT_MODELS = Path(r"D:\Code\mong-nhiem\artifacts\models\mn-002")
DEFAULT_SERVER = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")


def command_output(arguments: list[str]) -> str:
    process = subprocess.run(arguments, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    return (process.stdout or "") + (process.stderr or "")


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def runtime_identity(server: Path) -> dict[str, Any]:
    raw = command_output([str(server), "--version"])
    match = re.search(r"version:\s*(.*?)\s*\(build\s+(\d+),\s*commit\s+([0-9a-f]+)", raw, re.IGNORECASE)
    return {"backend": "llama.cpp", "version": match.group(1).strip() if match else None, "build": match.group(2) if match else None, "commit": match.group(3) if match else None, "raw_version_output": raw}


def hardware_identity() -> dict[str, Any]:
    raw = command_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"])
    parts = [part.strip() for part in next((line for line in raw.splitlines() if line.strip()), "").split(",")]
    try:
        ram_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        ram_bytes = None
    return {"os": platform.platform() or None, "cpu": platform.processor() or None, "ram_bytes": ram_bytes, "gpu": parts[0] if parts else None, "vram_bytes": int(parts[1]) * 1024 * 1024 if len(parts) > 1 and parts[1].isdigit() else None, "driver": parts[2] if len(parts) > 2 else None, "cuda": None}


def wait_for_server(process: subprocess.Popen[Any], base_url: str) -> None:
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise ecc002.ContractError(f"llama-server exited during startup: {process.returncode}")
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=2) as response:
                if response.status == 200:
                    return
        except (TimeoutError, urllib.error.URLError):
            time.sleep(0.5)
    raise ecc002.ContractError("llama-server did not become healthy within 180 seconds")


def parse_levels(values: list[int] | None, allowed: list[int]) -> list[int]:
    selected = values or allowed
    if len(selected) != len(set(selected)) or any(value not in allowed for value in selected):
        raise ecc002.ContractError(f"context levels must be unique members of {allowed}")
    return sorted(selected)


def run(args: argparse.Namespace) -> Path:
    definition, cases = ecc002.load_definition()
    models = ecc002.load_json(ecc002.CONFIGS / "models.json")
    if args.model not in models:
        raise ecc002.ContractError(f"unknown model {args.model}; choose from {sorted(models)}")
    model_config = models[args.model]
    model = args.models_dir / model_config["file"]
    if not model.is_file() or not args.llama_server.is_file():
        raise ecc002.ContractError(f"missing model/runtime dependency: model={model.is_file()} server={args.llama_server.is_file()}")
    all_levels = definition["independent_variable"]["levels"]
    levels = parse_levels(args.context_level, all_levels)
    if args.case:
        requested = set(args.case)
        selected_cases = [case for case in cases if case["id"] in requested]
        if {case["id"] for case in selected_cases} != requested:
            raise ecc002.ContractError("one or more requested case IDs are unknown")
    else:
        selected_cases = cases[: args.case_limit] if args.case_limit else cases
    complete = levels == all_levels and [case["id"] for case in selected_cases] == [case["id"] for case in cases]
    repository_commit = command_output(["git", "rev-parse", "HEAD"]).strip()
    repository_dirty = bool(command_output(["git", "status", "--porcelain", "--untracked-files=all"]).strip())
    created = dt.datetime.now(dt.UTC)
    run_id = f"{created:%Y%m%dT%H%M%SZ}-ecc-002-{args.model}-{uuid.uuid4().hex[:8]}"
    run_dir, raw_dir = args.output_dir / run_id, args.output_dir / run_id / "raw"
    raw_dir.mkdir(parents=True)
    inference = {**definition["inference"], "configured_context_size": definition["token_budget"]["configured_context_size"], "output_tokens": definition["token_budget"]["output_tokens"], "chat_template_kwargs": model_config["chat_template_kwargs"]}
    kwargs_json = json.dumps(model_config["chat_template_kwargs"], separators=(",", ":"))
    server_command = [str(args.llama_server), "-m", str(model), "--host", args.host, "--port", str(args.port), "-c", str(inference["configured_context_size"]), "-t", str(inference["threads"]), "-b", str(inference["batch_size"]), "-np", str(inference["parallel_slots"]), "-fa", "on" if inference["flash_attention"] else "off", "--temp", "0", "--seed", str(inference["seed"]), "--jinja", "--no-webui", "--no-cache-prompt", "--metrics", "--chat-template-kwargs", kwargs_json]
    runner_levels = [part for level in levels for part in ("--context-level", str(level))]
    metadata = {"run_id": run_id, "created_at": created.isoformat(), "experiment": {"id": definition["id"], "version": definition["version"]}, "definition_fingerprint": ecc002.definition_fingerprint(), "repository": {"commit": repository_commit, "dirty": repository_dirty}, "model": {"key": args.model, "name": model.stem, "file": model.name, "size_bytes": model.stat().st_size, "sha256": file_digest(model), "qualified_by": model_config["qualified_by"]}, "runtime": runtime_identity(args.llama_server), "hardware": hardware_identity(), "inference": inference, "selection": {"context_levels": levels, "case_ids": [case["id"] for case in selected_cases], "complete_definition_coverage": complete}, "command": {"server": server_command, "runner": ["run_ecc002.py", "--model", args.model, *runner_levels]}}
    ecc002.dump_json(run_dir / "metadata.json", metadata)
    stdout = (raw_dir / "llama-server.stdout.txt").open("w", encoding="utf-8")
    stderr = (raw_dir / "llama-server.stderr.txt").open("w", encoding="utf-8")
    process: subprocess.Popen[Any] | None = None
    records: list[dict[str, Any]] = []
    try:
        process = subprocess.Popen(server_command, stdout=stdout, stderr=stderr)
        client = ecc002.ServerClient(f"http://{args.host}:{args.port}", model_config["chat_template_kwargs"])
        wait_for_server(process, client.base_url)
        for level in levels:
            for case in selected_cases:
                built = ecc002.build_case(client, case, level, definition)
                started, error = time.perf_counter(), None
                try:
                    request, response = client.complete(built.content, inference)
                    raw_text = response["choices"][0]["message"].get("content") or ""
                    if response.get("usage", {}).get("prompt_tokens") != built.actual_input_tokens:
                        raise ecc002.ContractError(f"{case['id']} target {level}: preflight/API prompt-token disagreement")
                    passed, normalized = ecc002.evaluate(case["answer"], raw_text)
                except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError, ecc002.ContractError) as exc:
                    request = {"messages": [{"role": "user", "content": built.content}], "temperature": inference["temperature"], "seed": inference["seed"], "max_tokens": inference["output_tokens"], "chat_template_kwargs": model_config["chat_template_kwargs"]}
                    response, raw_text, normalized, passed = None, "", "", False
                    error = {"type": "model_request_error", "message": f"{type(exc).__name__}: {exc}"}
                record = {**{key: value for key, value in ecc002.built_case_dict(built).items() if key != "content"}, "configured_context_size": inference["configured_context_size"], "output_token_budget": inference["output_tokens"], "request": request, "output": {"raw_text": raw_text, "normalized_text": normalized, "response": response}, "evaluation": {"passed": passed, "score": float(passed)}, "truncated": False, "timing": {"total_ms": round((time.perf_counter() - started) * 1000, 3)}, "error": error}
                records.append(record)
                print(f"{case['id']} @ {level}: {'PASS' if passed else 'FAIL'} ({built.actual_input_tokens} tokens)", flush=True)
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(20)
            except subprocess.TimeoutExpired:
                process.kill()
        stdout.close()
        stderr.close()
        (run_dir / "results.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
        ecc002.dump_json(run_dir / "summary.json", ecc002.summarize(run_id, records, levels, [case["id"] for case in selected_cases], complete))
    ecc002.validate_run(run_dir)
    print(f"Validated run: {run_dir}")
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, choices=sorted(ecc002.load_json(ecc002.CONFIGS / "models.json")))
    parser.add_argument("--context-level", action="append", type=int)
    parser.add_argument("--case", action="append")
    parser.add_argument("--case-limit", type=int)
    parser.add_argument("--models-dir", type=Path, default=DEFAULT_MODELS)
    parser.add_argument("--llama-server", type=Path, default=DEFAULT_SERVER)
    parser.add_argument("--output-dir", type=Path, default=ecc002.RUNS)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18502)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
