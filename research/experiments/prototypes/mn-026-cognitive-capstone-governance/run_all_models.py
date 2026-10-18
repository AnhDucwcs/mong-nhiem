"""Automated 3-model benchmark orchestrator for MN-026 Post-Run."""

import json
import os
import subprocess
import sys
import time
import urllib.request

# Ensure prototype root is in path
PROTOTYPE_DIR = os.path.dirname(os.path.abspath(__file__))
if PROTOTYPE_DIR not in sys.path:
    sys.path.insert(0, PROTOTYPE_DIR)

from src.runner_track2 import run_track2_benchmark

LLAMA_SERVER = r"D:\Materials\llama.cpp\build\bin\Release\llama-server.exe"
MODELS = [
    {
        "name": "qwen3_5_2b",
        "gguf": r"d:\Code\mong-nhiem\artifacts\models\mn-002\Qwen3.5-2B-Q4_K_M.gguf",
        "family": "qwen",
    },
    {
        "name": "llama3_2_3b",
        "gguf": r"d:\Code\mong-nhiem\artifacts\models\mn-002\Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "family": "llama",
    },
    {
        "name": "qwen3_4b",
        "gguf": r"d:\Code\mong-nhiem\artifacts\models\mn-002\Qwen3-4B-Q4_K_M.gguf",
        "family": "qwen",
    },
]


def kill_existing_servers():
    subprocess.run(["taskkill", "/F", "/IM", "llama-server.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)


def wait_for_server(url: str, timeout: float = 30.0):
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        try:
            req = urllib.request.Request(f"{url}/health")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Automated benchmark orchestrator for MN-026")
    parser.add_argument("--stage", type=int, default=None, help="Filter to specific stage e.g. 7")
    parser.add_argument("--model", type=str, default="all", choices=["all", "qwen3_5_2b", "llama3_2_3b", "qwen3_4b"], help="Model to run")
    args = parser.parse_args()

    results_summary = {}

    target_models = MODELS if args.model == "all" else [m for m in MODELS if m["name"] == args.model]

    for m in target_models:
        stage_desc = f"Stage {args.stage}" if args.stage is not None else "All Stages"
        print(f"\n=======================================================")
        print(f"Starting Benchmark for: {m['name']} ({m['family']}) [{stage_desc}]")
        print(f"GGUF: {m['gguf']}")
        print(f"=======================================================")
        kill_existing_servers()

        server_cmd = [
            LLAMA_SERVER,
            "-m", m["gguf"],
            "-c", "1024",
            "-ngl", "99",
            "--port", "18502",
        ]
        proc = subprocess.Popen(server_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Waiting for llama-server to initialize...")
        ready = wait_for_server("http://127.0.0.1:18502", timeout=45.0)
        if not ready:
            print(f"ERROR: Server failed to start for {m['name']}")
            proc.kill()
            continue

        print(f"Server is healthy. Executing Track 2 benchmark (Stage: {args.stage})...")
        start_bench = time.perf_counter()
        try:
            res = run_track2_benchmark(
                endpoint_url="http://127.0.0.1:18502",
                model_tag=m["name"],
                model_family=m["family"],
                stage_filter=args.stage,
            )
            elapsed = time.perf_counter() - start_bench
            res["benchmark_elapsed_sec"] = elapsed
            results_summary[m["name"]] = res
        finally:
            print(f"Terminating server for {m['name']}...")
            proc.terminate()
            try:
                proc.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                proc.kill()
            kill_existing_servers()
            time.sleep(2.0)

    print("\n\n=======================================================")
    print(f"BENCHMARK COMPLETED (Stage: {args.stage}). FINAL DISPOSITION:")
    print("=======================================================")
    for m_name, res in results_summary.items():
        print(f"\nModel: {m_name}")
        print(f"  Overall Verdict: {res['overall_verdict']}")
        print(f"  Clauses Met: {res['clauses_met']}/{res['total_clauses']}")
        for cid, c in res["clauses"].items():
            status = "PASS" if c["pass"] else "FAIL"
            print(f"    {cid}: {c['desc']} = {c['value']} ({c['target']}) -> {status}")

    # Write summary master file
    suffix = f"_stage{args.stage}" if args.stage is not None else ""
    master_summary_path = os.path.join(PROTOTYPE_DIR, "runs", f"post_patch_{args.model}{suffix}_summary.json")
    with open(master_summary_path, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)
    print(f"\nMaster summary written to: {master_summary_path}")


if __name__ == "__main__":
    main()
