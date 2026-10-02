#!/usr/bin/env python3
"""Run 3-Way Comparative Benchmark on MN-009 Contexts:
1. Arm 1: Direct Single-Call (CoT OFF)
2. Arm 2: Monolithic In-Context CoT (CoT ON)
3. Arm 3: 2-Milestone Scaffolding Pipeline (M1 Decomposition + Host Circuit Breaker + M2 Synthesis)
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

REPO_ROOT = Path(__file__).resolve().parents[4]
PROTOTYPE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SERVER = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")
DEFAULT_MODEL = REPO_ROOT / "artifacts" / "models" / "mn-002" / "Qwen3.5-2B-Q4_K_M.gguf"
CASES_FILE = PROTOTYPE_ROOT / "definition" / "corpus-v1" / "cases.jsonl"
PACKED_FILE = PROTOTYPE_ROOT / "runs" / "mn009-execution-run-0002-qwen35" / "packed_contexts.jsonl"
RUNS_DIR = PROTOTYPE_ROOT / "runs"
REPORTS_DIR = PROTOTYPE_ROOT / "reports"


def check_health(host: str, port: int) -> bool:
    try:
        url = f"http://{host}:{port}/health"
        req = urllib.request.Request(url, headers={"User-Agent": "mn009-runner"})
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


def request_chat(
    prompt: str,
    enable_thinking: bool,
    max_tokens: int,
    host: str = "127.0.0.1",
    port: int = 18502,
    system_prompt: str | None = None,
) -> dict[str, Any]:
    url = f"http://{host}:{port}/v1/chat/completions"
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "messages": messages,
        "temperature": 0.0,
        "seed": 42,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": enable_thinking},
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "mn009-runner"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    elapsed_ms = (time.perf_counter() - t0) * 1000

    choice = data["choices"][0]
    raw_content = choice["message"].get("content", "")
    timings = data.get("timings", {})
    usage = data.get("usage", {})

    # Extract thinking tokens vs final output
    thought = ""
    answer = raw_content
    match = re.search(r"<think>(.*?)</think>", raw_content, flags=re.DOTALL)
    if match:
        thought = match.group(1).strip()
        answer = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
    elif "<think>" in raw_content:
        # Thinking was truncated before closing </think>!
        thought = raw_content.replace("<think>", "").strip()
        answer = ""  # Budget exhausted during thinking

    return {
        "raw": raw_content,
        "thought": thought,
        "answer": answer,
        "total_ms": round(elapsed_ms, 2),
        "prompt_ms": timings.get("prompt_ms", 0.0),
        "predicted_ms": timings.get("predicted_ms", 0.0),
        "prompt_tokens": usage.get("prompt_tokens", 0),
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
    # Check full containment
    if norm_o in norm_p or norm_p in norm_o:
        return True
    # Check significant tokens overlap (all core non-stop tokens of oracle in prediction)
    tokens_o = set(norm_o.split())
    tokens_p = set(norm_p.split())
    # remove common filler tokens
    stop_tokens = {"at", "is", "the", "a", "an", "and", "or", "to", "of", "in", "status", "role", "node", "unit", "operative"}
    key_tokens_o = tokens_o - stop_tokens
    if key_tokens_o and key_tokens_o.issubset(tokens_p):
        return True
    return False


def run_comparison(server_bin: Path, model_file: Path, host: str = "127.0.0.1", port: int = 18502) -> Path:
    # 1. Load benchmark corpus
    with CASES_FILE.open("r", encoding="utf-8") as f:
        cases = {json.loads(line)["case_id"]: json.loads(line) for line in f if line.strip()}
    with PACKED_FILE.open("r", encoding="utf-8") as f:
        packed = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(packed)} packed cases for 3-Way Comparative Benchmark.")

    # 2. Manage llama-server
    server_process = None
    if not check_health(host, port):
        print(f"Starting llama-server with {model_file.name} on port {port}...")
        cmd = [
            str(server_bin),
            "-m", str(model_file),
            "--host", host,
            "--port", str(port),
            "-c", "4096",
            "-t", "8",
            "-b", "512",
            "-np", "1",
            "-fa", "on",
            "--temp", "0",
            "--seed", "42",
            "--jinja",
            "--no-webui",
            "--metrics",
        ]
        server_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not wait_for_server(host, port, timeout_sec=60):
            if server_process:
                server_process.kill()
            raise RuntimeError("Failed to start llama-server within 60s")
        print("Server is healthy.")
    else:
        print("Using existing running llama-server.")

    run_id = f"mn009-comparison-run-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    records = []
    stats = {
        "Arm_1_Direct": {"correct": 0, "by_domain": {}, "latencies": [], "tokens": []},
        "Arm_2_Monolithic_CoT": {"correct": 0, "by_domain": {}, "latencies": [], "tokens": []},
        "Arm_3_Two_Milestone": {"correct": 0, "by_domain": {}, "latencies": [], "tokens": []},
    }

    try:
        total_cases = len(packed)
        for idx, item in enumerate(packed, 1):
            cid = item["case_id"]
            cat = item["category"]
            c_meta = cases[cid]
            oracle = c_meta["oracle_answer"]
            query = c_meta["query"]
            packed_prompt = item["packed_prompt"]

            print(f"\n[{idx}/{total_cases}] Evaluating {cid} ({cat})... Oracle: '{oracle}'", flush=True)

            # ----------------------------------------------------
            # Arm 1: Direct Single-Call (CoT OFF)
            # ----------------------------------------------------
            res_a1 = request_chat(packed_prompt, enable_thinking=False, max_tokens=64, host=host, port=port)
            pass_a1 = check_exact_or_contained(res_a1["answer"], oracle)
            stats["Arm_1_Direct"]["correct"] += int(pass_a1)
            stats["Arm_1_Direct"]["by_domain"].setdefault(cat, [0, 0])[0] += int(pass_a1)
            stats["Arm_1_Direct"]["by_domain"][cat][1] += 1
            stats["Arm_1_Direct"]["latencies"].append(res_a1["total_ms"])
            stats["Arm_1_Direct"]["tokens"].append(res_a1["completion_tokens"])
            print(f"  - Arm 1 (Direct):   {'PASS' if pass_a1 else 'FAIL'} | Ans: '{res_a1['answer'][:40]}' | {res_a1['total_ms']}ms", flush=True)

            # ----------------------------------------------------
            # Arm 2: Monolithic CoT (CoT ON)
            # ----------------------------------------------------
            res_a2 = request_chat(packed_prompt, enable_thinking=True, max_tokens=512, host=host, port=port)
            pass_a2 = check_exact_or_contained(res_a2["answer"], oracle)
            stats["Arm_2_Monolithic_CoT"]["correct"] += int(pass_a2)
            stats["Arm_2_Monolithic_CoT"]["by_domain"].setdefault(cat, [0, 0])[0] += int(pass_a2)
            stats["Arm_2_Monolithic_CoT"]["by_domain"][cat][1] += 1
            stats["Arm_2_Monolithic_CoT"]["latencies"].append(res_a2["total_ms"])
            stats["Arm_2_Monolithic_CoT"]["tokens"].append(res_a2["completion_tokens"])
            print(f"  - Arm 2 (Mono CoT): {'PASS' if pass_a2 else 'FAIL'} | Ans: '{res_a2['answer'][:40]}' | {res_a2['total_ms']}ms | Toks: {res_a2['completion_tokens']}", flush=True)

            # ----------------------------------------------------
            # Arm 3: 2-Milestone Scaffolding Pipeline
            # ----------------------------------------------------
            # Mốc 1: Phân rã & Trích xuất logic trung gian với CoT ngắn
            m1_prompt = f"{packed_prompt}\n\nTask: Trace and isolate the conclusive final state, entity properties, or function return value relevant to the query."
            res_m1 = request_chat(m1_prompt, enable_thinking=True, max_tokens=256, host=host, port=port)

            # Host Circuit Breaker & State Compaction:
            m1_text = res_m1["answer"] if res_m1["answer"] else res_m1["thought"]
            # Clean up into verified state card
            m2_prompt = (
                f"Verified State Card:\n{m1_text.strip()}\n\n"
                f"Query: {query}\n"
                "Return only the direct answer."
            )
            # Mốc 2: Tổng hợp trực tiếp không cần CoT
            res_m2 = request_chat(m2_prompt, enable_thinking=False, max_tokens=64, host=host, port=port)
            pass_a3 = check_exact_or_contained(res_m2["answer"], oracle)
            total_m3_ms = res_m1["total_ms"] + res_m2["total_ms"]
            total_m3_toks = res_m1["completion_tokens"] + res_m2["completion_tokens"]

            stats["Arm_3_Two_Milestone"]["correct"] += int(pass_a3)
            stats["Arm_3_Two_Milestone"]["by_domain"].setdefault(cat, [0, 0])[0] += int(pass_a3)
            stats["Arm_3_Two_Milestone"]["by_domain"][cat][1] += 1
            stats["Arm_3_Two_Milestone"]["latencies"].append(total_m3_ms)
            stats["Arm_3_Two_Milestone"]["tokens"].append(total_m3_toks)
            print(f"  - Arm 3 (2-Milestone): {'PASS' if pass_a3 else 'FAIL'} | Ans: '{res_m2['answer'][:40]}' | {total_m3_ms}ms | Toks: {total_m3_toks}", flush=True)

            records.append({
                "case_id": cid,
                "category": cat,
                "oracle_answer": oracle,
                "arm_1": {"passed": pass_a1, "answer": res_a1["answer"], "total_ms": res_a1["total_ms"], "tokens": res_a1["completion_tokens"]},
                "arm_2": {"passed": pass_a2, "answer": res_a2["answer"], "thought_len": len(res_a2["thought"]), "total_ms": res_a2["total_ms"], "tokens": res_a2["completion_tokens"]},
                "arm_3": {"passed": pass_a3, "m1_answer": res_m1["answer"], "m2_answer": res_m2["answer"], "total_ms": total_m3_ms, "tokens": total_m3_toks},
            })

    finally:
        if server_process and server_process.poll() is None:
            print("Shutting down local llama-server...")
            server_process.terminate()
            try:
                server_process.wait(15)
            except subprocess.TimeoutExpired:
                server_process.kill()

    # Save raw records
    records_file = run_dir / "results.jsonl"
    with records_file.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Generate summary
    summary = {
        "run_id": run_id,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": model_file.name,
        "total_cases": len(packed),
        "arms": {},
    }
    for arm_name, data in stats.items():
        summary["arms"][arm_name] = {
            "accuracy": round(data["correct"] / len(packed) * 100, 2),
            "correct_count": data["correct"],
            "total_count": len(packed),
            "mean_latency_ms": round(sum(data["latencies"]) / len(data["latencies"]), 2),
            "mean_tokens": round(sum(data["tokens"]) / len(data["tokens"]), 2),
            "by_domain": {
                dom: {"correct": vals[0], "total": vals[1], "accuracy": round(vals[0] / vals[1] * 100, 2)}
                for dom, vals in data["by_domain"].items()
            },
        }

    summary_file = run_dir / "summary.json"
    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n======================= FINAL BENCHMARK SUMMARY =======================")
    for arm_name, s in summary["arms"].items():
        print(f"\n>>> {arm_name.upper()} <<<")
        print(f"Overall Accuracy : {s['accuracy']}% ({s['correct_count']}/{s['total_count']})")
        print(f"Mean Latency     : {s['mean_latency_ms']} ms")
        print(f"Mean Tokens      : {s['mean_tokens']} tokens")
        for dom, d_data in s["by_domain"].items():
            print(f"  - {dom:14s}: {d_data['accuracy']}% ({d_data['correct']}/{d_data['total']})")

    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3-Way Comparative Benchmark on MN-009")
    parser.add_argument("--server", type=Path, default=DEFAULT_SERVER)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--port", type=int, default=18502)
    args = parser.parse_args()

    run_comparison(args.server, args.model, port=args.port)
