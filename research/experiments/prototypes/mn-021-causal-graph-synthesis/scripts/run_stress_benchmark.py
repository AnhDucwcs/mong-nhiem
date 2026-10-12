"""Stress Benchmark Execution Runner for Milestone MN-021 with Automated Zip Packaging.

Evaluates compound multi-shock scenarios across Track 1 (Simulator) and Track 2 (Real Model Inference)
for cross-model stress testing (Qwen3.5-2B, Qwen3-4B, Llama-3.2-3B).
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src and benchmarks to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "benchmarks"))

from corpus_v2_stress import generate_stress_benchmark_corpus
from orchestrator_federated import FederatedOrchestrator
from pack_evidence_zip import EvidenceZipPacker


def run_stress_benchmark_suite(
    track: int = 1,
    limit: int = 15,
    port: int = 18502,
    model_id: str = "Qwen3.5-2B-Q4_K_M",
    output_base: Optional[Path] = None,
) -> Path:
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    track_str = "track1-sim" if track == 1 else f"track2-{model_id}"
    run_id = f"mn021-stress-run-{timestamp}-{track_str}"

    base_dir = output_base or (Path(__file__).parent.parent / "runs")
    run_dir = base_dir / run_id
    audit_dir = run_dir / "audit_logs"
    audit_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Starting MN-021 High-Difficulty Stress Benchmark Suite ===")
    print(f"Run ID: {run_id} | Track: {track} | Model: {model_id} | Limit: {limit} cases")
    print(f"Audit log output: {audit_dir}\n")

    corpus = generate_stress_benchmark_corpus()[:limit]

    arms = [
        "arm1_flat",
        "arm2_reactive",
        "arm3_federated_synthesis",
    ]

    results_by_arm: Dict[str, Any] = {
        arm: {
            "successes": 0,
            "total": 0,
            "success_rate": 0.0,
            "committed_breaches": 0,
            "committed_races": 0,
            "temporal_evolutions": 0,
            "contested_anomalies": 0,
            "cross_inspections": 0,
            "reconciliation_acc": 0.0,
            "max_tokens": 0,
            "mean_tokens": 0.0,
            "compaction_ratio": 0.0,
            "mean_latency_ms": 0.0,
            "_token_accum": [],
            "_compaction_accum": [],
            "_latency_accum": [],
            "_rec_acc_accum": [],
        }
        for arm in arms
    }

    start_time = time.time()

    for idx, case in enumerate(corpus, 1):
        case_id = case["case_id"]
        domain = case["domain"]
        n_shocks = len(case["shock_config"].get("shocks", []))
        print(f"[{idx:02d}/{len(corpus):02d}] [COMPOUND-SHOCK: {n_shocks}] Evaluating {case_id} ({domain})...")

        for arm in arms:
            orch = FederatedOrchestrator(
                domain=domain,
                initial_entities=case["initial_entities"],
                subgoals_agent1=case["agent1_goals"],
                subgoals_agent2=case["agent2_goals"],
                arm=arm,
                port=port,
                model_id=model_id,
                track=track,
                shock_config=case["shock_config"],
            )
            res = orch.run_episode(case_id=case_id)

            # Record arm results
            arm_data = results_by_arm[arm]
            arm_data["total"] += 1
            if res["status"] == "PASS":
                arm_data["successes"] += 1
            arm_data["committed_breaches"] += res["committed_rule_breaches"]
            arm_data["committed_races"] += res["committed_race_violations"]
            arm_data["temporal_evolutions"] += res["temporal_evolutions_resolved"]
            arm_data["contested_anomalies"] += res["contested_anomalies_detected"]
            arm_data["cross_inspections"] += res["cross_inspections_performed"]
            arm_data["max_tokens"] = max(arm_data["max_tokens"], res["max_prompt_tokens"])
            arm_data["_token_accum"].append(res["mean_prompt_tokens"])
            arm_data["_compaction_accum"].append(res["autodream_compaction_ratio"])
            arm_data["_latency_accum"].append(res["mean_turn_latency_ms"])
            arm_data["_rec_acc_accum"].append(res["reconciliation_accuracy"])

            # Save individual audit trace
            log_file = audit_dir / f"{case_id}_{arm}_audit.json"
            log_file.write_text(json.dumps(res, indent=2), encoding="utf-8")

    duration = time.time() - start_time

    # Calculate final rates
    for arm in arms:
        data = results_by_arm[arm]
        data["success_rate"] = round((data["successes"] / max(data["total"], 1)) * 100.0, 1)
        data["mean_tokens"] = round(
            sum(data["_token_accum"]) / max(len(data["_token_accum"]), 1), 1
        )
        data["compaction_ratio"] = round(
            sum(data["_compaction_accum"]) / max(len(data["_compaction_accum"]), 1), 4
        )
        data["mean_latency_ms"] = round(
            sum(data["_latency_accum"]) / max(len(data["_latency_accum"]), 1), 2
        )
        data["reconciliation_acc"] = round(
            sum(data["_rec_acc_accum"]) / max(len(data["_rec_acc_accum"]), 1), 1
        )
        # Clean temporary accumulators
        del data["_token_accum"]
        del data["_compaction_accum"]
        del data["_latency_accum"]
        del data["_rec_acc_accum"]

    summary = {
        "run_id": run_id,
        "timestamp": timestamp,
        "track": track,
        "model_id": model_id if track == 2 else "simulator",
        "benchmark_type": "high_difficulty_compound_stress",
        "total_cases": len(corpus),
        "duration_seconds": round(duration, 2),
        "results": results_by_arm,
    }

    # Save run summary metadata
    summary_path = run_dir / "run_info.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n[INFO] Run summary saved to {summary_path}")

    # Display results table
    print("\n" + "=" * 80)
    print(f"STRESS BENCHMARK RESULTS: {run_id}")
    print("=" * 80)
    print(
        f"{'Arm':<28} | {'Success':<10} | {'Rate':<8} | {'Breaches':<8} | {'Races':<6} | {'MaxTok':<6} | {'Compaction':<10} | {'Latency':<9}"
    )
    print("-" * 80)
    for arm, d in results_by_arm.items():
        succ_str = f"{d['successes']}/{d['total']}"
        rate_str = f"{d['success_rate']}%"
        print(
            f"{arm:<28} | {succ_str:<10} | {rate_str:<8} | {d['committed_breaches']:<8} | {d['committed_races']:<6} | {d['max_tokens']:<6} | {d['compaction_ratio']:<10} | {d['mean_latency_ms']:<7}ms"
        )
    print("=" * 80)

    # Automated Zero-Bloat Packaging
    print(f"\n[PACKAGING] Compressing {len(corpus) * len(arms)} audit traces into audit_logs.zip...")
    archive_info = EvidenceZipPacker.pack_audit_logs(
        run_dir=run_dir,
        remove_loose_files=True,
    )

    print(f"[PACKAGING COMPLETE] SHA-256: {archive_info['sha256']}")
    print(f"[PACKAGING COMPLETE] Archived {archive_info['file_count']} files ({archive_info['compressed_bytes']:,} bytes).")
    print(f"[INFO] 100% loose JSON traces safely pruned from disk.")

    summary["audit_logs_archive_sha256"] = archive_info["sha256"]
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MN-021 High-Difficulty Stress Benchmark Suite.")
    parser.add_argument("--track", type=int, default=1, choices=[1, 2], help="1=Simulator, 2=Real Model Inference")
    parser.add_argument("--limit", type=int, default=15, help="Number of cases to evaluate (default: 15)")
    parser.add_argument("--port", type=int, default=18502, help="Llama-server HTTP port (default: 18502)")
    parser.add_argument("--model-id", type=str, default="Qwen3.5-2B-Q4_K_M", help="Model identifier string")
    args = parser.parse_args()

    run_stress_benchmark_suite(
        track=args.track,
        limit=args.limit,
        port=args.port,
        model_id=args.model_id,
    )
