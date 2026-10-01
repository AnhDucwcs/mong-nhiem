#!/usr/bin/env python3
"""Evaluate currently running llama-server against MN-009 30-case benchmark."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PROTOTYPE_ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = PROTOTYPE_ROOT / "definition" / "corpus-v1" / "cases.jsonl"
PACKED_FILE = PROTOTYPE_ROOT / "runs" / "mn009-execution-run-0002-qwen35" / "packed_contexts.jsonl"
RUNS_DIR = PROTOTYPE_ROOT / "runs"


def request_chat(prompt: str, max_tokens: int = 64, host: str = "127.0.0.1", port: int = 18502) -> dict:
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
        headers={"Content-Type": "application/json", "User-Agent": "eval-runner"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    elapsed_ms = (time.perf_counter() - t0) * 1000

    choice = data["choices"][0]
    raw_content = choice["message"].get("content", "").strip()
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--port", type=int, default=18502)
    args = parser.parse_args()

    with CASES_FILE.open("r", encoding="utf-8") as f:
        cases = {json.loads(line)["case_id"]: json.loads(line) for line in f if line.strip()}
    with PACKED_FILE.open("r", encoding="utf-8") as f:
        packed = [json.loads(line) for line in f if line.strip()]

    print(f"Evaluating {args.model_name} on {len(packed)} cases...", flush=True)

    records = []
    stats = {"correct": 0, "total": len(packed), "latencies": [], "tokens": [], "by_domain": {}}

    for idx, item in enumerate(packed, 1):
        cid = item["case_id"]
        cat = item["category"]
        oracle = cases[cid]["oracle_answer"]
        prompt = item["packed_prompt"]

        res = request_chat(prompt, max_tokens=64, port=args.port)
        passed = check_exact_or_contained(res["answer"], oracle)

        stats["correct"] += int(passed)
        dom = stats["by_domain"].setdefault(cat, [0, 0])
        dom[0] += int(passed)
        dom[1] += 1
        stats["latencies"].append(res["total_ms"])
        stats["tokens"].append(res["completion_tokens"])

        records.append({
            "case_id": cid,
            "category": cat,
            "passed": passed,
            "prediction": res["answer"],
            "oracle": oracle,
            "latency_ms": res["total_ms"],
            "tokens": res["completion_tokens"],
        })
        print(f"[{args.model_name}] [{idx:02d}/30] {cid} ({cat:11s}): {'PASS' if passed else 'FAIL'} | {res['total_ms']:6.1f}ms | Ans: '{res['answer'][:35]}'", flush=True)

    summary = {
        "model": args.model_name,
        "accuracy": round(stats["correct"] / len(packed) * 100, 2),
        "correct_count": stats["correct"],
        "total_count": len(packed),
        "mean_latency_ms": round(sum(stats["latencies"]) / len(stats["latencies"]), 2),
        "mean_tokens": round(sum(stats["tokens"]) / len(stats["tokens"]), 2),
        "by_domain": {
            dom: {"correct": v[0], "total": v[1], "accuracy": round(v[0] / v[1] * 100, 2)}
            for dom, v in stats["by_domain"].items()
        },
    }

    out_file = RUNS_DIR / f"eval_{args.model_name.lower().replace('.', '_')}.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nSummary:", flush=True)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
