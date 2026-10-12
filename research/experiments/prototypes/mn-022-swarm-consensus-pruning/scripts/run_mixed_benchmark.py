"""Heterogeneous Cross-Model Swarm Benchmark Runner for MN-022."""
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


def run_mixed_benchmark(
    cases_limit: int = 80,
    server_port: int = 18502,
    is_mock: bool = False,
    min_latency: int = 0,
    max_latency: int = 5,
) -> Path:
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"mn022-mixed-run-{timestamp}-heterogeneous-swarm"

    base_dir = Path(__file__).resolve().parent.parent
    run_dir = base_dir / "runs" / run_id
    audit_dir = run_dir / "audit_logs"
    audit_dir.mkdir(parents=True, exist_ok=True)

    corpus = get_corpus()[:cases_limit]
    results: List[Dict[str, Any]] = []

    # Model assignment mapping across the 5 swarm agents
    model_map = {
        "agent_1": "Qwen3.5-2B-Q4_K_M",
        "agent_2": "Llama-3.2-3B-Instruct-Q4_K_M",
        "agent_3": "Qwen3.5-2B-Q4_K_M",
        "agent_4": "Llama-3.2-3B-Instruct-Q4_K_M",
        "agent_5": "Qwen3.5-2B-Q4_K_M",
    }
    port_map = {
        "agent_1": server_port,
        "agent_2": server_port + 1,
        "agent_3": server_port,
        "agent_4": server_port + 1,
        "agent_5": server_port,
    }

    print(f"=== Starting MN-022 Heterogeneous Swarm Benchmark: {run_id} ===")
    print(f"Swarm Model Distribution: {model_map}")
    print(f"Port Distribution: {port_map}")
    print(f"Scenarios: {len(corpus)}, Latency Envelope: [{min_latency}, {max_latency}] ticks")

    for idx, scenario in enumerate(corpus, 1):
        workers = {
            aid: AgentWorker(
                agent_id=aid,
                assigned_goal=scenario.agent_goals.get(aid, ""),
                is_mock=is_mock,
                server_port=port_map[aid],
                model_name=model_map[aid],
            )
            for aid in [f"agent_{i+1}" for i in range(scenario.num_agents)]
        }

        orchestrator = SwarmOrchestrator(
            scenario=scenario,
            arm="arm3",
            min_latency=min_latency,
            max_latency=max_latency,
            workers=workers,
            seed=200 + idx,
        )

        res = orchestrator.run_episode()
        results.append(res)

        audit_file = audit_dir / f"episode_arm3_{scenario.scenario_id}.json"
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)

        if idx % 20 == 0 or idx == len(corpus):
            succ = sum(1 for r in results if r["success"])
            print(f"  [{idx}/{len(corpus)}] Mixed ARM3 Success: {succ}/{idx} ({succ/idx*100:.1f}%)")

    total = len(results)
    successes = sum(1 for r in results if r["success"])
    breaches = sum(r["physical_breaches"] for r in results)
    races = sum(r["race_collisions"] for r in results)
    max_tok = max((r["max_tokens"] for r in results), default=0)
    mean_tok = round(sum(r["mean_tokens"] for r in results) / total, 1) if total else 0
    mean_lat = round(sum(r["mean_latency_ms"] for r in results) / total, 2) if total else 0
    mean_comp = round(sum(r["compaction_ratio"] for r in results) / total, 4) if total else 0.0

    summary = {
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
        "track": "Heterogeneous Mixed Swarm",
        "model_distribution": model_map,
        "total_cases": len(corpus),
        "swarm_size": 5,
        "latency_bounds": [min_latency, max_latency],
        "arms": {"arm3": summary},
        "created_at": timestamp,
    }

    with open(run_dir / "run_info.json", "w", encoding="utf-8") as f:
        json.dump(run_info, f, indent=2)

    zip_sha = pack_audit_logs(run_dir)
    print(f"\nAudit logs packed into audit_logs.zip (SHA-256: {zip_sha})")
    print(f"Summary saved to {run_dir / 'run_info.json'}")

    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MN-022 Mixed Swarm Benchmark")
    parser.add_argument("--cases", type=int, default=80)
    parser.add_argument("--port", type=int, default=18502)
    parser.add_argument("--mock", action="store_true", help="Run with simulator policies")
    parser.add_argument("--min-latency", type=int, default=0)
    parser.add_argument("--max-latency", type=int, default=5)
    args = parser.parse_args()

    run_mixed_benchmark(
        cases_limit=args.cases,
        server_port=args.port,
        is_mock=args.mock,
        min_latency=args.min_latency,
        max_latency=args.max_latency,
    )
