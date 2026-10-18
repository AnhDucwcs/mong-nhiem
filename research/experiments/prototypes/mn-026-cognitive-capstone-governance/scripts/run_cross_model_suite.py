"""Master Cross-Model Benchmark Suite Runner for Post-MN-026 Generalization.

Sequentially executes real model inference (Track 2) across qualified secondary SLMs:
1. Llama-3.2-3B-Instruct (Llama-3.2-3B-Instruct-Q4_K_M.gguf)
2. Qwen3-4B (Qwen3-4B-Q4_K_M.gguf)
Across all N=120 scenarios and 3 experimental arms (360 episodes per model, 720 total episodes).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

# Prototype root
PROTOTYPE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROTOTYPE_ROOT))

from src.runner_track2 import run_track2_benchmark

LLAMA_SERVER_BIN = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe")
MODELS_DIR = Path(r"D:\Code\mong-nhiem\artifacts\models\mn-002")

MODELS = [
    {
        "name": "Llama-3.2-3B-Instruct",
        "tag": "llama3_2_3b",
        "family": "llama",
        "gguf": MODELS_DIR / "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
    },
    {
        "name": "Qwen3-4B",
        "tag": "qwen3_4b",
        "family": "qwen",
        "gguf": MODELS_DIR / "Qwen3-4B-Q4_K_M.gguf",
    },
]


def check_health(port: int = 18502) -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/health", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def kill_existing_server():
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "llama-server.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)
    except Exception:
        pass


def launch_server(gguf_path: Path, port: int = 18502) -> subprocess.Popen:
    kill_existing_server()
    cmd = [
        str(LLAMA_SERVER_BIN),
        "-m", str(gguf_path),
        "--port", str(port),
        "-c", "2048",
        "-ngl", "99",
        "--host", "127.0.0.1",
    ]
    print(f"\n[llama-server] Launching {gguf_path.name} on port {port}...")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(40):
        time.sleep(1)
        if check_health(port):
            print(f"[llama-server] Server ready and healthy on port {port}.")
            return proc
    proc.kill()
    raise RuntimeError(f"Server failed to initialize within 40 seconds for {gguf_path.name}")


def main():
    results: Dict[str, Any] = {}
    total_start = time.perf_counter()

    for m in MODELS:
        print(f"\n=======================================================")
        print(f"STARTING POST-MN-026 GENERALIZATION: {m['name']}")
        print(f"=======================================================")

        server_proc = launch_server(m["gguf"], port=18502)
        try:
            res = run_track2_benchmark(
                endpoint_url="http://127.0.0.1:18502",
                model_tag=m["tag"],
                model_family=m["family"],
            )
            results[m["tag"]] = res
        finally:
            print(f"\n[llama-server] Shutting down server for {m['name']}...")
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()
            kill_existing_server()
            time.sleep(2)
            print(f"[llama-server] Stopped. VRAM released.")

    total_duration = time.perf_counter() - total_start
    print(f"\n=======================================================")
    print(f"ALL CROSS-MODEL BENCHMARKS COMPLETED in {total_duration:.1f}s")
    print(f"=======================================================")
    for tag, res in results.items():
        print(f"Model [{tag}]: Verdict = {res['overall_verdict']} ({res['clauses_met']}/{res['total_clauses']} Clauses Met)")


if __name__ == "__main__":
    main()
