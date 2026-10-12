"""Benchmark Execution Runner for Milestone MN-021 with Automated Zip Packaging."""
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

from corpus_v1 import generate_benchmark_corpus
from orchestrator_federated import FederatedOrchestrator
from pack_evidence_zip import EvidenceZipPacker


def run_benchmark_suite(
    track: int = 1,
    limit: int = 80,
    port: int = 18502,
    model_id: str = "Qwen3.5-2B-Q4_K_M",
    output_base: Optional[Path] = None,
) -> Path:
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    track_str = "track1-sim" if track == 1 else f"track2-{model_id}"
    run_id = f"mn021-run-{timestamp}-{track_str}"

    base_dir = output_base or (Path(__file__).parent.parent / "runs")
    run_dir = base_dir / run_id
    audit_dir = run_dir / "audit_logs"
    audit_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Starting MN-021 Federated Causal Benchmark Suite ===")
    print(f"Run ID: {run_id} | Track: {track} | Limit: {limit} cases")
    print(f"Audit log output: {audit_dir}\n")

    corpus = generate_benchmark_corpus()[:limit]

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
        shock_flag = "[SHOCK]" if case["shock_config"].get("has_shock") else "[NOMINAL]"
        print(f"[{idx:02d}/{len(corpus):02d}] {shock_flag} Evaluating {case_id} ({domain})...")

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
        data["mean_tokens"] = round(sum(data["_token_accum"]) / max(len(data["_token_accum"]), 1), 1)
        data["compaction_ratio"] = round(sum(data["_compaction_accum"]) / max(len(data["_compaction_accum"]), 1), 4)
        data["mean_latency_ms"] = round(sum(data["_latency_accum"]) / max(len(data["_latency_accum"]), 1), 2)
        data["reconciliation_acc"] = round(sum(data["_rec_acc_accum"]) / max(len(data["_rec_acc_accum"]), 1), 1)
        del data["_token_accum"]
        del data["_compaction_accum"]
        del data["_latency_accum"]
        del data["_rec_acc_accum"]

    print(f"\nBenchmark completed in {duration:.1f}s.")
    print("=== SUMMARY METRICS ===")
    for arm, d in results_by_arm.items():
        print(f"[{arm}] Success: {d['successes']}/{d['total']} ({d['success_rate']}%) | Breaches: {d['committed_breaches']} | Max Tok: {d['max_tokens']} | Compaction: {d['compaction_ratio']*100:.1f}%")

    # -------------------------------------------------------------------------
    # AUTOMATED ZIP PACKAGING PROTOCOL
    # -------------------------------------------------------------------------
    print("\n[Audit Protocol] Packaging audit logs into audit_logs.zip...")
    zip_summary = EvidenceZipPacker.pack_audit_logs(run_dir=run_dir, remove_loose_files=True)
    print(f"Archive created: {zip_summary['archive_path']}")
    print(f"Files packed: {zip_summary['file_count']} | Raw: {zip_summary['raw_bytes']} B -> Compressed: {zip_summary['compressed_bytes']} B (Ratio: {zip_summary['compression_ratio']*100:.1f}%)")
    print(f"SHA-256 Fingerprint: {zip_summary['sha256']}")

    # Determine Verdict against Gate B
    arm3_rate = results_by_arm["arm3_federated_synthesis"]["success_rate"]
    arm2_rate = results_by_arm["arm2_reactive"]["success_rate"]
    delta_rate = arm3_rate - arm2_rate
    breaches = results_by_arm["arm3_federated_synthesis"]["committed_breaches"]
    max_tokens = results_by_arm["arm3_federated_synthesis"]["max_tokens"]
    compaction = results_by_arm["arm3_federated_synthesis"]["compaction_ratio"]
    rec_acc = results_by_arm["arm3_federated_synthesis"]["reconciliation_acc"]
    mean_lat = results_by_arm["arm3_federated_synthesis"]["mean_latency_ms"]

    m1_pass = arm3_rate >= 85.0
    m2_pass = delta_rate >= 40.0
    m3_pass = breaches == 0
    m4_pass = rec_acc >= 95.0
    m5_pass = max_tokens <= 512
    m6_pass = compaction >= 0.70
    m7_pass = mean_lat < 1000.0

    verdict = "PASS" if (m1_pass and m2_pass and m3_pass and m4_pass and m5_pass and m6_pass and m7_pass) else "FAIL"

    run_info = {
        "run_id": run_id,
        "milestone": "mn-021-causal-graph-synthesis",
        "track": track,
        "timestamp": timestamp,
        "total_cases": len(corpus),
        "model_id": model_id,
        "duration_seconds": round(duration, 2),
        "arms_evaluated": results_by_arm,
        "audit_logs_archive_sha256": zip_summary["sha256"],
        "gate_b_clauses": {
            "M1_resolution_rate": {"value": f"{arm3_rate}%", "bound": ">= 85.0%", "passed": m1_pass},
            "M2_superiority_delta": {"value": f"+{delta_rate:.1f}%", "bound": ">= +40.0%", "passed": m2_pass},
            "M3_committed_breaches": {"value": breaches, "bound": "== 0", "passed": m3_pass},
            "M4_reconciliation_acc": {"value": f"{rec_acc}%", "bound": ">= 95.0%", "passed": m4_pass},
            "M5_max_prompt_tokens": {"value": max_tokens, "bound": "<= 512", "passed": m5_pass},
            "M6_compaction_ratio": {"value": f"{compaction*100:.1f}%", "bound": ">= 70.0%", "passed": m6_pass},
            "M7_mean_latency_ms": {"value": f"{mean_lat} ms", "bound": "< 1000 ms", "passed": m7_pass},
        },
        "overall_verdict": verdict,
    }

    run_info_file = run_dir / "run_info.json"
    run_info_file.write_text(json.dumps(run_info, indent=2), encoding="utf-8")
    print(f"\nRun info written to: {run_info_file}")
    print(f"Overall Gate B Verdict: {verdict}\n")

    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MN-021 Federated Causal Benchmark Runner")
    parser.add_argument("--track", type=int, default=1, choices=[1, 2], help="Evaluation Track (1: Simulator, 2: LLM API)")
    parser.add_argument("--limit", type=int, default=80, help="Number of benchmark cases to evaluate")
    parser.add_argument("--port", type=int, default=18502, help="Local llama-server HTTP port")
    parser.add_argument("--model-id", type=str, default="Qwen3.5-2B-Q4_K_M", help="Model identifier string")

    args = parser.parse_args()
    run_benchmark_suite(
        track=args.track,
        limit=args.limit,
        port=args.port,
        model_id=args.model_id,
    )
