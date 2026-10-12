"""Benchmark Runner executing Track 1 and Track 2 evaluations across N = 80 swarm cases."""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from benchmarks.corpus_v1_swarm import get_corpus
from src.agent_worker import AgentWorker
from src.orchestrator_swarm import SwarmOrchestrator
from src.pack_evidence_zip import pack_audit_logs


def run_benchmark(
    track: int = 1,
    cases_limit: int = 80,
    server_port: int = 18502,
    model_name: str = "Qwen3.5-2B-Q4_K_M",
    min_latency: int = 0,
    max_latency: int = 5,
) -> Path:
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    track_name = f"track{track}-sim" if track == 1 else f"track{track}-{model_name}"
    run_id = f"mn022-run-{timestamp}-{track_name}"

    base_dir = Path(__file__).resolve().parent.parent
    run_dir = base_dir / "runs" / run_id
    audit_dir = run_dir / "audit_logs"
    audit_dir.mkdir(parents=True, exist_ok=True)

    corpus = get_corpus()[:cases_limit]
    arms = ["arm1", "arm2", "arm3"]
    arm_results: Dict[str, List[Dict[str, Any]]] = {a: [] for a in arms}

    is_mock = (track == 1)

    print(f"=== Starting MN-022 Benchmark: {run_id} ===")
    print(f"Track: {track} ({'Simulator' if is_mock else f'SLM on port {server_port}'})")
    print(f"Scenarios: {len(corpus)}, Latency Envelope: [{min_latency}, {max_latency}] ticks")

    for arm in arms:
        print(f"\n--- Executing {arm.upper()} ({len(corpus)} cases) ---")
        for idx, scenario in enumerate(corpus, 1):
            workers = {
                aid: AgentWorker(
                    agent_id=aid,
                    assigned_goal=scenario.agent_goals.get(aid, ""),
                    is_mock=is_mock,
                    server_port=server_port,
                    model_name=model_name,
                )
                for aid in [f"agent_{i+1}" for i in range(scenario.num_agents)]
            }

            orchestrator = SwarmOrchestrator(
                scenario=scenario,
                arm=arm,
                min_latency=min_latency,
                max_latency=max_latency,
                workers=workers,
                seed=42 + idx,
            )

            res = orchestrator.run_episode()
            arm_results[arm].append(res)

            # Save detailed audit log
            audit_file = audit_dir / f"episode_{arm}_{scenario.scenario_id}.json"
            with open(audit_file, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=2)

            if idx % 20 == 0 or idx == len(corpus):
                succ = sum(1 for r in arm_results[arm] if r["success"])
                print(f"  [{idx}/{len(corpus)}] {arm.upper()} Success: {succ}/{idx} ({succ/idx*100:.1f}%)")

    # Compute arm summaries
    arms_summary: Dict[str, Dict[str, Any]] = {}
    for arm in arms:
        results = arm_results[arm]
        total = len(results)
        successes = sum(1 for r in results if r["success"])
        breaches = sum(r["physical_breaches"] for r in results)
        races = sum(r["race_collisions"] for r in results)
        max_tok = max((r["max_tokens"] for r in results), default=0)
        mean_tok = round(sum(r["mean_tokens"] for r in results) / total, 1) if total else 0
        mean_lat = round(sum(r["mean_latency_ms"] for r in results) / total, 2) if total else 0
        mean_comp = round(sum(r["compaction_ratio"] for r in results) / total, 4) if total else 0.0

        arms_summary[arm] = {
            "success_count": successes,
            "total_count": total,
            "success_rate": round(successes / total * 100.0, 2),
            "physical_breaches": breaches,
            "race_collisions": races,
            "max_prompt_tokens": max_tok,
            "mean_prompt_tokens": mean_tok,
            "mean_latency_ms": mean_lat,
            "compaction_ratio": mean_comp,
        }

    run_info = {
        "run_id": run_id,
        "track": f"Track {track}",
        "model_name": model_name,
        "total_cases": len(corpus),
        "swarm_size": 5,
        "latency_bounds": [min_latency, max_latency],
        "arms": arms_summary,
        "created_at": timestamp,
    }

    # Save run_info.json
    with open(run_dir / "run_info.json", "w", encoding="utf-8") as f:
        json.dump(run_info, f, indent=2)

    # Pack audit logs into audit_logs.zip and remove loose JSON files
    zip_sha = pack_audit_logs(run_dir)
    print(f"\nAudit logs packed into audit_logs.zip (SHA-256: {zip_sha})")
    print(f"Summary saved to {run_dir / 'run_info.json'}")

    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MN-022 Swarm Benchmark")
    parser.add_argument("--track", type=int, default=1, choices=[1, 2])
    parser.add_argument("--cases", type=int, default=80)
    parser.add_argument("--port", type=int, default=18502)
    parser.add_argument("--model", type=str, default="Qwen3.5-2B-Q4_K_M")
    parser.add_argument("--min-latency", type=int, default=0)
    parser.add_argument("--max-latency", type=int, default=5)
    args = parser.parse_args()

    run_benchmark(
        track=args.track,
        cases_limit=args.cases,
        server_port=args.port,
        model_name=args.model,
        min_latency=args.min_latency,
        max_latency=args.max_latency,
    )
