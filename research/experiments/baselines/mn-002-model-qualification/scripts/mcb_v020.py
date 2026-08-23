#!/usr/bin/env python3
"""MCB v0.2.0: versioned correction for audited output-contract defects."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

import mcb

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmark" / "v0.2.0"
CASES = BENCHMARK / "cases"
SCHEMAS = ROOT / "schemas" / "v0.2.0"
CONFIG = ROOT / "configs" / "mcb-v0.2.0.json"
RUNS = ROOT / "runs"
REPORT = ROOT / "reports" / "model-qualification-v0.2.0.md"
VERSION = "0.2.0"


def template_kwargs(filename: str) -> dict[str, bool] | None:
    if filename.startswith(("Qwen3-", "SmolLM3-")):
        return {"enable_thinking": False}
    return None


def benchmark_cases() -> list[dict[str, Any]]:
    cases = copy.deepcopy([*mcb.ins(), *mcb.struct(), *mcb.retrieve(), *mcb.state(), *mcb.cause()])
    for case in cases:
        case["version"] = 2
        if case["suite"] in {"state_tracking", "causal_reasoning"}:
            case["input"]["prompt"] += " Return only the answer, without punctuation or explanation."
    return cases


def write_definition() -> None:
    values = benchmark_cases()
    for suite in mcb.SUITES:
        entries = [entry for entry in values if entry["suite"] == suite]
        (CASES / f"{suite}.jsonl").parent.mkdir(parents=True, exist_ok=True)
        (CASES / f"{suite}.jsonl").write_text("".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in entries), encoding="utf-8")
    mcb.dump(BENCHMARK / "manifest.yaml", {"id": "mcb", "version": VERSION, "supersedes": "0.1.0", "change": "Clarify exact-only output contracts for state_tracking and causal_reasoning; preserve strict deterministic scoring.", "minimum_overall_score": 0.80, "total_cases": 100, "suites": [{"id": suite, "cases": 20, "critical": True, "minimum_score": mcb.LIMITS[suite]} for suite in mcb.SUITES]})
    schema = mcb.schemas()["benchmark-case.schema.json"]
    schema["properties"]["version"] = {"const": 2}
    mcb.dump(SCHEMAS / "benchmark-case.schema.json", schema)
    mcb.dump(CONFIG, {"benchmark_version": VERSION, "temperature": 0.0, "seed": 42, "context_size": 4096, "threads": 12, "gpu_layers": "all", "batch_size": 2048, "host": "127.0.0.1", "chat_template": "GGUF metadata via --jinja; native enable_thinking=false for verified Qwen3 and SmolLM3 templates"})


def load_cases() -> list[dict[str, Any]]:
    return [json.loads(line) for suite in mcb.SUITES for line in (CASES / f"{suite}.jsonl").read_text(encoding="utf-8").splitlines() if line]


def validate() -> None:
    cases = load_cases()
    counts = {suite: sum(item["suite"] == suite for item in cases) for suite in mcb.SUITES}
    if len(cases) != 100 or len({item["id"] for item in cases}) != 100 or any(count != 20 for count in counts.values()):
        raise RuntimeError(f"invalid v0.2.0 case counts: {counts}, total={len(cases)}")
    if any(item["version"] != 2 for item in cases):
        raise RuntimeError("v0.2.0 case version mismatch")
    print("Validated MCB v0.2.0: 100 cases, 20 per suite.")


def request(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    value = urllib.request.Request(url, json.dumps(payload).encode("utf-8"), {"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(value, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def evaluate(case: dict[str, Any], text: str) -> tuple[bool, Any]:
    return mcb.evalcase(case, text)


def run_model(model: Path, server: Path, port: int) -> Path:
    validate()
    cfg = mcb.load(CONFIG)
    run_id = f"{dt.datetime.now(dt.UTC):%Y%m%dT%H%M%SZ}-mcb-v020-{re.sub('[^a-z0-9]+', '-', model.stem.lower()).strip('-')}-{uuid.uuid4().hex[:8]}"
    run = RUNS / run_id
    raw = run / "raw"
    raw.mkdir(parents=True)
    command = [str(server), "-m", str(model), "--host", cfg["host"], "--port", str(port), "-c", str(cfg["context_size"]), "-t", str(cfg["threads"]), "-b", str(cfg["batch_size"]), "-ngl", str(cfg["gpu_layers"]), "-fa", "on", "--temp", "0", "--seed", "42", "--jinja", "--no-webui", "--metrics"]
    metadata = {"run_id": run_id, "created_at": dt.datetime.now(dt.UTC).isoformat(), "benchmark": {"id": "mcb", "version": VERSION}, "repository": {"commit": mcb.cmd(["git", "rev-parse", "HEAD"]).strip()}, "model": {"name": model.stem, "file": model.name, "size_bytes": model.stat().st_size, "sha256": mcb.digest(model)}, "inference": {**cfg, "chat_template_kwargs": template_kwargs(model.name)}, "command": {"server": command}}
    mcb.dump(run / "metadata.json", metadata)
    stdout, stderr = (raw / "llama-server.stdout.txt").open("w", encoding="utf-8"), (raw / "llama-server.stderr.txt").open("w", encoding="utf-8")
    records: list[dict[str, Any]] = []
    process = None
    problem = None
    try:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
        base = f"http://{cfg['host']}:{port}"
        for _ in range(180):
            if process.poll() is not None:
                raise RuntimeError(f"llama-server exited {process.returncode}")
            try:
                with urllib.request.urlopen(base + "/health", timeout=2) as health:
                    if health.status == 200:
                        break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(1)
        else:
            raise RuntimeError("llama-server startup timeout")
        for case in load_cases():
            message = "\n\n".join(part for part in (case["input"]["context"], case["input"]["prompt"]) if part)
            payload = {"messages": [{"role": "user", "content": message}], "temperature": 0, "seed": 42, "max_tokens": case["generation"]["max_tokens"]}
            if template_kwargs(model.name):
                payload["chat_template_kwargs"] = template_kwargs(model.name)
            started = time.perf_counter()
            try:
                response = request(base + "/v1/chat/completions", payload)
                text = response["choices"][0]["message"].get("content") or ""
                passed, parsed = evaluate(case, text)
                error = None
            except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError) as exc:
                response, text, parsed, passed = None, "", None, False
                error = {"type": "model_request_error", "message": f"{type(exc).__name__}: {exc}"}
            records.append({"case_id": case["id"], "request": payload, "output": {"text": text, "parsed": parsed, "response": response}, "evaluation": {"passed": passed, "score": float(passed)}, "timing": {"total_ms": round((time.perf_counter() - started) * 1000, 3)}, "error": error})
    except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError) as exc:
        problem = f"{type(exc).__name__}: {exc}"
    finally:
        if process and process.poll() is None:
            process.terminate()
            try: process.wait(20)
            except subprocess.TimeoutExpired: process.kill()
        stdout.close(); stderr.close()
    (run / "results.jsonl").write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    if problem or len(records) != 100:
        summary = {"run_id": run_id, "run_status": "invalid", "qualification": {"passed": None, "failure_reasons": [problem or f"only {len(records)} results"]}, "overall": None, "suites": {}}
    else:
        definition = {case["id"]: case for case in load_cases()}
        suites = {suite: [] for suite in mcb.SUITES}
        for record in records: suites[definition[record["case_id"]]["suite"]].append(record)
        score = {suite: {"cases": 20, "passed": sum(row["evaluation"]["passed"] for row in rows), "score": sum(row["evaluation"]["score"] for row in rows) / 20} for suite, rows in suites.items()}
        total = sum(row["evaluation"]["passed"] for row in records)
        overall = {"cases": 100, "passed": total, "score": total / 100}
        reasons = ([] if overall["score"] >= .8 else [f"overall {overall['score']:.2f} < 0.80"]) + [f"{suite} {value['score']:.2f} < {mcb.LIMITS[suite]:.2f}" for suite, value in score.items() if value["score"] < mcb.LIMITS[suite]]
        summary = {"run_id": run_id, "run_status": "valid", "qualification": {"passed": not reasons, "failure_reasons": reasons}, "overall": overall, "suites": score, "performance": {"source": "unchanged; see MCB v0.1.0 llama-bench evidence"}}
    mcb.dump(run / "summary.json", summary)
    print(f"{model.name}: {run_id}")
    return run


def report() -> None:
    latest = {}
    for directory in RUNS.glob("*mcb-v020*"):
        if (directory / "metadata.json").is_file() and (directory / "summary.json").is_file():
            latest[mcb.load(directory / "metadata.json")["model"]["file"]] = (mcb.load(directory / "metadata.json"), mcb.load(directory / "summary.json"))
    lines = ["# MN-002 Model Qualification — MCB v0.2.0", "", "v0.2.0 clarifies the exact-only output contract for state and causal suites and disables verified native thinking for Qwen3 and SmolLM3. It supersedes v0.1.0 capability scores; v0.1.0 raw evidence is preserved.", "", "| Model | Instruction | Structured | Retrieval | State | Causal | Overall | Qualification |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for name in mcb.MODELS_REQUIRED:
        metadata, summary = latest[name]
        row = [f"{summary['suites'][suite]['score']:.2f}" for suite in mcb.SUITES] + [f"{summary['overall']['score']:.2f}", "PASS" if summary["qualification"]["passed"] else "FAIL"]
        lines.append("| " + " | ".join([metadata["model"]["file"], *row]) + " |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-definition", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--run-all", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--models-dir", type=Path, default=mcb.MODELS)
    parser.add_argument("--llama-server", type=Path, default=mcb.BIN / "llama-server.exe")
    args = parser.parse_args()
    if args.write_definition: write_definition()
    if args.validate: validate()
    if args.run_all:
        for index, name in enumerate(mcb.MODELS_REQUIRED): run_model(args.models_dir / name, args.llama_server, 18200 + index)
    if args.report: report()


if __name__ == "__main__":
    main()
