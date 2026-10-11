"""Master Track 2 Benchmark Suite Runner for MN-019.

Sequentially executes real model inference (Track 2) across all 3 stages:
- Stage 1: Continuous Parametric Adaptation (drift-001)
- Stage 2: Dynamic Schema Evolution (drift-002)
- Stage 3: Proactive Causal Event Synthesis (drift-003)
Across 60 cases and 3 evaluation arms on Qwen3.5-2B via llama-server.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path


PROTOTYPE_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS_DIR = PROTOTYPE_ROOT / "experiments"

STAGES = [
    {
        "id": "drift-001",
        "name": "Stage 1: Continuous Parametric Adaptation",
        "dir": EXPERIMENTS_DIR / "drift-001-parametric-adaptation",
        "script": EXPERIMENTS_DIR / "drift-001-parametric-adaptation" / "scripts" / "run_benchmark.py",
    },
    {
        "id": "drift-002",
        "name": "Stage 2: Dynamic Schema Evolution",
        "dir": EXPERIMENTS_DIR / "drift-002-schema-evolution",
        "script": EXPERIMENTS_DIR / "drift-002-schema-evolution" / "scripts" / "run_benchmark.py",
    },
    {
        "id": "drift-003",
        "name": "Stage 3: Proactive Causal Event Synthesis",
        "dir": EXPERIMENTS_DIR / "drift-003-causal-event-synthesis",
        "script": EXPERIMENTS_DIR / "drift-003-causal-event-synthesis" / "scripts" / "run_benchmark.py",
    },
]


def check_server_health(port: int = 18502) -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def run_stage(stage_info: dict, limit: int, port: int) -> dict:
    stage_id = stage_info["id"]
    stage_name = stage_info["name"]
    script_path = stage_info["script"]

    print(f"\n========================================================")
    print(f"STARTING {stage_name} (Track 2, Limit={limit}, Port={port})")
    print(f"========================================================")

    cmd = [
        sys.executable,
        str(script_path),
        "--track", "2",
        "--limit", str(limit),
        "--port", str(port),
    ]

    t0 = time.perf_counter()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    output_lines = []
    if proc.stdout:
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            output_lines.append(line)

    proc.wait()
    duration = time.perf_counter() - t0

    # Locate latest run_dir in stage
    runs_dir = stage_info["dir"] / "runs"
    latest_run = None
    if runs_dir.exists():
        run_folders = [f for f in runs_dir.iterdir() if f.is_dir() and "track2" in f.name]
        if run_folders:
            latest_run = max(run_folders, key=lambda f: f.stat().st_mtime)

    run_info = {}
    if latest_run and (latest_run / "run_info.json").exists():
        with open(latest_run / "run_info.json", "r", encoding="utf-8") as f:
            run_info = json.load(f)

    return {
        "stage_id": stage_id,
        "stage_name": stage_name,
        "exit_code": proc.returncode,
        "duration_seconds": round(duration, 1),
        "run_dir": str(latest_run) if latest_run else None,
        "run_info": run_info,
    }


def main():
    parser = argparse.ArgumentParser(description="Run Full Track 2 Benchmark Suite")
    parser.add_argument("--limit", type=int, default=60, help="Number of cases per stage")
    parser.add_argument("--port", type=int, default=18502, help="llama-server port")
    args = parser.parse_args()

    print("Checking llama-server health on port", args.port)
    if not check_server_health(args.port):
        print(f"ERROR: llama-server is NOT responding on port {args.port}!")
        sys.exit(1)

    print("llama-server is healthy. Commencing Track 2 Benchmark Suite across all 3 stages...")

    suite_start = time.perf_counter()
    results = []

    for stage_info in STAGES:
        res = run_stage(stage_info, limit=args.limit, port=args.port)
        results.append(res)

    suite_duration = time.perf_counter() - suite_start

    print("\n" + "=" * 60)
    print("MASTER TRACK 2 BENCHMARK SUITE COMPLETED")
    print("=" * 60)
    print(f"Total Duration: {suite_duration / 60.0:.2f} minutes")

    for r in results:
        info = r.get("run_info", {})
        arms = info.get("arms_evaluated", {})
        print(f"\n--- {r['stage_name']} ---")
        print(f"Duration: {r['duration_seconds']}s | Exit Code: {r['exit_code']}")
        print(f"Run Dir: {r['run_dir']}")
        for arm_name, arm_data in arms.items():
            print(f"  {arm_name}: {arm_data.get('successes')}/{info.get('total_cases', '?')} ({arm_data.get('success_rate', '?')}%)")
        print(f"  Overall Verdict: {info.get('overall_verdict', 'UNKNOWN')}")

    summary_file = PROTOTYPE_ROOT / "track2_master_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "limit": args.limit,
            "port": args.port,
            "total_duration_minutes": round(suite_duration / 60.0, 2),
            "stages": results,
        }, f, indent=2)
    print(f"\nSummary saved to: {summary_file}")


if __name__ == "__main__":
    main()
