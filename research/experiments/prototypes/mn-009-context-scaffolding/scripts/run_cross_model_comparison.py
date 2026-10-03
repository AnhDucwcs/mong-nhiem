#!/usr/bin/env python3
"""Run 3-Model Downstream Comparison on MN-009 Benchmark Suite:
1. Llama-3.2-3B-Instruct-Q4_K_M.gguf
2. Qwen3-4B-Q4_K_M.gguf
3. Qwen3.5-2B-Q4_K_M.gguf
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[5]
PROTOTYPE_ROOT = Path(__file__).resolve().parents[1]

SERVER_BIN = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")
MODELS_DIR = REPO_ROOT / "artifacts" / "models" / "mn-002"
CASES_FILE = PROTOTYPE_ROOT / "definition" / "corpus-v1" / "cases.jsonl"
PACKED_FILE = PROTOTYPE_ROOT / "runs" / "mn009-execution-run-0002-qwen35" / "packed_contexts.jsonl"
RUNS_DIR = PROTOTYPE_ROOT / "runs"

MODELS = [
    {"name": "Llama-3.2-3B", "file": MODELS_DIR / "Llama-3.2-3B-Instruct-Q4_K_M.gguf"},
    {"name": "Qwen3-4B", "file": MODELS_DIR / "Qwen3-4B-Q4_K_M.gguf"},
    {"name": "Qwen3.5-2B", "file": MODELS_DIR / "Qwen3.5-2B-Q4_K_M.gguf"},
]


def check_health(host: str, port: int) -> bool:
    try:
        url = f"http://{host}:{port}/health"
        req = urllib.request.Request(url, headers={"User-Agent": "cross-model-runner"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False


def wait_for_server(host: str, port: int, timeout_sec: int = 60) -> bool:
    start = time.time()
    while time.time() - start < timeout_sec:
        if check_health(host, port):
            return True
        time.sleep(0.5)
    return False


def request_chat(prompt: str, max_tokens: int = 64, host: str = "127.0.0.1", port: int = 18502) -> dict[str, Any]:
    url = f"http://{host}:{port}/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "seed": 42,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "cross-model-runner"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    elapsed_ms = (time.perf_counter() - t0) * 1000

    choice = data["choices"][0]
    raw_content = choice["message"].get("content", "").strip()
    # Strip think tags if any exist
    cleaned = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
    usage = data.get("usage", {})

    return {
        "answer": cleaned,
        "total_ms": round(elapsed_ms, 2),
        "completion_tokens": usage.get("completion_tokens", 0),
    }


def normalize(text: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return " ".join(cleaned.split())


def check_exact_or_contained(prediction: str, oracle: str) -> bool:
    norm_p = normalize(prediction)
    norm_o = normalize(oracle)
    if not norm_p or not norm_o:
        return False
    if norm_o in norm_p or norm_p in norm_o:
        return True
    tokens_o = set(norm_o.split())
    tokens_p = set(norm_p.split())
    stop_tokens = {"at", "is", "the", "a", "an", "and", "or", "to", "of", "in", "status", "role", "node", "unit", "operative"}
    key_tokens_o = tokens_o - stop_tokens
    if key_tokens_o and key_tokens_o.issubset(tokens_p):
        return True
    return False


def run_all(selected_models: list[str] | None = None, host: str = "127.0.0.1", port: int = 18502) -> dict[str, Any]:
    with CASES_FILE.open("r", encoding="utf-8") as f:
        cases = {json.loads(line)["case_id"]: json.loads(line) for line in f if line.strip()}
    with PACKED_FILE.open("r", encoding="utf-8") as f:
        packed = [json.loads(line) for line in f if line.strip()]

    run_id = f"mn009-cross-model-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    summary = {"run_id": run_id, "models": {}}

    target_models = MODELS
    if selected_models:
        target_models = [m for m in MODELS if m["name"].lower() in [s.lower() for s in selected_models]]

    for m in target_models:

        m_name = m["name"]
        m_file = m["file"]
        print(f"\n=======================================================", flush=True)
        print(f"Evaluating Model: {m_name} ({m_file.name})", flush=True)
        print(f"=======================================================", flush=True)

        server_log_path = run_dir / f"{m_name}_server.log"
        server_log = server_log_path.open("w", encoding="utf-8")

        server_process = subprocess.Popen(
            [
                str(SERVER_BIN),
                "-m", str(m_file),
                "--host", host,
                "--port", str(port),
                "-ngl", "99",
                "-c", "2048",
                "-t", "8",
                "-b", "512",
                "-np", "1",
                "-fa", "on",
                "--temp", "0",
                "--seed", "42",
                "--jinja",
                "--no-webui",
                "--metrics",
            ],
            stdout=server_log,
            stderr=server_log,
        )

        try:
            if not wait_for_server(host, port, timeout_sec=60):
                server_log.flush()
                raise RuntimeError(f"Server failed to start for {m_name}. See log: {server_log_path}")
            print("Server is ready.", flush=True)


            m_stats = {"correct": 0, "total": len(packed), "latencies": [], "tokens": [], "by_domain": {}}
            m_records = []

            for idx, item in enumerate(packed, 1):
                cid = item["case_id"]
                cat = item["category"]
                oracle = cases[cid]["oracle_answer"]
                prompt = item["packed_prompt"]

                res = request_chat(prompt, max_tokens=64, host=host, port=port)
                passed = check_exact_or_contained(res["answer"], oracle)

                m_stats["correct"] += int(passed)
                dom = m_stats["by_domain"].setdefault(cat, [0, 0])
                dom[0] += int(passed)
                dom[1] += 1
                m_stats["latencies"].append(res["total_ms"])
                m_stats["tokens"].append(res["completion_tokens"])

                m_records.append({
                    "case_id": cid,
                    "category": cat,
                    "passed": passed,
                    "prediction": res["answer"],
                    "oracle": oracle,
                    "latency_ms": res["total_ms"],
                    "tokens": res["completion_tokens"],
                })

                print(f"[{m_name}] [{idx:02d}/30] {cid} ({cat:11s}): {'PASS' if passed else 'FAIL'} | {res['total_ms']:6.1f}ms | Ans: '{res['answer'][:35]}'", flush=True)

            summary["models"][m_name] = {
                "file": m_file.name,
                "accuracy": round(m_stats["correct"] / len(packed) * 100, 2),
                "correct_count": m_stats["correct"],
                "total_count": len(packed),
                "mean_latency_ms": round(sum(m_stats["latencies"]) / len(m_stats["latencies"]), 2),
                "mean_tokens": round(sum(m_stats["tokens"]) / len(m_stats["tokens"]), 2),
                "by_domain": {
                    dom: {"correct": v[0], "total": v[1], "accuracy": round(v[0] / v[1] * 100, 2)}
                    for dom, v in m_stats["by_domain"].items()
                },
            }

            with (run_dir / f"{m_name}_results.jsonl").open("w", encoding="utf-8") as f_out:
                for rec in m_records:
                    f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")

        finally:
            print(f"Terminating server for {m_name}...", flush=True)
            server_process.terminate()
            try:
                server_process.wait(15)
            except subprocess.TimeoutExpired:
                server_process.kill()
            server_log.close()
            time.sleep(1.0)


    summary_file = run_dir / "cross_model_summary.json"
    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n======================= FINAL CROSS-MODEL COMPARISON =======================", flush=True)
    for name, s in summary["models"].items():
        print(f"\nModel: {name} ({s['file']})", flush=True)
        print(f"  Overall Accuracy : {s['accuracy']}% ({s['correct_count']}/{s['total_count']})", flush=True)
        print(f"  Mean Latency     : {s['mean_latency_ms']} ms", flush=True)
        print(f"  Mean Tokens      : {s['mean_tokens']} tokens", flush=True)
        for dom, d in s["by_domain"].items():
            print(f"    - {dom:12s}: {d['accuracy']}% ({d['correct']}/{d['total']})", flush=True)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run cross-model benchmark comparison")
    parser.add_argument("--models", nargs="+", default=["Qwen3.5-2B", "Qwen3-4B"], help="Models to compare")
    parser.add_argument("--port", type=int, default=18502, help="llama-server port")
    args = parser.parse_args()
    run_all(selected_models=args.models, port=args.port)

