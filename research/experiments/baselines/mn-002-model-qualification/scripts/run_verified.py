#!/usr/bin/env python3
"""Verified execution wrapper for MCB v0.1.0.

It keeps the base runner local to MN-002, disables Qwen3 native thinking through
the GGUF chat-template keyword, and fixes llama-bench's numeric GPU-layer syntax.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import mcb


def qwen_api(original):
    def request(url, payload):
        payload = dict(payload)
        payload["chat_template_kwargs"] = {"enable_thinking": False}
        return original(url, payload)
    return request


def latest_run(filename: str) -> Path:
    found = []
    for directory in mcb.RUNS.glob("*"):
        metadata = directory / "metadata.json"
        if metadata.is_file() and mcb.load(metadata)["model"]["file"] == filename:
            found.append(directory)
    return max(found, key=lambda item: item.name)


def bench(model: Path, run: Path, executable: Path, cfg: dict) -> None:
    command = [str(executable), "-m", str(model), "-p", str(cfg["performance"]["prompt_tokens"]), "-n", str(cfg["performance"]["generation_tokens"]), "-r", str(cfg["performance"]["repetitions"]), "-t", str(cfg["threads"]), "-ngl", "-1", "-fa", "on", "-o", "json"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    raw = run / "raw"
    (raw / "llama-bench-verified.stdout.txt").write_text(result.stdout or "", encoding="utf-8")
    (raw / "llama-bench-verified.stderr.txt").write_text(result.stderr or "", encoding="utf-8")
    prompt = generation = None
    try:
        payload = json.loads(result.stdout)
        for item in payload.get("tests", []):
            name = str(item.get("test", "")).lower()
            rate = item.get("t/s")
            if rate is not None and "pp" in name:
                prompt = float(rate)
            if rate is not None and "tg" in name:
                generation = float(rate)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    metadata = mcb.load(run / "metadata.json")
    metadata["command"]["benchmark_verified"] = command
    mcb.dump(run / "metadata.json", metadata)
    summary = mcb.load(run / "summary.json")
    summary["performance"]["llama_bench_generation_tokens_per_second"] = generation
    summary["performance"]["llama_bench_prompt_tokens_per_second"] = prompt
    mcb.dump(run / "summary.json", summary)
    mcb.validate_run(run)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-all", action="store_true")
    parser.add_argument("--model", action="append")
    parser.add_argument("--models-dir", type=Path, default=mcb.MODELS)
    parser.add_argument("--llama-server", type=Path, default=mcb.BIN / "llama-server.exe")
    parser.add_argument("--llama-bench", type=Path, default=mcb.BIN / "llama-bench.exe")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    names = args.model or (list(mcb.MODELS_REQUIRED) if args.run_all else [])
    if not names:
        parser.error("choose --run-all or --model")
    config = mcb.load(mcb.F / "qualification-config.json")
    for index, name in enumerate(names):
        model = args.models_dir / name
        if not model.is_file():
            print(f"MISSING MODEL: {name}")
            continue
        original = mcb.api
        if name.startswith("Qwen3-"):
            mcb.api = qwen_api(original)
        try:
            mcb.run(model, args.llama_server, args.llama_bench, 18100 + index)
            bench(model, latest_run(name), args.llama_bench, config)
        except (OSError, RuntimeError, TimeoutError, ValueError, subprocess.SubprocessError) as exc:
            print(f"MODEL RUN ERROR {name}: {type(exc).__name__}: {exc}")
        finally:
            mcb.api = original
    if args.report:
        mcb.report()


if __name__ == "__main__":
    main()
