#!/usr/bin/env python3
"""Run deterministic pre-freeze two-hop/three-hop short-context probes."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

import ecc007

sys.path.insert(0, str(ecc007.ECC006))
import run_ecc006

OUT = ecc007.ROOT / "calibration" / "runs"
MODELS = {
    "llama-3.2-3b": ("Llama-3.2-3B-Instruct-Q4_K_M.gguf", {}),
    "qwen3-4b": ("Qwen3-4B-Q4_K_M.gguf", {"enable_thinking": False}),
}


def wait(process: subprocess.Popen[object], base_url: str) -> None:
    for _ in range(360):
        if process.poll() is not None:
            raise RuntimeError(f"llama-server exited: {process.returncode}")
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=1) as response:
                if response.status == 200:
                    return
        except (TimeoutError, urllib.error.URLError):
            time.sleep(.5)
    raise RuntimeError("llama-server startup timeout")


def build(client: ecc007.TokenRuntime, case: dict[str, object], target: int, seed: int) -> tuple[str, str, list[tuple[str, str]], int, float, int]:
    def count(edges: int) -> int:
        return client.count_prompt(ecc007.compose(case, edges, seed)[1])
    low, high = 0, 1
    while count(high) <= target:
        low, high = high, high * 2
    while low + 1 < high:
        middle = (low + high) // 2
        if count(middle) <= target:
            low = middle
        else:
            high = middle
    candidates = []
    for before in range(low + 1):
        context, content, prefix, edges = ecc007.compose(case, low, seed, before)
        actual = client.count_prompt(content)
        if actual <= target:
            ratio = client.count_text(prefix) / client.count_text(context)
            candidates.append((abs(ratio - .5), content, edges, actual, ratio, before))
    _distance, content, edges, actual, ratio, before = min(candidates, key=lambda item: item[0])
    return content, ecc007.relevant_graph(case), edges, actual, ratio, before


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=sorted(MODELS), required=True)
    args = parser.parse_args()
    model_name, template_kwargs = MODELS[args.model]
    model = run_ecc006.DEFAULT_MODELS / model_name
    server = run_ecc006.DEFAULT_SERVER
    if not model.is_file() or not server.is_file():
        raise RuntimeError(f"missing model/runtime dependency: model={model.is_file()} server={server.is_file()}")
    OUT.mkdir(parents=True, exist_ok=True)
    command = [
        str(server), "-m", str(model), "--host", "127.0.0.1", "--port", "18507", "-c", "16896", "-t", "12", "-b", "2048",
        "-np", "1", "-fa", "on", "--temp", "0", "--seed", "42", "--jinja", "--no-webui", "--no-cache-prompt",
        "--chat-template-kwargs", json.dumps(template_kwargs, separators=(",", ":")),
    ]
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results = []
    try:
        base_url = "http://127.0.0.1:18507"
        wait(process, base_url)
        client = ecc007.ServerClient(base_url, template_kwargs)
        for hop in (2, 3):
            for index in range(4):
                case = ecc007.graph(index + 1, hop, index < 2)
                content, relevant, distractors, actual, ratio, before = build(client, case, 512, 20260828)
                request, response = client.complete(content, {"temperature": 0.0, "seed": 42, "output_tokens": 16, "chat_template_kwargs": template_kwargs})
                raw = response["choices"][0]["message"].get("content") or ""
                passed, normalized = ecc007.evaluate(case, raw)
                results.append({
                    "model": args.model, "hop_count": hop, "case": case, "actual_input_tokens": actual,
                    "evidence_ratio": round(ratio, 6), "distractor_edges_before": before, "distractor_edges": distractors,
                    "relevant_graph": relevant, "request": request, "raw": raw, "normalized": normalized, "passed": passed,
                })
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(20)
            except subprocess.TimeoutExpired:
                process.kill()
    destination = OUT / f"{args.model}-results.json"
    destination.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for hop in (2, 3):
        rows = [row for row in results if row["hop_count"] == hop]
        print(f"{args.model} {hop}-hop: {sum(row['passed'] for row in rows)}/{len(rows)}")


if __name__ == "__main__":
    main()
