#!/usr/bin/env python3
"""Materialize the frozen MN-004 source inventory and run tokenizer-only hard gates."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import mn004


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


def wait_for_server(process: subprocess.Popen[Any], base_url: str) -> None:
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise mn004.ContractError(f"llama-server exited during tokenizer preflight: {process.returncode}")
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=2) as response:
                if response.status == 200:
                    return
        except (TimeoutError, urllib.error.URLError):
            time.sleep(0.5)
    raise mn004.ContractError("llama-server did not become healthy during tokenizer preflight")


def start_server(server: Path, model: Path, definition: dict[str, Any], kwargs: dict[str, Any], port: int) -> subprocess.Popen[Any]:
    runtime = definition["runtime"]
    command = [str(server), "-m", str(model), "--host", "127.0.0.1", "--port", str(port), "-c", str(runtime["configured_context_size"]), "-t", str(runtime["threads"]), "-b", str(runtime["batch_size"]), "-np", str(runtime["parallel_slots"]), "-fa", "on" if runtime["flash_attention"] else "off", "--temp", "0", "--seed", str(runtime["seed"]), "--jinja", "--no-webui", "--no-cache-prompt", "--metrics", "--chat-template-kwargs", json.dumps(kwargs, separators=(",", ":"))]
    return subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def verify_runtime_and_model(server: Path, model: Path, model_key: str, definition: dict[str, Any]) -> dict[str, Any]:
    if not server.is_file() or not model.is_file():
        raise mn004.ContractError(f"missing runtime dependency: server={server.is_file()} model={model.is_file()}")
    identity = runtime_identity(server)
    frozen = definition["runtime"]
    for field in ("backend", "version", "build", "commit"):
        if identity[field] != frozen[field]:
            raise mn004.ContractError(f"runtime {field} mismatch: expected {frozen[field]!r}, saw {identity[field]!r}")
    observed = file_digest(model)
    if observed != definition["models"][model_key]["sha256"]:
        raise mn004.ContractError(f"{model_key} model hash mismatch")
    return {"runtime": identity, "model": {"key": model_key, "file": model.name, "sha256": observed}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    configs = mn004.load_json(mn004.CONFIGS / "models.json")
    parser.add_argument("--models-dir", type=Path, default=Path(configs["default_models_dir"]))
    parser.add_argument("--llama-server", type=Path, default=Path(configs["default_llama_server"]))
    parser.add_argument("--port", type=int, default=18604)
    args = parser.parse_args()
    definition = mn004.validate_definition()
    llama_model = args.models_dir / definition["models"]["llama-3.2-3b"]["file"]
    qwen_model = args.models_dir / definition["models"]["qwen3-4b"]["file"]
    identities = {
        "llama-3.2-3b": verify_runtime_and_model(args.llama_server, llama_model, "llama-3.2-3b", definition),
        "qwen3-4b": verify_runtime_and_model(args.llama_server, qwen_model, "qwen3-4b", definition),
    }
    process: subprocess.Popen[Any] | None = None
    try:
        process = start_server(args.llama_server, llama_model, definition, definition["models"]["llama-3.2-3b"]["chat_template_kwargs"], args.port)
        base_url = f"http://127.0.0.1:{args.port}"
        wait_for_server(process, base_url)
        llama_client = mn004.ServerClient(base_url, definition["models"]["llama-3.2-3b"]["chat_template_kwargs"])
        inventory = mn004.materialize_inventory(llama_client, definition)
        mn004.validate_inventory(inventory, llama_client, definition)
        mn004.dump_json(mn004.DEFINITION / "source-inventory.json", inventory)
        llama_preflight = mn004.preflight_inventory(llama_client, inventory, "llama-3.2-3b", definition)
        llama_preflight["identity"] = identities["llama-3.2-3b"]
        mn004.dump_json(mn004.DEFINITION / "preflight-llama-3.2-3b.json", llama_preflight)
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=5)
    process = None
    try:
        qwen_port = args.port + 1
        process = start_server(args.llama_server, qwen_model, definition, definition["models"]["qwen3-4b"]["chat_template_kwargs"], qwen_port)
        base_url = f"http://127.0.0.1:{qwen_port}"
        wait_for_server(process, base_url)
        qwen_client = mn004.ServerClient(base_url, definition["models"]["qwen3-4b"]["chat_template_kwargs"])
        qwen_preflight = mn004.preflight_inventory(qwen_client, inventory, "qwen3-4b", definition)
        qwen_preflight["identity"] = identities["qwen3-4b"]
        mn004.dump_json(mn004.DEFINITION / "preflight-qwen3-4b.json", qwen_preflight)
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=5)
    statuses = {"llama-3.2-3b": llama_preflight["status"], "qwen3-4b": qwen_preflight["status"]}
    mn004.dump_json(mn004.DEFINITION / "preflight-summary.json", {"definition_fingerprint": mn004.definition_fingerprint(definition), "inventory_fingerprint": inventory["inventory_fingerprint"], "statuses": statuses, "contract_executable": all(value == "feasible" for value in statuses.values())})
    print(json.dumps(statuses, sort_keys=True))
    if not all(value == "feasible" for value in statuses.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
